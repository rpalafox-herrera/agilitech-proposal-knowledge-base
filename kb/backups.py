"""Consistent, portable snapshots of SQLite plus every original. No remote service."""
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED, BadZipFile
import hashlib
import json
import os
import re
import sqlite3

from .errors import KBError

MAX_BACKUP_BYTES = 200 * 1024 * 1024


def create_backup(kb):
    """Block app mutations while SQLite's backup API and originals are captured."""
    buffer = BytesIO()
    with kb.connect() as lock:
        lock.execute('BEGIN IMMEDIATE')
        records = lock.execute('SELECT file_location,sha256,file_size FROM documents ORDER BY id').fetchall()
        if sum(row['file_size'] for row in records) + kb.db_path.stat().st_size > MAX_BACKUP_BYTES:
            raise KBError('Browser backups are limited to 200 MB. Stop the app and copy the complete data folder for larger local archives.')
        with TemporaryDirectory() as temp:
            snapshot = Path(temp) / 'knowledge_base.db'
            with sqlite3.connect(kb.db_path) as source, sqlite3.connect(snapshot) as destination:
                source.backup(destination)
            with ZipFile(buffer, 'w', ZIP_DEFLATED) as archive:
                archive.write(snapshot, 'knowledge_base.db')
                for row in records:
                    # The mutation lock protects paths while read_original handles the backend.
                    with kb.connect() as reader:
                        doc = reader.execute('SELECT id FROM documents WHERE file_location=?', (row['file_location'],)).fetchone()
                    original = kb.read_original(doc['id'])
                    if hashlib.sha256(original).hexdigest() != row['sha256']:
                        raise KBError('An original no longer matches its recorded checksum. Backup stopped; check storage.')
                    archive.writestr(row['file_location'], original)
                archive.writestr('manifest.json', json.dumps({
                    'version': 1, 'created_at': datetime.now(timezone.utc).isoformat(),
                    'documents': len(records), 'original_storage': kb.original_storage,
                    'restore_storage': 'Local',
                }, indent=2))
    return buffer.getvalue()


def restore_backup(archive_path, destination):
    """Restore trusted app backups to a NEW/empty local folder, never overwrite a library."""
    destination = Path(destination).resolve()
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise KBError('Restore requires a new or empty folder. Existing data was not changed.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with TemporaryDirectory(dir=destination.parent) as temp:
            staging = Path(temp) / 'restored'
            staging.mkdir()
            with ZipFile(archive_path) as archive:
                entries = archive.infolist()
                names = [i.filename for i in entries]
                if len(entries) > 20000 or sum(i.file_size for i in entries) > 1024**3:
                    raise KBError('Backup exceeds restore size limits.')
                if len(names) != len(set(names)):
                    raise KBError('Backup contains duplicate paths.')
                for item in entries:
                    name = item.filename
                    if name not in {'knowledge_base.db', 'manifest.json'} and not re.fullmatch(r'uploads/[0-9a-f]{32}\.(pdf|docx|txt)', name):
                        raise KBError('Backup contains an unsafe or unexpected path.')
                    target = staging / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(item) as source, target.open('xb') as output:
                        import shutil
                        shutil.copyfileobj(source, output)
            manifest = json.loads((staging / 'manifest.json').read_text())
            if manifest.get('version') != 1:
                raise KBError('Unsupported backup version.')
            with sqlite3.connect(staging / 'knowledge_base.db') as db:
                if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    raise KBError('The backup database failed its integrity check.')
                records = db.execute('SELECT file_location,sha256 FROM documents').fetchall()
                if len(records) != manifest['documents']:
                    raise KBError('Backup document count does not match its manifest.')
                for location, digest in records:
                    if not re.fullmatch(r'uploads/[0-9a-f]{32}\.(pdf|docx|txt)', location):
                        raise KBError('Backup database contains an unsafe file path.')
                    original = staging / location
                    if not original.is_file() or hashlib.sha256(original.read_bytes()).hexdigest() != digest:
                        raise KBError('A backup original is missing or has a mismatched checksum.')
                db.execute("INSERT INTO documents_fts(documents_fts,rank) VALUES ('integrity-check',1)")
                db.execute("INSERT INTO segments_fts(segments_fts,rank) VALUES ('integrity-check',1)")
            (staging / 'manifest.json').unlink()
            if destination.exists():
                destination.rmdir()
            os.replace(staging, destination)
    except KBError:
        raise
    except (BadZipFile, OSError, sqlite3.Error, ValueError, KeyError) as exc:
        raise KBError('Could not validate this backup. No existing library was changed.') from exc
    return len(records)
