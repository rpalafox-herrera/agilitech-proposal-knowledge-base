"""Application operations; parameterized SQL, immutable originals and local storage."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import sqlite3
from uuid import uuid4

from .errors import KBError, DuplicateDocument
from .extraction import extract, safe_filename

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FILTER_KEYS = ("industry", "proposal_year", "engineering_discipline", "project_type")
META_KEYS = ("title", "industry", "project_type", "engineering_discipline", "proposal_year", "client_name", "description")


def match_query(query):
    """Quote all tokens so user input is never SQL or raw FTS syntax.

    Plain words require every word; double quotes require a contiguous phrase.
    """
    query = str(query).strip()
    if len(query) > 500:
        raise KBError("Please limit search to 500 characters.")
    parts = re.findall(r'"([^"]+)"|(\S+)', query)
    tokens = [phrase or word for phrase, word in parts]
    tokens = [t for t in tokens if re.search(r"[^\W_]", t, re.UNICODE)]
    return " AND ".join('"' + t.replace('"', '""') + '"' for t in tokens)


def metadata_values(metadata, default_title):
    result = {}
    for key in META_KEYS:
        value = metadata.get(key)
        if key == "proposal_year":
            if value is None or str(value).strip() in {"", "Unknown"}:
                result[key] = None
            else:
                try:
                    year = int(str(value).strip())
                except (ValueError, TypeError):
                    raise KBError("Proposal year must be a whole year, or left blank.")
                if not 1900 <= year <= 2100:
                    raise KBError("Proposal year must be between 1900 and 2100, or unknown.")
                result[key] = year
        else:
            value = str(value or "").strip()
            limit = 10000 if key == "description" else 300
            if len(value) > limit:
                raise KBError(f"{key.replace('_', ' ').title()} exceeds {limit} characters.")
            default = default_title if key == "title" else ("Unknown" if key in FILTER_KEYS else "")
            result[key] = value or default
    return result


class KnowledgeBase:
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or os.environ.get("AGILITECH_DATA_DIR") or PROJECT_ROOT / "data").resolve()
        self.uploads = self.data_dir / "uploads"
        self.db_path = self.data_dir / "knowledge_base.db"
        try:
            self.uploads.mkdir(parents=True, exist_ok=True)
            with self.connect() as db:
                db.execute("PRAGMA journal_mode=WAL")
                db.executescript(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))
        except (OSError, sqlite3.Error) as exc:
            raise KBError("Cannot initialize local storage. Check write permissions and that Python's SQLite supports FTS5.") from exc

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db_path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def _file(self, location):
        candidate = (self.data_dir / location).resolve()
        if candidate.parent != self.uploads.resolve() or candidate.is_symlink():
            raise KBError("Unsafe stored file location. File access was blocked.")
        return candidate

    def upload(self, filename, data, metadata=None):
        filename = safe_filename(filename)
        values = metadata_values(metadata or {}, Path(filename).stem)
        digest = hashlib.sha256(data).hexdigest()
        with self.connect() as db:
            duplicate = db.execute("SELECT id FROM documents WHERE sha256=?", (digest,)).fetchone()
        if duplicate:
            raise DuplicateDocument(duplicate["id"])
        extracted = extract(filename, data)
        location = "uploads/" + uuid4().hex + Path(filename).suffix.lower()
        target = self._file(location)
        try:
            with self.connect() as db:
                # Serialize database/file mutation and recheck duplicates after extraction.
                db.execute("BEGIN IMMEDIATE")
                duplicate = db.execute("SELECT id FROM documents WHERE sha256=?", (digest,)).fetchone()
                if duplicate:
                    raise DuplicateDocument(duplicate["id"])
                with target.open("xb") as output:
                    output.write(data)
                columns = list(values) + ["original_filename", "uploaded_at", "file_location", "file_size", "sha256", "extracted_text", "extraction_warning"]
                args = list(values.values()) + [filename, datetime.now(timezone.utc).isoformat(timespec="seconds"), location, len(data), digest, extracted.text, extracted.warning]
                cursor = db.execute(f"INSERT INTO documents ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})", args)
                document_id = cursor.lastrowid
                db.executemany("INSERT INTO segments(document_id,sequence,location,text) VALUES(?,?,?,?)",
                               [(document_id, i, s["location"], s["text"]) for i, s in enumerate(extracted.segments)])
            return document_id
        except Exception as exc:
            target.unlink(missing_ok=True)
            if isinstance(exc, KBError):
                raise
            raise KBError("Upload could not be saved. Check available disk space and folder permissions.") from exc

    def get_document(self, document_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM documents WHERE id=?", (document_id,)).fetchone()
        return dict(row) if row else None

    def get_segments(self, document_id):
        with self.connect() as db:
            return [dict(r) for r in db.execute("SELECT location,text FROM segments WHERE document_id=? ORDER BY sequence", (document_id,))]

    def read_original(self, document_id):
        doc = self.get_document(document_id)
        if not doc:
            raise KBError("Document no longer exists.")
        try:
            return self._file(doc["file_location"]).read_bytes()
        except OSError as exc:
            raise KBError("The original file is missing or unreadable. Restore it from a local backup.") from exc

    def update_metadata(self, document_id, metadata):
        doc = self.get_document(document_id)
        if not doc:
            raise KBError("Document no longer exists.")
        values = metadata_values({**doc, **metadata}, doc["title"])
        with self.connect() as db:
            db.execute("UPDATE documents SET " + ",".join(f"{key}=?" for key in values) + " WHERE id=?", [*values.values(), document_id])

    def delete_document(self, document_id, confirmed=False):
        if not confirmed:
            raise KBError("Confirm deletion before removing a document and its original file.")
        target = staged = None
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                doc = db.execute("SELECT file_location FROM documents WHERE id=?", (document_id,)).fetchone()
                if not doc:
                    raise KBError("Document no longer exists.")
                target = self._file(doc["file_location"])
                if target.exists():
                    staged = target.with_suffix(target.suffix + ".deleting")
                    target.rename(staged)
                db.execute("DELETE FROM documents WHERE id=?", (document_id,))
        except Exception as exc:
            if staged and staged.exists():
                staged.rename(target)
            if isinstance(exc, KBError):
                raise
            raise KBError("Deletion failed; the record and file were retained.") from exc
        if staged:
            try:
                staged.unlink()
            except OSError as exc:
                raise KBError("The record was deleted, but its staged original could not be removed. "
                              f"Close other programs and remove {staged.name} from the uploads folder.") from exc

    def _filters(self, filters):
        clauses, args = [], []
        for key, value in (filters or {}).items():
            if key not in FILTER_KEYS:
                raise KBError("Unsupported filter.")
            if value is None or value == "":
                continue
            if key == "proposal_year" and value == "Unknown":
                clauses.append("d.proposal_year IS NULL")
            else:
                clauses.append(f"d.{key}=?")
                args.append(value)
        return (" AND " + " AND ".join(clauses)) if clauses else "", args

    def list_documents(self, filters=None, limit=200, offset=0):
        clause, args = self._filters(filters)
        with self.connect() as db:
            return [dict(r) for r in db.execute("SELECT d.* FROM documents d WHERE 1=1" + clause + " ORDER BY d.uploaded_at DESC,d.id DESC LIMIT ? OFFSET ?", [*args, limit, offset])]

    def count_documents(self, filters=None):
        clause, args = self._filters(filters)
        with self.connect() as db:
            return db.execute("SELECT count(*) FROM documents d WHERE 1=1" + clause, args).fetchone()[0]

    def search(self, query, filters=None, limit=20, offset=0):
        if not str(query).strip():
            return self.list_documents(filters, limit, offset)
        expression = match_query(query)
        if not expression:
            return []
        clause, args = self._filters(filters)
        with self.connect() as db:
            rows = db.execute("SELECT d.*, bm25(documents_fts,3.0,1.0,1.0) AS score, "
                              "snippet(documents_fts,2,'[',']',' ... ',40) AS excerpt "
                              "FROM documents_fts JOIN documents d ON d.id=documents_fts.rowid "
                              "WHERE documents_fts MATCH ?" + clause + " ORDER BY score,d.id DESC LIMIT ? OFFSET ?",
                              [expression, *args, limit, offset]).fetchall()
            results = []
            for row in rows:
                doc = dict(row)
                # One query per term allows locations even when terms span multiple pages.
                sources, seen = [], set()
                for part in re.findall(r'"(?:[^"]|"")+"', expression):
                    for source in db.execute("SELECT s.id,s.location,snippet(segments_fts,0,'[',']',' ... ',40) AS text "
                                             "FROM segments_fts JOIN segments s ON s.id=segments_fts.rowid "
                                             "WHERE segments_fts MATCH ? AND s.document_id=? ORDER BY rank LIMIT 3", (part, doc["id"])):
                        if source["id"] not in seen:
                            sources.append({"location": source["location"], "text": source["text"]})
                            seen.add(source["id"])
                doc["sources"] = sources[:5]
                results.append(doc)
            return results

    def count_search(self, query, filters=None):
        if not str(query).strip():
            return self.count_documents(filters)
        expression = match_query(query)
        if not expression:
            return 0
        clause, args = self._filters(filters)
        with self.connect() as db:
            return db.execute("SELECT count(*) FROM documents_fts JOIN documents d ON d.id=documents_fts.rowid WHERE documents_fts MATCH ?" + clause, [expression, *args]).fetchone()[0]

    def stats(self):
        with self.connect() as db:
            return {"documents": db.execute("SELECT count(*) FROM documents").fetchone()[0],
                    "industries": db.execute("SELECT count(DISTINCT industry) FROM documents WHERE industry<>'Unknown'").fetchone()[0]}

    def filter_options(self):
        with self.connect() as db:
            return {key: [r[0] if r[0] is not None else "Unknown" for r in db.execute(f"SELECT DISTINCT {key} FROM documents ORDER BY {key}")] for key in FILTER_KEYS}
