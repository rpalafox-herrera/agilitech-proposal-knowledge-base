"""Keep only the selected small fictional demo archive; never touches user uploads."""
from pathlib import Path

from kb.service import KnowledgeBase
from sample_content import ARCHIVE_SAMPLES


SAMPLE_DIR = Path(__file__).resolve().parent / "samples"
KEEP_FILENAMES = {sample["filename"] for sample in ARCHIVE_SAMPLES}


def prune_demo(kb):
    """Remove only generated `fictional_archive_` demo records outside the current set."""
    removed_records = 0
    for document in kb.list_documents(limit=10_000):
        name = document["original_filename"]
        if name.startswith("fictional_archive_") and name not in KEEP_FILENAMES:
            kb.delete_document(document["id"], confirmed=True)
            removed_records += 1

    removed_sample_files = 0
    for path in SAMPLE_DIR.glob("fictional_archive_*.txt"):
        if path.name not in KEEP_FILENAMES:
            path.unlink()
            removed_sample_files += 1
    return {"records_removed": removed_records, "sample_files_removed": removed_sample_files}


if __name__ == "__main__":
    print(prune_demo(KnowledgeBase()))
