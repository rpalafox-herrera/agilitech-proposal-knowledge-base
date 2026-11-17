"""Add the bundled demo through the same validation/indexing path as uploads."""
from pathlib import Path

from kb.service import DuplicateDocument, KnowledgeBase
from sample_content import ARCHIVE_SAMPLES


def seed_demo(kb, samples=None):
    """Seed the full archive, or an explicitly supplied smaller teaching set."""
    samples = ARCHIVE_SAMPLES if samples is None else samples
    counts = {"added": 0, "skipped": 0}
    for index, sample in enumerate(samples):
        filename = str(Path(sample["filename"]).with_suffix(".pdf")) if index == 0 else sample["filename"]
        path = Path(__file__).resolve().parent / "samples" / filename
        try:
            kb.upload(filename, path.read_bytes(), sample)
            counts["added"] += 1
        except DuplicateDocument:
            counts["skipped"] += 1
    return counts


if __name__ == "__main__":
    result = seed_demo(KnowledgeBase())
    print(f"Fictional demo: {result['added']} added; {result['skipped']} already present.")
