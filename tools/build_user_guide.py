"""Build the maintained ChurchManager user guide PDF from its Markdown source."""

from __future__ import annotations

import re
import runpy
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
__version__ = runpy.run_path(ROOT / "churchmanager_version.py")["__version__"]
SOURCE = ROOT / "Documentation" / "ChurchManager.UserGuide.md"
OUTPUT = ROOT / "output" / "pdf" / "ChurchManager.UserGuide.pdf"


def _inline(text: str) -> str:
    """Convert the guide's small supported Markdown inline subset to markup."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def _styles():
    styles = getSampleStyleSheet()
    navy = colors.HexColor("#12395B")
    blue = colors.HexColor("#0B5A91")
    styles.add(ParagraphStyle(
        "GuideTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=25, leading=30, textColor=navy, alignment=TA_CENTER,
        spaceAfter=18,
    ))
    styles.add(ParagraphStyle(
        "GuideSubtitle", parent=styles["Normal"], fontSize=12, leading=17,
        textColor=blue, alignment=TA_CENTER, spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        "GuideH1", parent=styles["Heading1"], fontName="Helvetica-Bold",
        fontSize=17, leading=21, textColor=navy, spaceBefore=13, spaceAfter=7,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        "GuideH2", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=12, leading=15, textColor=blue, spaceBefore=9, spaceAfter=4,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        "GuideBody", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9.5, leading=13.5, textColor=colors.HexColor("#202830"),
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "GuideBullet", parent=styles["GuideBody"], leftIndent=16,
        firstLineIndent=-8, bulletIndent=4, spaceAfter=4,
    ))
    return styles


def _page(canvas, document):
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(colors.HexColor("#B8C7D3"))
    canvas.line(0.7 * inch, 0.58 * inch, width - 0.7 * inch, 0.58 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#526574"))
    canvas.drawString(0.7 * inch, 0.38 * inch, f"ChurchManager User Guide - {__version__}")
    canvas.drawRightString(width - 0.7 * inch, 0.38 * inch, f"Page {document.page}")
    canvas.restoreState()


def _story(markdown: str):
    styles = _styles()
    story = []
    paragraph = []
    first_heading = True

    def flush():
        if paragraph:
            story.append(Paragraph(_inline(" ".join(paragraph)), styles["GuideBody"]))
            paragraph.clear()

    for raw in markdown.splitlines():
        line = raw.strip()
        if line == "\\pagebreak":
            flush(); story.append(PageBreak()); continue
        if line == "---":
            flush(); story.append(Spacer(1, 8)); continue
        if not line:
            flush(); continue
        if line.startswith("# "):
            flush()
            style = styles["GuideTitle"] if first_heading else styles["GuideH1"]
            story.append(Paragraph(_inline(line[2:]), style))
            first_heading = False
        elif line.startswith("## "):
            flush(); story.append(Paragraph(_inline(line[3:]), styles["GuideH1"]))
        elif line.startswith("### "):
            flush(); story.append(Paragraph(_inline(line[4:]), styles["GuideH2"]))
        elif re.match(r"^\d+\. ", line):
            flush(); story.append(Paragraph(_inline(line), styles["GuideBullet"]))
        elif line.startswith("- "):
            flush(); story.append(Paragraph(_inline(line[2:]), styles["GuideBullet"], bulletText="-"))
        elif line.endswith("  "):
            paragraph.append(line[:-2])
        elif first_heading is False and len(story) == 1:
            flush(); story.append(Paragraph(_inline(line), styles["GuideSubtitle"]))
        else:
            paragraph.append(line)
    flush()
    return story


def build(source: Path = SOURCE, output: Path = OUTPUT) -> Path:
    """Build and return the final user-guide PDF path."""
    output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(output), pagesize=letter, rightMargin=0.72 * inch,
        leftMargin=0.72 * inch, topMargin=0.68 * inch, bottomMargin=0.72 * inch,
        title="ChurchManager User Guide", author="ChurchManager Project",
        subject="Task-oriented ChurchManager user instructions",
    )
    document.build(_story(source.read_text(encoding="utf-8")), onFirstPage=_page, onLaterPages=_page)
    return output


if __name__ == "__main__":
    print(build())
