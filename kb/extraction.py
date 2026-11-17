"""Extract text and honest source locations without uploading anything."""
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import re
from zipfile import ZipFile

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from pypdf import PdfReader

from .errors import KBError

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
MAX_TEXT_CHARS = 5_000_000
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@dataclass
class Extraction:
    segments: list[dict]
    warning: str = ""

    @property
    def text(self):
        return "\n\n".join(s["text"] for s in self.segments)


def safe_filename(filename):
    # Handle both slash conventions regardless of operating system.
    name = str(filename).replace("\\", "/").split("/")[-1]
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" .")
    if not name or name in {".", ".."}:
        raise KBError("Please choose a file with a valid filename.")
    suffix = Path(name).suffix.lower()
    return name[:180 - len(suffix)] + suffix if len(name) > 180 else name


def extract(filename, data):
    name = safe_filename(filename)
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise KBError("Unsupported file. Choose PDF, DOCX, or TXT (not legacy DOC).")
    if not data:
        raise KBError("The file is empty; nothing was saved.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise KBError("The file exceeds the 20 MB upload limit.")
    segments, warnings = [], []
    total_chars = 0

    def add(location, text):
        nonlocal total_chars
        cleaned = text.replace("\x00", "").strip()
        if cleaned:
            segments.append({"location": location, "text": cleaned})
            total_chars += len(cleaned)
        if total_chars > MAX_TEXT_CHARS:
            raise KBError("Extracted text exceeds the 5 million character safety limit.")

    try:
        if ext == ".pdf":
            reader = PdfReader(BytesIO(data))
            if reader.is_encrypted:
                raise KBError("Encrypted PDFs are not supported. Save an unencrypted copy first.")
            if len(reader.pages) > 1000:
                raise KBError("PDFs are limited to 1,000 pages per file.")
            empty = []
            for number, page in enumerate(reader.pages, 1):
                contents = page.get_contents()
                if contents and len(contents.get_data()) > 20 * 1024 * 1024:
                    raise KBError(f"PDF page {number} exceeds the extraction safety limit.")
                text = page.extract_text() or ""
                if not text.strip():
                    empty.append(str(number))
                add(f"Page {number}", text)
            if empty:
                warnings.append("No text on PDF pages " + ", ".join(empty[:30]) +
                                ". Scanned images require OCR, which this prototype does not include.")
        elif ext == ".docx":
            with ZipFile(BytesIO(data)) as archive:
                infos = archive.infolist()
                if len(infos) > 10000 or sum(i.file_size for i in infos) > 100 * 1024 * 1024:
                    raise KBError("DOCX contents exceed the decompression safety limit.")
            doc = Document(BytesIO(data))
            p, t = 0, 0
            for block in doc.iter_inner_content():
                if isinstance(block, Paragraph):
                    p += 1
                    add(f"Paragraph {p}", block.text)
                elif isinstance(block, Table):
                    t += 1
                    for r, row in enumerate(block.rows, 1):
                        add(f"Table {t}, row {r}", " | ".join(cell.text for cell in row.cells))
            warnings.append("DOCX locations refer to body paragraphs and table rows, not pages. "
                            "Headers, footers, text boxes, images and tracked changes may be omitted.")
        else:
            try:
                text = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                if data.startswith((b"\xff\xfe", b"\xfe\xff")):
                    text = data.decode("utf-16")
                else:
                    raise KBError("TXT must be saved as UTF-8 or UTF-16 with a byte-order mark.")
            if "\x00" in text or any(ord(c) < 32 and c not in "\n\r\t" for c in text):
                raise KBError("This TXT appears to contain binary data.")
            lines = text.splitlines()
            for start in range(0, len(lines), 25):
                add(f"Lines {start + 1}-{min(start + 25, len(lines))}", "\n".join(lines[start:start + 25]))
    except KBError:
        raise
    except Exception as exc:
        raise KBError("Could not read this document. It may be damaged or use an unsupported format; "
                      "nothing was saved. Try opening and re-saving the original.") from exc
    if not segments:
        raise KBError("No searchable text was found; nothing was saved. Image-only PDFs need OCR first.")
    return Extraction(segments, " ".join(warnings))
