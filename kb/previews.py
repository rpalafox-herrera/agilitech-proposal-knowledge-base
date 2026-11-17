"""Safe, local browser previews for uploaded Word and text documents."""

from io import BytesIO
from html import escape

from docx import Document
from docx.document import Document as DocxDocument
from docx.table import Table
from docx.text.paragraph import Paragraph


PREVIEW_CSS = """
<style>
.document-sheet{box-sizing:border-box;width:100%;max-width:900px;margin:0 auto;background:#fff;border:1px solid #dfe8e6;
border-radius:12px;padding:42px 54px;color:#1b3038;box-shadow:0 8px 28px rgba(18,43,54,.08);
font-family:Arial,sans-serif;line-height:1.58}.document-sheet h1{font-size:1.7rem;margin:0 0 1rem}
.document-sheet h2{font-size:1.4rem;margin:1.4rem 0 .7rem}.document-sheet h3{font-size:1.18rem;margin:1.2rem 0 .6rem}
.document-sheet p{margin:.45rem 0}.document-sheet .list{padding-left:1.3rem}.document-sheet .spacer{height:.7rem}
.document-sheet table{width:100%;border-collapse:collapse;margin:1rem 0}.document-sheet th,.document-sheet td{
border:1px solid #becdca;padding:8px 10px;vertical-align:top;text-align:left}.document-sheet tr:first-child td{
background:#edf4f2;font-weight:700}.document-sheet pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit;margin:0}
@media(max-width:700px){.document-sheet{padding:24px 20px}}
</style>
"""


def _blocks(parent):
    """Yield paragraphs and tables in their original document order."""
    if not isinstance(parent, DocxDocument):
        return
    for child in parent.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, parent)
        elif child.tag.endswith("}tbl"):
            yield Table(child, parent)


def _run_html(paragraph):
    output = []
    for run in paragraph.runs:
        text = escape(run.text).replace("\n", "<br>")
        if not text:
            continue
        if run.bold:
            text = f"<strong>{text}</strong>"
        if run.italic:
            text = f"<em>{text}</em>"
        if run.underline:
            text = f"<u>{text}</u>"
        output.append(text)
    return "".join(output) or escape(paragraph.text)


def docx_preview(data):
    """Return sanitized document-like HTML and an optional limitations note."""
    document = Document(BytesIO(data))
    body = []
    for block in _blocks(document):
        if isinstance(block, Paragraph):
            content = _run_html(block)
            if not content:
                body.append('<div class="spacer"></div>')
                continue
            style = (block.style.name if block.style else "").lower()
            if style.startswith("heading 1") or style == "title":
                body.append(f"<h1>{content}</h1>")
            elif style.startswith("heading 2"):
                body.append(f"<h2>{content}</h2>")
            elif style.startswith("heading"):
                body.append(f"<h3>{content}</h3>")
            elif "list" in style:
                marker = "1." if "number" in style else "•"
                body.append(f'<p class="list">{marker}&nbsp; {content}</p>')
            else:
                body.append(f"<p>{content}</p>")
        else:
            rows = []
            for row in block.rows:
                cells = "".join(
                    f"<td>{'<br>'.join(escape(paragraph.text) for paragraph in cell.paragraphs)}</td>"
                    for cell in row.cells
                )
                rows.append(f"<tr>{cells}</tr>")
            body.append("<table>" + "".join(rows) + "</table>")
    note = "Embedded Word images, headers, footers, and exact page layout may not appear in this browser preview." if document.inline_shapes else "Word page breaks, headers, and exact spacing may differ in the browser preview."
    return PREVIEW_CSS + '<article class="document-sheet">' + "".join(body) + "</article>", note


def text_preview(text):
    """Render plain text as a readable, safely escaped document sheet."""
    return PREVIEW_CSS + '<article class="document-sheet"><pre>' + escape(str(text)) + "</pre></article>"
