"""Rebuild bundled fictional samples. Optional: needs reportlab (dev requirements)."""
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from sample_content import ARCHIVE_SAMPLES

SAMPLE_DIR = Path(__file__).resolve().parent / "samples"


def sample_filename(index, sample):
    return str(Path(sample["filename"]).with_suffix(".pdf")) if index == 0 else sample["filename"]


def generate_samples():
    SAMPLE_DIR.mkdir(exist_ok=True)
    for index, sample in enumerate(ARCHIVE_SAMPLES):
        path = SAMPLE_DIR / sample_filename(index, sample)
        if path.suffix == ".txt":
            path.write_text(sample["text"], encoding="utf-8")
            continue
        # Preserve the existing, visually verified PDF byte-for-byte. Rebuilding
        # it would change its checksum and create an avoidable duplicate upload.
        if path.exists():
            continue
        styles = getSampleStyleSheet()
        styles["Title"].fontSize = 20
        styles["Title"].leading = 25
        styles["Title"].textColor = colors.HexColor("#193044")
        styles["Title"].alignment = TA_LEFT
        styles["BodyText"].fontSize = 11
        styles["BodyText"].leading = 16
        blocks = sample["text"].split("\n\n")
        story = [Paragraph(escape(blocks[0]), styles["Title"]), Spacer(1, 16)]
        for block in blocks[1:]:
            story.extend([Paragraph(escape(block).replace("\n", "<br/>"), styles["BodyText"]), Spacer(1, 12)])

        def footer(canvas, doc):
            canvas.setFont("Helvetica", 9)
            canvas.setFillColor(colors.HexColor("#516675"))
            canvas.drawString(54, 32, "Fictional university demo - all project details and figures invented")
            canvas.drawRightString(558, 32, f"Page {doc.page}")

        SimpleDocTemplate(str(path), pagesize=letter, rightMargin=54, leftMargin=54,
                          topMargin=46, bottomMargin=54, title=sample["title"],
                          author="Fictional university demo").build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Generated {len(ARCHIVE_SAMPLES)} fictional samples in {SAMPLE_DIR}")


if __name__ == "__main__":
    generate_samples()
