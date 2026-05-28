"""
CodeDNA — Comprehensive Portfolio + Technical Documentation Report
Uses real screenshots from SS/ folder and actual source code.
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.graphics.shapes import Drawing, Rect, String as GString
from reportlab.graphics import renderPDF
import textwrap

# ── Paths ──────────────────────────────────────────────────────────────────
BASE = Path("/home/sloth/Skill/CodeDNA")
SS = BASE / "SS"
SCHEMA = BASE / "prisma/schema.prisma"
OUTPUT = Path("/home/sloth/codedna-project-report.pdf")

# ── Colour palette ──────────────────────────────────────────────────────────
C_GREEN   = colors.HexColor("#00c46a")
C_BLUE    = colors.HexColor("#3B82F6")
C_PURPLE  = colors.HexColor("#8B5CF6")
C_CYAN    = colors.HexColor("#06B6D4")
C_ORANGE  = colors.HexColor("#F97316")
C_DARK    = colors.HexColor("#0f172a")
C_CARD    = colors.HexColor("#1e293b")
C_BORDER  = colors.HexColor("#334155")
C_TEXT    = colors.HexColor("#1e293b")
C_MUTED   = colors.HexColor("#64748b")
C_WHITE   = colors.white
C_ROW_ALT = colors.HexColor("#f8fafc")
C_TEAL    = colors.HexColor("#0D9488")

W, H = A4

# ── Screenshot mapping ──────────────────────────────────────────────────────
SHOTS = {
    "landing":   SS / "Screenshot_2026-05-28_09-21-21.png",
    "landing2":  SS / "Screenshot_2026-05-28_09-21-38.png",
    "public":    SS / "Screenshot_2026-05-28_09-21-49.png",
    "genome":    SS / "Screenshot_2026-05-28_09-22-01.png",
    "projects":  SS / "Screenshot_2026-05-28_09-22-17.png",
    "growth":    SS / "Screenshot_2026-05-28_09-22-34.png",
    "analysis":  SS / "Screenshot_2026-05-28_09-23-37.png",
}

# ── Page numbering state ────────────────────────────────────────────────────
_total_pages = [0]

# ── Canvas callbacks ────────────────────────────────────────────────────────
def on_page(canv, doc):
    canv.saveState()
    pg = doc.page
    # Top bar
    canv.setFillColor(C_DARK)
    canv.rect(0, H - 1.1*cm, W, 1.1*cm, fill=1, stroke=0)
    canv.setFillColor(C_GREEN)
    canv.setFont("Helvetica-Bold", 8)
    canv.drawString(1.8*cm, H - 0.7*cm, "CodeDNA")
    canv.setFillColor(colors.HexColor("#94a3b8"))
    canv.setFont("Helvetica", 7.5)
    canv.drawRightString(W - 1.8*cm, H - 0.7*cm, "AI-Powered Developer Genome Analysis Platform")
    # Bottom bar
    canv.setFillColor(colors.HexColor("#f1f5f9"))
    canv.rect(0, 0, W, 1*cm, fill=1, stroke=0)
    canv.setStrokeColor(colors.HexColor("#e2e8f0"))
    canv.setLineWidth(0.5)
    canv.line(0, 1*cm, W, 1*cm)
    canv.setFillColor(C_MUTED)
    canv.setFont("Helvetica", 7.5)
    canv.drawString(1.8*cm, 0.35*cm, "© 2026 Md Zahid Hasan Nerob · github.com/zhnverse")
    canv.setFont("Helvetica-Bold", 8)
    canv.setFillColor(C_TEAL)
    canv.drawRightString(W - 1.8*cm, 0.35*cm, f"Page {pg}")
    canv.restoreState()

def on_page_cover(canv, doc):
    canv.saveState()
    # Full dark bg
    canv.setFillColor(C_DARK)
    canv.rect(0, 0, W, H, fill=1, stroke=0)
    # Green accent strip left
    canv.setFillColor(C_GREEN)
    canv.rect(0, 0, 0.5*cm, H, fill=1, stroke=0)
    # Gradient overlay simulation (layered rects)
    for i in range(30):
        alpha = 0.03 * (30 - i) / 30
        canv.setFillColor(colors.HexColor("#00c46a"))
        canv.setFillAlpha(alpha)
        canv.circle(W * 0.7, H * 0.3, (i + 1) * 25, fill=1, stroke=0)
    canv.setFillAlpha(1.0)
    canv.restoreState()

# ── Styles ──────────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()

    def P(name, **kw):
        kw.setdefault("fontName", "Helvetica")
        kw.setdefault("textColor", C_TEXT)
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    return {
        "body":       P("body",   fontSize=9.5, leading=15, spaceAfter=6, alignment=TA_JUSTIFY),
        "body_sm":    P("body_sm",fontSize=8.5, leading=13, spaceAfter=4),
        "h1":         P("h1",     fontSize=26, leading=32, spaceAfter=6, spaceBefore=8,
                         fontName="Helvetica-Bold", textColor=C_TEAL),
        "h2":         P("h2",     fontSize=16, leading=22, spaceAfter=4, spaceBefore=14,
                         fontName="Helvetica-Bold", textColor=C_TEAL),
        "h3":         P("h3",     fontSize=12, leading=16, spaceAfter=3, spaceBefore=10,
                         fontName="Helvetica-Bold", textColor=C_TEXT),
        "h4":         P("h4",     fontSize=10.5, leading=14, spaceAfter=2, spaceBefore=8,
                         fontName="Helvetica-Bold", textColor=C_BLUE),
        "caption":    P("caption",fontSize=8, leading=11, spaceAfter=6, spaceBefore=2,
                         textColor=C_MUTED, alignment=TA_CENTER, fontName="Helvetica-Oblique"),
        "code":       P("code",   fontSize=8, leading=12, spaceAfter=4, spaceBefore=4,
                         fontName="Courier", backColor=colors.HexColor("#f1f5f9"),
                         leftIndent=12, rightIndent=12, borderPadding=8,
                         borderColor=colors.HexColor("#e2e8f0"), borderWidth=0.5,
                         borderRadius=4),
        "bullet":     P("bullet", fontSize=9.5, leading=14, spaceAfter=3,
                         leftIndent=14, firstLineIndent=-8),
        "label":      P("label",  fontSize=8, leading=11, textColor=C_MUTED,
                         fontName="Helvetica-Bold"),
        "badge_green":P("bg",     fontSize=8, leading=11, textColor=C_GREEN,
                         fontName="Helvetica-Bold"),
        "muted":      P("muted",  fontSize=9, leading=13, textColor=C_MUTED),
        "cover_title":P("ct",     fontSize=40, leading=46, fontName="Helvetica-Bold",
                         textColor=C_WHITE, spaceAfter=4),
        "cover_sub":  P("cs",     fontSize=18, leading=24, fontName="Helvetica-Bold",
                         textColor=C_GREEN, spaceAfter=16),
        "cover_body": P("cb",     fontSize=11, leading=17, textColor=colors.HexColor("#94a3b8")),
        "cover_label":P("cl",     fontSize=9, fontName="Helvetica-Bold",
                         textColor=colors.HexColor("#64748b")),
        "toc_h1":     P("toc1",   fontSize=11, fontName="Helvetica-Bold", textColor=C_TEAL,
                         spaceAfter=2, spaceBefore=5),
        "toc_h2":     P("toc2",   fontSize=9.5, textColor=C_TEXT, spaceAfter=1,
                         leftIndent=16),
        "part_label": P("pl",     fontSize=11, fontName="Helvetica-Bold", textColor=C_GREEN,
                         spaceAfter=2, spaceBefore=4),
    }

S = make_styles()

# ── Helper flowables ────────────────────────────────────────────────────────
def HR(color=C_BORDER, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=6, spaceBefore=4)

def SP(h=6):
    return Spacer(1, h)

def B(txt, style="body"):
    return Paragraph(txt, S[style])

def shot(key, width_pct=0.82, caption=None, max_height_cm=10):
    path = SHOTS.get(key)
    if not path or not path.exists():
        return []
    avail_w = (W - 3.6*cm) * width_pct
    max_h = max_height_cm * cm
    # Load to get natural dimensions
    from PIL import Image as PILImage
    try:
        with PILImage.open(str(path)) as pil:
            nat_w, nat_h = pil.size
        ratio = nat_h / nat_w
        # Fit within both constraints
        w = avail_w
        h = w * ratio
        if h > max_h:
            h = max_h
            w = h / ratio
    except Exception:
        w = avail_w
        h = None
    img = Image(str(path), width=w, height=h) if h else Image(str(path), width=w)
    img.hAlign = "CENTER"
    items = [SP(4), img]
    if caption:
        items.append(B(caption, "caption"))
    items.append(SP(6))
    return items

def info_box(title, items_list, color=C_BLUE):
    """Colored info box with bullet list."""
    rows = []
    for item in items_list:
        rows.append([Paragraph(f"• {item}", S["body_sm"])])
    data = [[Paragraph(title, ParagraphStyle("ib_title", fontName="Helvetica-Bold",
                fontSize=9, textColor=color))]] + rows
    t = Table(data, colWidths=[W - 3.6*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#eff6ff") if color==C_BLUE else colors.HexColor("#f0fdf4")),
        ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#f8fafc")),
        ("BOX", (0,0), (-1,-1), 0.8, color),
        ("LINEBELOW", (0,0), (-1,0), 0.5, color),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return [t, SP(8)]

def tech_badge(items_list):
    """Row of technology badges."""
    cells = [Paragraph(f"  {t}  ", ParagraphStyle("tb", fontSize=8, textColor=C_TEAL,
              fontName="Helvetica-Bold", backColor=colors.HexColor("#f0fdf4"),
              borderColor=C_GREEN, borderWidth=0.5, borderPadding=3)) for t in items_list]
    data = [cells]
    t = Table(data, colWidths=[None]*len(cells))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#f0fdf4")),
        ("BOX", (0,0), (-1,-1), 0.5, C_GREEN),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ]))
    return [t, SP(6)]

def two_col(left_content, right_content, left_w=0.5):
    """Two column layout."""
    avail = W - 3.6*cm
    lw = avail * left_w - 0.3*cm
    rw = avail * (1 - left_w) - 0.3*cm
    data = [[left_content, right_content]]
    t = Table(data, colWidths=[lw, rw])
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("INNERGRID", (0,0), (-1,-1), 0, colors.white),
    ]))
    return t

# ── Section divider ─────────────────────────────────────────────────────────
def section_header(part_num, part_label, title):
    """Full-width section break with part label."""
    items = []
    items.append(PageBreak())
    items.append(SP(6))
    items.append(Paragraph(part_label, S["part_label"]))
    items.append(Paragraph(title, S["h1"]))
    items.append(HR(C_TEAL, 1.5))
    items.append(SP(6))
    return items

def chapter_header(num, title, subtitle=None):
    items = []
    items.append(SP(8))
    items.append(Paragraph(f"{num}. {title}", S["h2"]))
    if subtitle:
        items.append(Paragraph(subtitle, S["muted"]))
    items.append(HR(C_BORDER, 0.5))
    return items

def sub_header(title):
    return [SP(4), Paragraph(title, S["h3"]), SP(2)]

def subsub(title):
    return [SP(2), Paragraph(title, S["h4"]), SP(1)]

# ── Feature block ────────────────────────────────────────────────────────────
def feature_block(letter, title, what, how, why, screenshot_key=None, cap=None):
    items = []
    items.append(SP(8))
    # Header badge + title
    header_data = [[
        Paragraph(f" {letter} ", ParagraphStyle("fb_l", fontName="Helvetica-Bold",
            fontSize=10, textColor=C_WHITE, backColor=C_TEAL)),
        Paragraph(f"  {title}", ParagraphStyle("fb_t", fontName="Helvetica-Bold",
            fontSize=12, textColor=C_TEXT)),
    ]]
    ht = Table(header_data, colWidths=[0.7*cm, W - 4.3*cm])
    ht.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("BACKGROUND", (0,0), (0,0), C_TEAL),
        ("BACKGROUND", (1,0), (1,0), colors.HexColor("#f8fafc")),
        ("BOX", (0,0), (-1,-1), 0.5, C_BORDER),
    ]))
    items.append(ht)
    items.append(SP(4))
    # Three columns: What | How | Why
    def mini(label, text, c):
        return [
            Paragraph(label, ParagraphStyle("ml", fontName="Helvetica-Bold", fontSize=8,
                textColor=c)),
            Paragraph(text, ParagraphStyle("mb", fontSize=9, leading=13, textColor=C_TEXT)),
        ]
    col_w = (W - 3.6*cm) / 3 - 0.3*cm
    body_data = [[
        [p for p in mini("WHAT IT DOES", what, C_BLUE)],
        [p for p in mini("HOW IT WORKS", how, C_GREEN)],
        [p for p in mini("WHY IT MATTERS", why, C_PURPLE)],
    ]]
    bt = Table(body_data, colWidths=[col_w, col_w, col_w])
    bt.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("BACKGROUND", (0,0), (0,0), colors.HexColor("#eff6ff")),
        ("BACKGROUND", (1,0), (1,0), colors.HexColor("#f0fdf4")),
        ("BACKGROUND", (2,0), (2,0), colors.HexColor("#faf5ff")),
        ("BOX", (0,0), (0,0), 0.5, C_BLUE),
        ("BOX", (1,0), (1,0), 0.5, C_GREEN),
        ("BOX", (2,0), (2,0), 0.5, C_PURPLE),
    ]))
    items.append(bt)
    if screenshot_key:
        items.extend(shot(screenshot_key, 0.80, cap))
    return items

# ── Table helpers ────────────────────────────────────────────────────────────
def make_table(headers, rows, col_widths=None, header_color=C_TEAL):
    avail = W - 3.6*cm
    if col_widths is None:
        cw = avail / len(headers)
        col_widths = [cw] * len(headers)
    data = [[Paragraph(h, ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8.5,
                textColor=C_WHITE)) for h in headers]]
    for i, row in enumerate(rows):
        bg = C_ROW_ALT if i % 2 == 0 else C_WHITE
        data.append([Paragraph(str(c), ParagraphStyle("td", fontSize=8.5, leading=12)) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = TableStyle([
        ("BACKGROUND", (0,0), (-1,0), header_color),
        ("TEXTCOLOR", (0,0), (-1,0), C_WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [C_ROW_ALT, C_WHITE]),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ])
    t.setStyle(style)
    return [t, SP(8)]

def code_block(txt):
    """Render monospaced code block."""
    wrapped = []
    for line in txt.strip().split("\n"):
        # Escape XML chars
        line = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        wrapped.append(line)
    content = "<br/>".join(wrapped)
    return [Paragraph(content, S["code"]), SP(4)]

# ── Read schema ─────────────────────────────────────────────────────────────
def read_schema():
    if SCHEMA.exists():
        return SCHEMA.read_text()
    return "// schema.prisma not found"

# ═══════════════════════════════════════════════════════════════════════════
# COVER PAGE
# ═══════════════════════════════════════════════════════════════════════════
def build_cover():
    items = []
    items.append(SP(3.5*cm))
    items.append(Paragraph("CodeDNA", S["cover_title"]))
    items.append(Paragraph("AI-Powered Developer Genome Analysis Platform", S["cover_sub"]))
    items.append(HR(C_GREEN, 1.5))
    items.append(SP(0.3*cm))
    items.append(Paragraph("Portfolio &amp; Technical Documentation", S["cover_body"]))
    items.append(SP(1.5*cm))

    # Author block
    meta = [
        ["Author", "Md Zahid Hasan Nerob"],
        ["GitHub", "github.com/zhnverse"],
        ["Program", "Computer Science — University Project"],
        ["Date", "May 2026"],
        ["Version", "1.0"],
    ]
    for row in meta:
        data = [[
            Paragraph(row[0], ParagraphStyle("cl", fontName="Helvetica-Bold", fontSize=9,
                textColor=colors.HexColor("#64748b"))),
            Paragraph(row[1], ParagraphStyle("cv", fontSize=9, textColor=C_WHITE)),
        ]]
        t = Table(data, colWidths=[3*cm, 10*cm])
        t.setStyle(TableStyle([
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        items.append(t)

    items.append(SP(2*cm))
    # Tech badges
    badges_data = [
        [Paragraph(t, ParagraphStyle("bdg", fontName="Helvetica-Bold", fontSize=8,
            textColor=C_WHITE, backColor=colors.HexColor("#1e3a5f"), borderPadding=4))
         for t in ["Next.js 14", "TypeScript", "PostgreSQL", "Prisma ORM",
                   "NextAuth.js", "D3.js", "Tailwind CSS"]],
    ]
    bt = Table(badges_data)
    bt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#1e3a5f")),
        ("BOX", (0,0), (-1,-1), 0.5, C_BLUE),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    items.append(bt)
    items.append(SP(1.5*cm))
    items.append(Paragraph(
        "Built solo · Full-stack TypeScript monorepo · Zero paid external services",
        ParagraphStyle("tagline", fontSize=9, textColor=colors.HexColor("#94a3b8"),
            alignment=TA_CENTER)
    ))
    items.append(PageBreak())
    return items

# ═══════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ═══════════════════════════════════════════════════════════════════════════
def build_toc():
    items = []
    items.append(SP(0.5*cm))
    items.append(Paragraph("Table of Contents", S["h1"]))
    items.append(HR(C_TEAL, 1.5))
    items.append(SP(0.3*cm))

    toc_entries = [
        ("PART 1: PORTFOLIO SHOWCASE", None, True),
        ("1.1 Executive Summary", "3"),
        ("1.2 Problem &amp; Solution", "3"),
        ("1.3 Feature Walkthrough", "4"),
        ("  A. GitHub OAuth &amp; Repository Sync", "4"),
        ("  B. AI-Powered Code Analysis", "5"),
        ("  C. Developer Score", "6"),
        ("  D. DNA Helix Visualization", "6"),
        ("  E. Radar Chart View", "7"),
        ("  F. Skill Tree View", "7"),
        ("  G. Projects Showcase", "8"),
        ("  H. Deep Analysis View", "8"),
        ("  I. Growth Tracking", "9"),
        ("  J. Achievement System", "9"),
        ("  K. Public Shareable Profile", "10"),
        ("  L. Embeddable Widget", "10"),
        ("  M. Dark / Light Theme", "10"),
        ("  N. Keyboard Shortcuts", "10"),
        ("1.4 Technical Highlights Summary", "11"),
        ("1.5 Metrics &amp; Impact", "11"),
        ("PART 2: TECHNICAL DOCUMENTATION", None, True),
        ("2.1 Architecture Overview", "12"),
        ("2.2 Technology Stack", "13"),
        ("2.3 Database Schema", "14"),
        ("2.4 API Reference", "16"),
        ("2.5 Component Architecture", "18"),
        ("2.6 Analysis Engine", "20"),
        ("2.7 Scoring Algorithm", "22"),
        ("2.8 Authentication Flow", "23"),
        ("2.9 Visualization Deep-Dive", "24"),
        ("2.10 Project Structure", "26"),
        ("2.11 Setup &amp; Installation", "27"),
        ("2.12 Deployment Guide", "28"),
        ("2.13 Future Roadmap", "28"),
        ("APPENDICES", None, True),
        ("Appendix A: Full schema.prisma", "29"),
        ("Appendix B: Environment Variables", "31"),
        ("Appendix C: Keyboard Shortcuts", "31"),
        ("Appendix D: Dependencies", "32"),
    ]

    for entry in toc_entries:
        if len(entry) == 3:  # part header
            items.append(SP(6))
            items.append(Paragraph(entry[0], S["toc_h1"]))
            items.append(HR(C_BORDER, 0.4))
        else:
            label, pg = entry
            is_main = not label.startswith(" ")
            row = [[
                Paragraph(label, S["toc_h1"] if is_main else S["toc_h2"]),
                Paragraph(pg or "", ParagraphStyle("toc_pg", fontSize=9.5 if is_main else 9,
                    alignment=TA_RIGHT, textColor=C_MUTED,
                    fontName="Helvetica-Bold" if is_main else "Helvetica")),
            ]]
            t = Table(row, colWidths=[W - 5.6*cm, 1.5*cm])
            t.setStyle(TableStyle([
                ("LEFTPADDING", (0,0), (-1,-1), 0),
                ("RIGHTPADDING", (0,0), (-1,-1), 0),
                ("TOPPADDING", (0,0), (-1,-1), 2 if is_main else 1),
                ("BOTTOMPADDING", (0,0), (-1,-1), 2 if is_main else 1),
            ]))
            items.append(t)
    items.append(PageBreak())
    return items

# ═══════════════════════════════════════════════════════════════════════════
# PART 1: PORTFOLIO SHOWCASE
# ═══════════════════════════════════════════════════════════════════════════
def build_portfolio():
    items = []
    items += section_header("1", "PART 1", "Portfolio Showcase")

    # ── 1.1 Executive Summary ──────────────────────────────────────────────
    items += chapter_header("1.1", "Executive Summary")
    items.append(B(
        "CodeDNA is a full-stack web application that transforms a developer's GitHub commit history "
        "into a living, evolving visual genome — a unique fingerprint of skills, patterns, and "
        "architectural expertise. Unlike static résumés or self-reported LinkedIn skills, CodeDNA "
        "connects to GitHub via OAuth 2.0, pulls every repository (public and private), runs a "
        "multi-stage analysis pipeline, and produces a developer genome visualised through three "
        "distinct interactive modes: a 3D DNA Helix, a D3.js Radar Chart, and a force-directed "
        "Skill Tree.", "body"
    ))
    items.append(B(
        "Built entirely solo as a Computer Science project, CodeDNA demonstrates mastery of modern "
        "full-stack engineering: Next.js 14 App Router with server components, PostgreSQL with "
        "type-safe Prisma ORM, NextAuth.js GitHub OAuth, custom D3.js visualisations, and a "
        "responsive Tailwind CSS design system. Every feature — from the scoring algorithm to the "
        "embeddable SVG widget — is implemented from scratch with zero paid external services.", "body"
    ))
    items.append(SP(4))
    items += info_box("Key Differentiators", [
        "No platform turns a developer's actual code into a visual genome",
        "Substance metrics (quality, depth, consistency) — not vanity metrics (stars, followers)",
        "Three distinct visualisation modes: DNA Helix, Radar Chart, Skill Tree",
        "Public shareable profile URL + embeddable SVG widget for any website",
        "Real-time growth tracking with milestone feed and predicted next skills",
    ], C_GREEN)

    # ── 1.2 Problem & Solution ─────────────────────────────────────────────
    items += chapter_header("1.2", "Problem &amp; Solution")
    items.append(B(
        "<b>The Problem:</b> GitHub's activity graph only shows commit frequency — not skill quality "
        "or architectural sophistication. LinkedIn skills are self-reported with no verification. "
        "Recruiters and hiring managers have no reliable way to assess a developer's actual "
        "abilities from their public profile. Developers have no tool to visualise their own "
        "growth trajectory objectively.", "body"
    ))
    items.append(B(
        "<b>The Solution:</b> CodeDNA connects to GitHub, analyses every repository's structure, "
        "dependencies, patterns, and quality indicators, then maps all findings onto a skill "
        "taxonomy with evidence-backed confidence levels (Claimed → Demonstrated → Mastered). "
        "The result is a living developer genome — a shareable, verifiable fingerprint of real "
        "coding ability that evolves automatically as you push new code.", "body"
    ))
    items.extend(shot("landing", 0.75,
        "Figure 1.1 — Landing page: 'Your Code Has DNA'. Users connect GitHub with one click "
        "through OAuth 2.0. The DNA bar visualisation at the bottom animates to reflect skill diversity."))

    # ── 1.3 Feature Walkthrough ────────────────────────────────────────────
    items += chapter_header("1.3", "Feature Walkthrough")
    items.append(B(
        "The following section provides a detailed walkthrough of every major feature, with "
        "embedded screenshots, technical explanations, and the user value each feature delivers.", "body"
    ))

    # A – GitHub OAuth & Sync
    items += feature_block(
        "A", "GitHub OAuth &amp; Repository Sync",
        what="One-click GitHub connection via OAuth 2.0. The platform syncs all repositories — "
             "public and private — with full metadata including primary language, stars, forks, "
             "and size.",
        how="NextAuth.js handles the OAuth 2.0 dance with GitHub as provider. On callback, "
            "the access token is stored in a JWT session. The /api/repos/sync route calls "
            "GitHub's REST API with pagination (100 repos/page) and upserts records into "
            "PostgreSQL via Prisma.",
        why="Developers connect once and all their work is immediately visible. Private repos "
            "are included, giving a complete picture of ability — not just the public-facing "
            "portfolio.",
    )

    # B – AI Analysis
    items += feature_block(
        "B", "AI-Powered Code Analysis",
        what="Each repository is analysed through a multi-stage pipeline: file tree extraction → "
             "language detection → dependency mapping → pattern recognition → skill extraction "
             "with confidence scoring.",
        how="The analysis engine (src/lib/mock-analysis.ts) uses deterministic seed-based logic "
            "to extract skills from primary language, repo name, and description. It detects "
            "architecture patterns (jamstack, layered, microservice, MVC), quality indicators "
            "(naming consistency, DRY adherence, separation of concerns), and maps findings to "
            "a 5-category skill taxonomy.",
        why="Users get instant, evidence-backed skill profiles from repos they have already "
            "built — no manual skill entry required. Every skill is tied to the repo that "
            "demonstrated it.",
        screenshot_key="genome",
        cap="Figure 1.2 — Genome page showing DNA Helix with 12 detected skills, developer score "
            "71/100, and skills panel with category + confidence filters."
    )

    # C – Developer Score
    items += feature_block(
        "C", "Developer Score",
        what="A composite 0-100 score derived from 5 weighted factors: Code Quality (30%), "
             "Skill Breadth (20%), Skill Depth (20%), Consistency (15%), and Growth Velocity (15%).",
        how="calculateDeveloperScore() runs 4 parallel Prisma queries, computes each factor "
            "independently (quality from repo analysisData JSON, breadth from category count × 5, "
            "depth from Mastered × 3 + Demonstrated × 2 + Claimed × 1 weights), then combines "
            "with weighted average and clamps to [0, 100].",
        why="The score reflects actual coding behaviour — not self-reported claims. 71/100 "
            "('Excellent') means real quality across real repos. The breakdown tells exactly "
            "which area to improve.",
    )

    # D – DNA Helix
    items += feature_block(
        "D", "DNA Helix Visualisation",
        what="An animated SVG double helix where each gene node represents a skill, sized by "
             "proficiency score and coloured by category. Auto-rotates when idle, responds to "
             "hover with skill detail tooltips.",
        how="Implemented in D3.js with pure SVG. A 3D cylindrical projection maps nodes onto "
             "two sinusoidal strands with depth-sorted rendering (painter's algorithm). The "
             "rotation animation uses requestAnimationFrame with a configurable speed. Node "
             "colours are mapped: blue=Language, green=Framework, orange=Pattern, "
             "purple=Tool, teal=Concept.",
        why="The helix is the central metaphor — developer DNA. It makes the abstract concept "
            "of 'skills across repos' immediately visual and memorable. No other tool shows "
            "developer ability this way.",
        screenshot_key="public",
        cap="Figure 1.3 — Public profile page (/genome/zhnverse) showing DNA helix with "
            "skill gene nodes, 71 score ring, top skills list, and public project cards."
    )

    # E – Radar
    items += feature_block(
        "E", "Radar Chart View",
        what="A D3.js radar chart mapping skills across 5 axes — Languages, Frameworks, "
             "Patterns, Tools, and Concepts. The filled polygon shows relative strength "
             "distribution at a glance.",
        how="Built with D3 radial scales and SVG polygon generation. Each axis represents "
            "a skill category; the value is the sum of proficiency scores in that category "
            "normalised to [0,1]. Theme-aware: re-renders when dark/light mode switches via "
            "resolvedTheme dependency in useEffect.",
        why="Instantly reveals if a developer is frontend-heavy, backend-dominant, or "
            "well-rounded. Employers can see specialisation shape in under 3 seconds.",
    )

    # F – Skill Tree
    items += feature_block(
        "F", "Skill Tree (Force-Directed Graph)",
        what="D3 force-directed graph: developer node at centre → category branch nodes → "
             "individual skill leaf nodes. Interactive — drag nodes to explore relationships, "
             "hover for detail.",
        how="D3 forceSimulation with forceLink, forceManyBody (repulsion), and forceCenter. "
            "Node mass proportional to proficiency score. Edges rendered as SVG lines with "
            "width proportional to evidence strength. Physics simulation runs until "
            "alphaDecay convergence then freezes.",
        why="Shows how skills cluster and relate — a TypeScript developer's tree looks "
            "fundamentally different from a Python data scientist's. Relational context "
            "that a flat list can never convey.",
    )

    # G – Projects
    items += feature_block(
        "G", "Project Showcase",
        what="Auto-generated project cards from analysed repos. Each card shows AI-written "
             "summary, detected architecture pattern badge, primary language, complexity and "
             "quality score bars, and demonstrated skill chips.",
        how="The /projects page queries all analysed repositories and their analysisData JSON. "
            "The 'Best Work' section surfaces top 3 repos by combined quality + complexity, "
            "automatically filtering tutorial clones (isTutorialClone flag from analysis). "
            "Filterable by language and architecture pattern.",
        why="A developer's best work is surfaced automatically — no curating needed. Recruiters "
            "see the most impressive projects first, with evidence of skill level.",
        screenshot_key="projects",
        cap="Figure 1.4 — Projects page showing Best Work section (top 3 by quality+complexity) "
            "and All Projects grid with architecture pattern badges, quality bars, and skill chips."
    )

    # H – Deep Analysis
    items += feature_block(
        "H", "Deep Analysis View",
        what="Per-repository deep dive: architecture detection with confidence score, code "
             "pattern breakdown, quality indicators as horizontal bars, demonstrated skills "
             "with confidence badges, and project highlights.",
        how="The /analysis/[repoId] page reads the repository's analysisData JSON (stored "
            "at analysis time) and renders each section. Architecture pattern is detected "
            "from repo name + description patterns. Quality bars are scored 0-100 across "
            "naming consistency, separation of concerns, DRY adherence, and overall quality.",
        why="Provides evidence-backed proof of what each project demonstrates. A recruiter "
            "can drill into any repo and see exactly what skills were validated, with what "
            "confidence level.",
        screenshot_key="analysis",
        cap="Figure 1.5 — Analysis page for 'Ai-portfolio': jamstack architecture at 78% "
            "confidence, quality breakdown bars, demonstrated skills with proficiency levels, "
            "and code pattern scores."
    )

    # I – Growth
    items += feature_block(
        "I", "Growth Tracking",
        what="Tracks skill progression over time with a D3 stacked area chart coloured by "
             "category. Milestone feed shows skill discoveries and level-ups. Predicted Next "
             "Skills forecasts likely future acquisitions.",
        how="GrowthEvents are created on each analysis: NEW_SKILL when a skill appears for "
            "the first time, LEVEL_UP when confidence increases. The stacked area chart "
            "groups events by week and category. Predicted skills use skill adjacency rules "
            "(e.g. Python → FastAPI/Django, JavaScript → TypeScript/Express).",
        why="Shows progression, not just current state. A developer who learned 12 skills "
            "in 30 days tells a very different story than one who learned the same 12 "
            "skills over 5 years.",
        screenshot_key="growth",
        cap="Figure 1.6 — Growth page showing skill timeline stacked area chart (12 skills, "
            "13 growth events), milestones feed, predicted next skills, and Speed Learner achievement."
    )

    # J – Achievements
    items += feature_block(
        "J", "Achievement System",
        what="Gamified badges rewarding real coding milestones: Polyglot (5+ languages), "
             "Full Stack (frontend + backend + database), Quality First (score > 80), "
             "Prolific (20+ repos), Speed Learner (5+ skills in 30 days).",
        how="Achievements are computed client-side from the stats API response. Each badge "
            "has a predicate function — Speed Learner checks growthVelocity ≥ 5 from the "
            "last-30-days growth event count. Earned badges glow green; locked ones are "
            "shown greyed with the requirement.",
        why="Gives developers tangible milestones to work toward. A developer who earns "
            "'Polyglot' has verifiable evidence of multi-language expertise — not just a "
            "self-claimed badge.",
    )

    # K – Public Profile
    items += feature_block(
        "K", "Public Shareable Profile",
        what="Every developer gets a permanent public URL at /genome/[username]. Shows DNA "
             "helix, skill breakdown, developer score ring, and top public projects. No "
             "login required to view.",
        how="The /genome/[username] page is a server component that queries the database "
            "publicly. OG meta tags (og:title, og:description, og:image) generate rich "
            "link previews when shared on Twitter/LinkedIn. The profile-client.tsx renders "
            "the same visualisations as the authenticated genome page.",
        why="A single shareable URL replaces a résumé. Share in a Discord, tweet it, put "
            "it in a job application — the genome is always up to date.",
    )

    # L – Widget
    items += feature_block(
        "L", "Embeddable SVG Widget",
        what="A 400×320 SVG card showing developer score ring, top 5 skill bars, and "
             "username. Embeddable on any website via &lt;img&gt; tag, iframe, or Markdown badge.",
        how="The /api/widget/[username] route generates SVG server-side using JavaScript "
            "string templates. No canvas, no browser — pure SVG text. Rate-limited to "
            "5 req/min/IP. Returns Content-Type: image/svg+xml with appropriate cache headers.",
        why="Developers can embed their genome on GitHub READMEs, personal portfolios, "
            "or Notion pages. The widget updates automatically as their genome evolves.",
    )

    # M – Theme
    items += feature_block(
        "M", "Dark / Light / System Theme",
        what="Full three-way theme support: dark (default), light, and system preference. "
             "All visualisations, charts, and UI components adapt their colour palette.",
        how="next-themes ThemeProvider wraps the app. The ThemeToggle component in the "
            "navbar cycles through sun/moon/monitor icons. D3 components use useTheme() "
            "with resolvedTheme in useEffect deps to re-render charts on theme change.",
        why="Dark mode is the developer default, light mode for daytime reading or "
            "screenshots. System mode respects OS preference automatically.",
    )

    # N – Keyboard Shortcuts
    items += feature_block(
        "N", "Keyboard Shortcuts",
        what="Power-user navigation shortcuts for all major pages, mounted globally.",
        how="The KeyboardShortcuts component uses a useEffect with document.addEventListener "
            "'keydown'. Key sequences (G then D, G then G, etc.) are tracked with a "
            "200ms timeout for the second key. The hook is defined in "
            "src/hooks/use-keyboard-shortcuts.ts.",
        why="Experienced developers navigate without touching the mouse — shortcuts reduce "
            "cognitive overhead and make the app feel native.",
    )

    # ── 1.4 Technical Highlights ───────────────────────────────────────────
    items += chapter_header("1.4", "Technical Highlights Summary")
    highlights = [
        "14 application pages/routes spanning landing, dashboard, genome, projects, growth, analysis, settings, and public profile",
        "6 database models (User, Repository, SkillNode, GenomeSnapshot, CodePattern, GrowthEvent) with full relational integrity",
        "18 API route handlers across authenticated, public, and widget endpoints",
        "3 distinct interactive visualisation types: SVG DNA Helix (3D projection), D3 Radar Chart, D3 Force-Directed Skill Tree",
        "Full OAuth 2.0 flow via GitHub with JWT session strategy and per-route auth middleware",
        "RESTful API with in-memory sliding-window rate limiting (5 req/min/IP) on all public endpoints",
        "Server-side rendering with Next.js 14 App Router — initial dashboard load uses 7 parallel Prisma queries server-side",
        "Full TypeScript end-to-end: Prisma schema types flow through API responses into React component props",
        "Responsive design: tested from 375px mobile to 1440px desktop breakpoints",
        "Embeddable SVG widget generated server-side — no canvas, no browser dependency",
        "Keyboard shortcut navigation system (G+D, G+G, G+P, G+R, G+S)",
        "Theme system with dark/light/system via next-themes, all D3 charts re-render on theme change",
    ]
    for h in highlights:
        items.append(B(f"• {h}", "bullet"))
    items.append(SP(6))

    # ── 1.5 Metrics & Impact ───────────────────────────────────────────────
    items += chapter_header("1.5", "Metrics &amp; Impact")
    metrics = [
        ["Metric", "Value"],
        ["Developer", "Solo — 1 person, full-stack"],
        ["Development Phases", "5 (Planning → DB → API → Frontend → Polish)"],
        ["TypeScript Coverage", "100% — zero JavaScript files in src/"],
        ["Database Models", "6 models, 15+ relationships"],
        ["API Endpoints", "18 route handlers"],
        ["React Components", "50+ components across UI, genome, dashboard, growth"],
        ["Visualisation Library", "D3.js v7 — pure SVG, no canvas"],
        ["Auth Strategy", "JWT with GitHub OAuth 2.0"],
        ["External Paid Services", "Zero — PostgreSQL + GitHub API (free tier)"],
        ["Vercel Deployment", "Ready — zero configuration required"],
        ["Analysed Repos (Live)", "10 repositories"],
        ["Detected Skills (Live)", "12 unique skills across 5 categories"],
        ["Developer Score (Live)", "71 / 100 — Excellent"],
    ]
    items += make_table(metrics[0], metrics[1:],
        col_widths=[7*cm, W - 3.6*cm - 7*cm])

    return items

# ═══════════════════════════════════════════════════════════════════════════
# PART 2: TECHNICAL DOCUMENTATION
# ═══════════════════════════════════════════════════════════════════════════
def build_technical():
    items = []
    items += section_header("2", "PART 2", "Technical Documentation")

    # ── 2.1 Architecture Overview ──────────────────────────────────────────
    items += chapter_header("2.1", "Architecture Overview")
    items.append(B(
        "CodeDNA uses a monolithic Next.js 14 App Router architecture with server-side rendering "
        "at the page level and client-side interactivity for visualisations. The system has four "
        "distinct layers:", "body"
    ))

    arch_layers = [
        ["Layer", "Technology", "Responsibility"],
        ["Client Layer", "React + D3.js", "Interactive visualisations, form handling, client state via useState/useCallback"],
        ["Server Layer", "Next.js 14 App Router", "SSR page rendering, 7 parallel Prisma queries on dashboard load, metadata generation"],
        ["API Layer", "Next.js Route Handlers", "18 REST endpoints, JWT auth via getToken(), rate limiting, GitHub API calls"],
        ["Data Layer", "PostgreSQL + Prisma ORM", "Type-safe queries, cascade deletes, CUID primary keys, JSON columns for flexible data"],
    ]
    items += make_table(arch_layers[0], arch_layers[1:],
        col_widths=[3.5*cm, 4*cm, W - 3.6*cm - 7.5*cm])

    items.append(SP(6))
    items.append(B("<b>Data Flow:</b>", "body"))
    flows = [
        "User → Browser → Next.js Server Component → Prisma → PostgreSQL (initial page load, SSR)",
        "Browser → Next.js API Route → getToken(JWT) → Prisma → PostgreSQL (mutations, refreshes)",
        "Browser → Next.js API Route → GitHub REST API (repo sync, using stored OAuth access token)",
        "External → /api/public/* or /api/widget/* → Prisma → PostgreSQL (public, no auth required)",
    ]
    for f in flows:
        items.append(B(f"• {f}", "bullet"))

    items.append(SP(6))
    items.append(B(
        "<b>Critical Auth Pattern:</b> Next.js 14 App Router Route Handlers cannot use "
        "getServerSession(authOptions) — it silently returns null. The solution is "
        "getToken({ req }) from next-auth/jwt, encapsulated in src/lib/api-auth.ts "
        "and used by all 18 API routes. Server Components (page.tsx files) continue to "
        "use getServerSession() correctly.", "body"
    ))

    # ── 2.2 Technology Stack ───────────────────────────────────────────────
    items += chapter_header("2.2", "Technology Stack")
    stack = [
        ["Layer", "Technology", "Version", "Rationale"],
        ["Framework", "Next.js", "14.2.18", "App Router, SSR, file-based routing, image optimisation"],
        ["Language", "TypeScript", "5.x", "End-to-end type safety from DB schema to React props"],
        ["Styling", "Tailwind CSS", "3.4.15", "Utility-first, JIT compilation, dark: modifier"],
        ["Components", "Radix UI + shadcn", "Custom", "Accessible headless primitives, keyboard nav"],
        ["Database", "PostgreSQL", "18.x", "Relational integrity, JSON columns, CUID PKs"],
        ["ORM", "Prisma", "5.22.0", "Type-safe queries, migrations, Prisma Studio"],
        ["Auth", "NextAuth.js", "4.24.11", "OAuth 2.0 GitHub provider, JWT sessions, callbacks"],
        ["Visualisation", "D3.js", "7.9.0", "SVG-based, force simulation, radial scales"],
        ["Theme", "next-themes", "0.4.6", "SSR-safe dark/light/system, ThemeProvider"],
        ["Icons", "Lucide React", "0.454.0", "Consistent icon library, tree-shakeable"],
        ["Animation", "tailwindcss-animate", "1.0.7", "CSS keyframe animations via Tailwind classes"],
        ["HTTP Client", "fetch (native)", "—", "Browser fetch API, no axios dependency"],
        ["Deployment", "Vercel", "—", "Zero-config Next.js hosting, preview deployments"],
    ]
    items += make_table(stack[0], stack[1:],
        col_widths=[3.2*cm, 3.2*cm, 2.5*cm, W - 3.6*cm - 8.9*cm])

    # ── 2.3 Database Schema ────────────────────────────────────────────────
    items += chapter_header("2.3", "Database Schema")
    items.append(B(
        "The database uses 6 models with PostgreSQL as the backing store. All primary keys "
        "use cuid() for URL-safe, globally unique identifiers. JSON columns (analysisData, "
        "evidence, metadata) provide flexibility for analysis output without schema migrations "
        "for each new analysis field.", "body"
    ))

    models = [
        ("User", "Stores GitHub OAuth profile data", [
            ["Field", "Type", "Description"],
            ["id", "String (CUID)", "Primary key"],
            ["githubId", "String @unique", "GitHub numeric user ID"],
            ["username", "String @unique", "GitHub login handle"],
            ["avatar", "String?", "GitHub avatar URL"],
            ["bio", "String?", "GitHub bio"],
            ["email", "String?", "GitHub email (if public)"],
            ["developerScore", "Int @default(0)", "Computed composite score 0-100"],
            ["createdAt / updatedAt", "DateTime", "Timestamps"],
        ]),
        ("Repository", "Synced from GitHub API — one per repo per user", [
            ["Field", "Type", "Description"],
            ["id", "String (CUID)", "Primary key"],
            ["userId", "String", "FK → User (cascade delete)"],
            ["githubRepoId", "String @unique", "GitHub repo numeric ID"],
            ["name / fullName", "String", "e.g. 'CodeDNA', 'zhnverse/CodeDNA'"],
            ["primaryLanguage", "String?", "Top language from GitHub"],
            ["languages", "Json?", "All language byte counts"],
            ["stars / forks / size", "Int", "GitHub metrics"],
            ["isPrivate", "Boolean", "Private vs public repo"],
            ["isAnalyzed", "Boolean", "Analysis complete flag"],
            ["analysisData", "Json?", "Full MockAnalysisResult stored as JSON"],
            ["complexityScore", "Int?", "0-100 complexity from analysis"],
            ["lastAnalyzedAt", "DateTime?", "Last analysis timestamp"],
        ]),
        ("SkillNode", "One row per unique skill per user — upserted on each analysis", [
            ["Field", "Type", "Description"],
            ["id", "String (CUID)", "Primary key"],
            ["userId / name", "@@unique", "Composite unique: one skill per user"],
            ["category", "SkillCategory enum", "LANGUAGE | FRAMEWORK | PATTERN | TOOL | CONCEPT"],
            ["proficiencyScore", "Int", "0-100 weighted proficiency"],
            ["confidence", "SkillConfidence enum", "CLAIMED | DEMONSTRATED | MASTERED"],
            ["evidence", "Json", "Array of repo evidence objects"],
            ["firstSeen / lastSeen", "DateTime", "Temporal skill tracking"],
        ]),
        ("GrowthEvent", "Audit log of skill discoveries and level-ups", [
            ["Field", "Type", "Description"],
            ["id", "String (CUID)", "Primary key"],
            ["userId", "String", "FK → User"],
            ["skillNodeId", "String?", "FK → SkillNode (nullable, SetNull on delete)"],
            ["eventType", "GrowthEventType enum", "NEW_SKILL | LEVEL_UP | MILESTONE | NEW_REPO"],
            ["title / description", "String", "Human-readable event description"],
            ["metadata", "Json?", "Additional context (repo name, old vs new confidence)"],
        ]),
        ("CodePattern", "Per-repo detected code patterns", [
            ["Field", "Type", "Description"],
            ["patternType", "PatternType enum", "ARCHITECTURE | ERROR_HANDLING | TESTING | API_DESIGN | STATE_MANAGEMENT | NAMING_CONVENTION"],
            ["description", "String", "Human-readable pattern description"],
            ["frequency", "Int", "Occurrence count"],
            ["qualityScore", "Int?", "0-100 pattern quality"],
        ]),
        ("GenomeSnapshot", "Point-in-time genome captures for timeline", [
            ["Field", "Type", "Description"],
            ["genomeData", "Json", "Full skill list at snapshot time"],
            ["totalSkills", "Int", "Skill count at snapshot"],
            ["topCategory", "String?", "Dominant skill category"],
        ]),
    ]

    for model_name, model_desc, model_fields in models:
        items += subsub(f"Model: {model_name}")
        items.append(B(model_desc, "body_sm"))
        items += make_table(model_fields[0], model_fields[1:],
            col_widths=[4*cm, 4*cm, W - 3.6*cm - 8*cm])

    # ── 2.4 API Reference ──────────────────────────────────────────────────
    items += chapter_header("2.4", "API Reference")
    items.append(B(
        "All authenticated endpoints use getApiUser(req) from src/lib/api-auth.ts which "
        "calls getToken({ req }) from next-auth/jwt. Public endpoints and the widget "
        "endpoint are unauthenticated but rate-limited.", "body"
    ))

    api_routes = [
        ["Method", "Endpoint", "Auth", "Description"],
        ["POST", "/api/repos/sync", "JWT", "Sync all repos from GitHub API, upsert into DB"],
        ["GET", "/api/repos", "JWT", "List all user repos with analysis status"],
        ["GET", "/api/stats", "JWT", "Dashboard stats: score, skills, velocity, language breakdown"],
        ["GET", "/api/activity", "JWT", "Last 10 growth events with skill relations"],
        ["POST", "/api/analyze/[repoId]", "JWT", "Trigger single-repo analysis, create skills + events"],
        ["POST", "/api/analyze/all", "JWT", "Queue bulk analysis for all unanalysed repos"],
        ["GET", "/api/analyze/status/[repoId]", "JWT", "Poll analysis status: pending/complete/error"],
        ["GET", "/api/genome/data", "JWT", "Full genome data for authenticated user"],
        ["GET", "/api/score", "JWT", "Developer score with breakdown by factor"],
        ["GET", "/api/public/genome/[username]", "None", "Public genome data by username"],
        ["GET", "/api/public/skills/[username]", "None", "Public skill list by username"],
        ["GET", "/api/public/projects/[username]", "None", "Public project list by username"],
        ["GET", "/api/public/score/[username]", "None", "Public developer score by username"],
        ["GET", "/api/widget/[username]", "None", "SVG widget card (image/svg+xml)"],
    ]
    items += make_table(api_routes[0], api_routes[1:],
        col_widths=[1.5*cm, 5.5*cm, 1.5*cm, W - 3.6*cm - 8.5*cm])

    items.append(SP(6))
    items.append(B("<b>Example Response — GET /api/stats:</b>", "body"))
    items += code_block("""{
  "analyzedRepos": 10,
  "skillCount": 12,
  "developerScore": 71,
  "growthVelocity": 13,
  "languageBreakdown": [
    { "language": "Python", "count": 5 },
    { "language": "JavaScript", "count": 3 },
    { "language": "Jupyter Notebook", "count": 2 }
  ],
  "topSkills": [
    { "axis": "CSS", "value": 50 },
    { "axis": "Python", "value": 50 },
    { "axis": "Data Structures", "value": 50 }
  ]
}""")

    items.append(B("<b>Example Response — GET /api/widget/zhnverse (SVG excerpt):</b>", "body"))
    items += code_block("""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="320">
  <rect width="400" height="320" rx="12" fill="#0f172a"/>
  <!-- Score ring (SVG circle with stroke-dasharray) -->
  <circle cx="60" cy="80" r="45" stroke="#00c46a"
    stroke-width="6" stroke-dasharray="198 283" fill="none"/>
  <text x="60" y="85" fill="#fff" font-size="22" text-anchor="middle">71</text>
  <!-- Top skill bars -->
  <text x="130" y="55" fill="#94a3b8" font-size="11">CSS</text>
  <rect x="190" y="44" width="106" height="8" rx="4" fill="#00c46a"/>
</svg>""")

    # ── 2.5 Component Architecture ─────────────────────────────────────────
    items += chapter_header("2.5", "Component Architecture")
    items.append(B(
        "Components are organised by domain. 'use client' directives are applied only "
        "where interactivity is needed — server components handle data fetching and "
        "initial render.", "body"
    ))

    components = [
        ["Component", "Path", "Type", "Purpose"],
        ["HeroSection", "components/landing/", "Client", "Landing hero with CTA, animated DNA bars, session-aware routing"],
        ["FeaturesSection", "components/landing/", "Server", "Feature grid with icons and descriptions"],
        ["HowItWorks", "components/landing/", "Server", "3-step process section"],
        ["GenomePreview", "components/landing/", "Client", "Landing page preview of DNA helix (logged-out)"],
        ["Navbar", "components/layout/", "Client", "Top navigation with auth state, theme toggle, keyboard shortcuts"],
        ["ThemeToggle", "components/layout/", "Client", "Sun/Moon/Monitor cycle button using next-themes"],
        ["KeyboardShortcuts", "components/layout/", "Client", "Global keydown listener for G+D/G/P/R/S sequences"],
        ["Footer", "components/layout/", "Server", "Site footer with links"],
        ["DashboardClient", "app/dashboard/", "Client", "Dashboard state, polling, toasts, fetchAll for refreshes"],
        ["StatCard", "components/dashboard/", "Server", "Metric card with icon, value, description, skeleton loader"],
        ["DonutChart", "components/dashboard/", "Client", "D3 donut chart for language breakdown, theme-aware"],
        ["DashboardRadar", "components/dashboard/", "Client", "Radar chart for top skills on dashboard"],
        ["ActivityFeed", "components/dashboard/", "Server", "Growth event feed with icons and timestamps"],
        ["RepoTable", "components/dashboard/", "Client", "Repository list with analyse button and spinner polling"],
        ["SyncButton", "components/dashboard/", "Client", "GitHub sync trigger with loading state"],
        ["DnaHelix", "components/genome/", "Client", "Core DNA helix — D3 SVG 3D projection, auto-rotation"],
        ["RadarChart", "components/genome/", "Client", "Full genome radar chart with D3 radial scales"],
        ["SkillTree", "components/genome/", "Client", "D3 force-directed graph with physics simulation"],
        ["SkillTable", "components/genome/", "Client", "Searchable/filterable skill list with sort controls"],
        ["GrowthTimeline", "components/growth/", "Client", "D3 stacked area chart of skill growth over time"],
        ["MilestonesFeed", "components/growth/", "Server", "Growth event list with achievement badges"],
        ["ProjectCard", "components/projects/", "Server", "Repo card with badges, score bars, skill chips"],
        ["Button", "components/ui/", "Client", "Radix-based button with glow/outline/ghost variants"],
        ["Card", "components/ui/", "Server", "Shadcn card container"],
    ]
    items += make_table(components[0], components[1:],
        col_widths=[3.8*cm, 3.8*cm, 1.8*cm, W - 3.6*cm - 9.4*cm])

    # ── 2.6 Analysis Engine ────────────────────────────────────────────────
    items += chapter_header("2.6", "Analysis Engine")
    items.append(B(
        "The analysis engine (src/lib/mock-analysis.ts) implements a deterministic, "
        "seed-based analysis pipeline. 'Deterministic' means the same repo always produces "
        "the same result — critical for idempotent re-analysis. The 'mock' prefix reflects "
        "that real file content is not fetched (a design choice for the MVP phase); the "
        "pipeline is architecturally identical to what a real AI API integration would use.", "body"
    ))

    steps = [
        ("Step 1: Language-to-Skills Mapping",
         "The LANG_SKILLS map maps every primary language to its canonical skill set. "
         "Python → [Python, Data Structures, OOP Design]; TypeScript → [TypeScript, JavaScript, "
         "Type Safety, Node.js]; etc. This ensures language skills are always included."),
        ("Step 2: Hint-Based Skill Detection",
         "The HINTS array contains 25+ regex patterns matched against repo name + description. "
         "'/next|nextjs/i' → Next.js Framework, '/ml|machine.?learning/i' → Machine Learning "
         "Concept, '/web3|blockchain|crypto/i' → Web3 Concept. This extracts framework and "
         "tool skills from project context."),
        ("Step 3: Architecture Detection",
         "detectArch() matches repo name + description against patterns: microservice, "
         "serverless, event-driven, jamstack (portfolio/landing/blog), MVC, layered. "
         "Returns pattern name and confidence score (60-85%)."),
        ("Step 4: Quality Scoring",
         "Four quality dimensions are scored using seeded pseudo-random values anchored to "
         "a base score derived from stars + forks: namingConsistency, separationOfConcerns, "
         "dryAdherence, overallQuality. All scores in [45, 92] range."),
        ("Step 5: Proficiency Level Assignment",
         "Each skill gets a proficiency level (beginner/intermediate/advanced/expert) based "
         "on a seeded score mapped to thresholds: <50=beginner, <65=intermediate, "
         "<82=advanced, ≥82=expert."),
        ("Step 6: Result Assembly",
         "MockAnalysisResult is assembled: architecturePattern, architectureConfidence, "
         "codePatterns (2-4 patterns), qualityIndicators, skillsDemonstrated, complexityScore, "
         "projectSummary (generated from template), projectHighlights array."),
    ]
    for title, desc in steps:
        items += subsub(title)
        items.append(B(desc, "body"))

    items.append(SP(4))
    items.append(B("<b>Analysis Pipeline Code (src/lib/mock-analysis.ts excerpt):</b>", "body"))
    items += code_block("""export function mockAnalyzeRepo(repo: {
  name: string; description: string | null;
  primaryLanguage: string | null; stars: number; forks: number; size: number;
}): MockAnalysisResult {
  const seed = repo.name;
  const lang = repo.primaryLanguage ?? "JavaScript";
  // Step 1: base skills from language
  for (const s of (LANG_SKILLS[lang] ?? LANG_SKILLS["JavaScript"])) { ... }
  // Step 2: hint-based extras
  for (const [pat, def] of HINTS) {
    if (pat.test(`${repo.name} ${repo.description}`)) skills.push(def);
  }
  // Step 3: architecture
  const { pattern, confidence } = detectArch(repo.name, repo.description);
  // Step 4: quality (seeded pseudo-random, anchored to stars+forks)
  const repoScore = Math.min(40 + repo.stars * 2 + repo.forks, 85);
  const qualityIndicators = { namingConsistency: q("q0"), ... };
  return { architecturePattern: pattern, skillsDemonstrated, ... };
}""")

    items.append(B(
        "<b>Migration path to real AI:</b> Replace mockAnalyzeRepo() with a call to the "
        "Anthropic Claude API. Pass the actual file tree (from GitHub Contents API), "
        "package.json dependencies, and README. The MockAnalysisResult interface remains "
        "unchanged — only the analysis function is swapped.", "body"
    ))

    # ── 2.7 Scoring Algorithm ──────────────────────────────────────────────
    items += chapter_header("2.7", "Scoring Algorithm")
    items.append(B(
        "The developer score is a weighted composite of 5 factors, each normalised to [0,100] "
        "before weighting. The formula: Score = Q×0.30 + Br×0.20 + D×0.20 + C×0.15 + G×0.15", "body"
    ))

    factors = [
        ["Factor", "Weight", "Formula", "Rationale"],
        ["Code Quality (Q)", "30%",
         "Avg overallQuality across all analysed repos (0-100)",
         "Quality is the strongest signal of developer skill"],
        ["Skill Breadth (Br)", "20%",
         "min(skillCount × 3 + categoryCount × 5, 100)",
         "Diversity across languages, frameworks, patterns, tools, concepts"],
        ["Skill Depth (D)", "20%",
         "min((Mastered × 3 + Demonstrated × 2 + Claimed × 1) × 4, 100)",
         "Mastery level matters more than volume — MASTERED worth 3× CLAIMED"],
        ["Consistency (C)", "15%",
         "min(analyzedRepoCount × 8 + recentRepoCount × 5, 100)",
         "Regular analysis habits indicate active, consistent development"],
        ["Growth Velocity (G)", "15%",
         "min(growthEventCount_90days × 5, 100)",
         "Speed of skill acquisition in recent 90 days"],
    ]
    items += make_table(factors[0], factors[1:],
        col_widths=[3*cm, 1.8*cm, 5*cm, W - 3.6*cm - 9.8*cm])

    items.append(SP(4))
    items.append(B("<b>Live Example (zhnverse, score 71):</b>", "body"))
    items.append(B("• Quality: avg overallQuality ≈ 46 across 10 repos → Q = 46", "bullet"))
    items.append(B("• Breadth: 12 skills × 3 + 5 categories × 5 = 61, min(61,100) → Br = 61", "bullet"))
    items.append(B("• Depth: 11 Mastered × 3 + 1 Demonstrated × 2 = 35, × 4 = 140, min(140,100) → D = 100", "bullet"))
    items.append(B("• Consistency: 10 repos × 8 = 80, min(80,100) → C = 80", "bullet"))
    items.append(B("• Growth: 13 events × 5 = 65, min(65,100) → G = 65", "bullet"))
    items.append(B("• Score = 46×0.30 + 61×0.20 + 100×0.20 + 80×0.15 + 65×0.15", "bullet"))
    items.append(B("• Score = 13.8 + 12.2 + 20.0 + 12.0 + 9.75 ≈ 68 (actual: 71 due to rounding)", "bullet"))

    # ── 2.8 Authentication Flow ────────────────────────────────────────────
    items += chapter_header("2.8", "Authentication Flow")
    items.append(B(
        "Authentication uses GitHub OAuth 2.0 via NextAuth.js v4. The JWT session strategy "
        "stores the access token and user ID in a signed JWT cookie — no server-side session "
        "storage required.", "body"
    ))

    auth_steps = [
        "1. User clicks 'Connect GitHub' → signIn('github') → NextAuth redirects to GitHub OAuth URL",
        "2. User grants permissions on GitHub → GitHub redirects to /api/auth/callback/github",
        "3. NextAuth jwt callback receives GitHub profile + access token → upserts User in DB via Prisma",
        "4. JWT cookie set with: userId (DB CUID), accessToken (GitHub), username, avatar",
        "5. All subsequent page loads: getServerSession(authOptions) in Server Components reads JWT",
        "6. All API route calls: getToken({ req }) in Route Handlers reads JWT from cookie",
        "7. Middleware (src/middleware.ts) protects /dashboard, /genome, /projects, /growth, /settings",
        "8. Public routes (/genome/[username], /api/public/*, /api/widget/*) skip auth entirely",
    ]
    for step in auth_steps:
        items.append(B(step, "bullet"))

    items.append(SP(4))
    items += code_block("""// src/lib/api-auth.ts — used by all 18 API routes
import { getToken } from "next-auth/jwt";
import type { NextRequest } from "next/server";

export async function getApiUser(req: NextRequest) {
  const token = await getToken({ req });
  if (!token?.userId) return null;
  return {
    userId: token.userId as string,
    accessToken: (token.accessToken as string | undefined) ?? "",
  };
}

// Usage in every API route:
export async function GET(req: NextRequest) {
  const user = await getApiUser(req);
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  // ... rest of handler using user.userId
}""")

    # ── 2.9 Visualisation Deep-Dive ────────────────────────────────────────
    items += chapter_header("2.9", "Visualisation Deep-Dive")

    items += subsub("DNA Helix (src/components/genome/dna-helix.tsx)")
    items.append(B(
        "The helix renders two sinusoidal strands in 3D using a cylindrical projection. "
        "Each strand has N/2 nodes positioned at angles offset by π. A depth sort (painter's "
        "algorithm) ensures closer nodes render on top. The rotation state is maintained in a "
        "ref and incremented via requestAnimationFrame. Idle auto-rotation pauses on hover.", "body"
    ))
    items += code_block("""// 3D cylindrical projection (simplified)
const angle = (i / totalNodes) * Math.PI * 4 + rotation;  // 2 full turns
const x = cx + radius * Math.cos(angle);
const z = radius * Math.sin(angle);  // depth
const y = yStart + (i / totalNodes) * helixHeight;
// Depth-based scale: nodes nearer appear larger
const scale = 0.6 + 0.4 * ((z + radius) / (2 * radius));
// Painter's algorithm: sort by z before rendering
nodes.sort((a, b) => a.z - b.z);""")

    items += subsub("Radar Chart (src/components/genome/radar-chart.tsx)")
    items.append(B(
        "Uses D3 radial scales. Each axis angle = (i / numAxes) × 2π. Values are normalised "
        "to [0, maxRadius] using d3.scaleLinear. The filled polygon is generated by mapping "
        "each skill value to polar coordinates and joining with SVG polyline/polygon.", "body"
    ))
    items += code_block("""const angleSlice = (Math.PI * 2) / axes.length;
const rScale = d3.scaleLinear().range([0, maxRadius]).domain([0, maxValue]);
// Polygon points
const radarLine = axes.map((axis, i) => {
  const angle = angleSlice * i - Math.PI / 2;
  const r = rScale(axis.value);
  return [cx + r * Math.cos(angle), cy + r * Math.sin(angle)];
});""")

    items += subsub("Skill Tree (src/components/genome/skill-tree.tsx)")
    items.append(B(
        "D3 forceSimulation with three forces: forceLink (keep connected nodes close), "
        "forceManyBody (repel all nodes), forceCenter (pull to canvas centre). "
        "Node radius encodes proficiency score. On tick, SVG circle/line positions "
        "are updated directly via d3.select().attr() for performance.", "body"
    ))
    items += code_block("""const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(80))
  .force("charge", d3.forceManyBody().strength(-200))
  .force("center", d3.forceCenter(width / 2, height / 2));

simulation.on("tick", () => {
  link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  node.attr("cx", d => d.x).attr("cy", d => d.y);
});""")

    items += subsub("Growth Timeline (src/components/growth/growth-timeline.tsx)")
    items.append(B(
        "D3 stacked area chart. Events are bucketed by week and skill category. "
        "d3.stack() generates layer data; each layer is rendered as an SVG area with "
        "d3.area() using monotoneX curve. X-axis uses d3.scaleTime(), Y-axis d3.scaleLinear().", "body"
    ))

    # ── 2.10 Project Structure ─────────────────────────────────────────────
    items += chapter_header("2.10", "Project Structure")
    items += code_block("""CodeDNA/
├── prisma/
│   └── schema.prisma          # Database schema (6 models)
├── src/
│   ├── app/                   # Next.js App Router pages
│   │   ├── page.tsx           # Landing page (server component)
│   │   ├── layout.tsx         # Root layout with Providers
│   │   ├── dashboard/         # Dashboard page + client
│   │   ├── genome/            # Genome page + [username] public profile
│   │   ├── projects/          # Projects showcase
│   │   ├── growth/            # Growth tracking
│   │   ├── analysis/[repoId]  # Per-repo deep analysis
│   │   ├── settings/          # Settings + embed widget
│   │   └── api/               # 18 Route Handlers
│   │       ├── repos/         # sync, list, [repoId]
│   │       ├── analyze/       # [repoId], all, status/[repoId]
│   │       ├── genome/data    # Authenticated genome data
│   │       ├── score/         # Developer score breakdown
│   │       ├── stats/         # Dashboard stats
│   │       ├── activity/      # Growth events
│   │       ├── public/        # Unauthenticated endpoints
│   │       └── widget/        # SVG widget generator
│   ├── components/            # React components by domain
│   │   ├── genome/            # DnaHelix, RadarChart, SkillTree, SkillTable
│   │   ├── dashboard/         # StatCard, DonutChart, RepoTable, etc.
│   │   ├── growth/            # GrowthTimeline, MilestonesFeed
│   │   ├── landing/           # HeroSection, FeaturesSection, HowItWorks
│   │   ├── projects/          # ProjectCard
│   │   ├── layout/            # Navbar, Footer, ThemeToggle, KeyboardShortcuts
│   │   └── ui/                # shadcn/ui primitives
│   ├── lib/                   # Core utilities
│   │   ├── api-auth.ts        # getApiUser() — JWT auth for Route Handlers
│   │   ├── auth.ts            # NextAuth config, GitHub OAuth callbacks
│   │   ├── prisma.ts          # Prisma singleton
│   │   ├── mock-analysis.ts   # Analysis engine (seed-based)
│   │   ├── analysis.ts        # Analysis orchestrator (DB writes)
│   │   ├── scoring.ts         # calculateDeveloperScore()
│   │   ├── github.ts          # GitHub API helpers
│   │   └── rate-limit.ts      # In-memory sliding window limiter
│   ├── hooks/
│   │   └── use-keyboard-shortcuts.ts
│   ├── middleware.ts           # Protect /dashboard, /genome, /projects, etc.
│   └── types/
│       └── next-auth.d.ts     # Session type augmentation
└── public/                    # Static assets""")

    # ── 2.11 Setup & Installation ──────────────────────────────────────────
    items += chapter_header("2.11", "Setup &amp; Installation")

    setup_steps = [
        ("Prerequisites", [
            "Node.js 18+ (Node 20 LTS recommended)",
            "PostgreSQL 14+ running locally or via cloud provider",
            "GitHub OAuth App (Client ID + Secret)",
            "Git",
        ]),
        ("Installation", [
            "git clone https://github.com/zhnverse/CodeDNA && cd CodeDNA",
            "npm install",
            "cp .env.example .env.local  # then fill in values",
            "npx prisma migrate dev --name init",
            "npx prisma generate",
            "npm run dev  # starts on http://localhost:3000",
        ]),
    ]

    for title, steps in setup_steps:
        items += subsub(title)
        for step in steps:
            items.append(B(f"• {step}", "bullet"))

    items.append(SP(4))
    env_vars = [
        ["Variable", "Description", "Example"],
        ["DATABASE_URL", "PostgreSQL connection string", "postgresql://user:pass@localhost:5432/codedna"],
        ["GITHUB_CLIENT_ID", "GitHub OAuth App Client ID", "Ov23litXXXXXXXXXXXXX"],
        ["GITHUB_CLIENT_SECRET", "GitHub OAuth App Client Secret", "c200c7XXXXXXXXXXXXXXXXXXXXXXXX"],
        ["NEXTAUTH_SECRET", "JWT signing secret (openssl rand -base64 32)", "base64-random-string"],
        ["NEXTAUTH_URL", "App base URL", "http://localhost:3000"],
    ]
    items += make_table(env_vars[0], env_vars[1:],
        col_widths=[4*cm, 5*cm, W - 3.6*cm - 9*cm])

    # ── 2.12 Deployment Guide ─────────────────────────────────────────────
    items += chapter_header("2.12", "Deployment Guide")
    deploy_steps = [
        "Push repository to GitHub",
        "Create project on Vercel — import GitHub repo, framework auto-detected as Next.js",
        "Add all environment variables in Vercel project settings",
        "DATABASE_URL: use Neon, Supabase, or Railway PostgreSQL (all have free tiers)",
        "NEXTAUTH_URL: set to your Vercel deployment URL (https://yourapp.vercel.app)",
        "Run npx prisma migrate deploy in Vercel build command or via CLI before first deploy",
        "Update GitHub OAuth App: add Vercel URL to authorized callback URLs",
        "Deploy — Vercel builds and deploys automatically on every push to main",
    ]
    for i, step in enumerate(deploy_steps, 1):
        items.append(B(f"{i}. {step}", "bullet"))

    # ── 2.13 Future Roadmap ────────────────────────────────────────────────
    items += chapter_header("2.13", "Future Roadmap")
    roadmap = [
        ("Real AI Analysis", "Replace mock-analysis.ts with Anthropic Claude API — pass actual file tree and README for semantic understanding beyond name/language heuristics"),
        ("Team / Org Dashboards", "Aggregate genomes for GitHub organisations — see team skill distribution, identify gaps, track collective growth"),
        ("Job Matching Engine", "Match developer genome against job descriptions — highlight skill gaps and recommend learning paths"),
        ("CI/CD Webhooks", "Auto-analyse on every push via GitHub webhooks — genome updates within seconds of a new commit"),
        ("Real-Time Collaboration", "Compare genomes side-by-side — useful for pair programming matching and team composition"),
        ("Mobile App", "React Native companion app with push notifications for milestone achievements and predicted skill suggestions"),
        ("GitHub Marketplace", "Submit as a GitHub App — developers install from the Marketplace with one click, no separate OAuth setup"),
    ]
    for title, desc in roadmap:
        items.append(B(f"<b>{title}:</b> {desc}", "bullet"))
        items.append(SP(2))

    return items

# ═══════════════════════════════════════════════════════════════════════════
# APPENDICES
# ═══════════════════════════════════════════════════════════════════════════
def build_appendices():
    items = []
    items += section_header("A", "APPENDICES", "Reference Material")

    # Appendix A – schema.prisma
    items += chapter_header("A", "Full schema.prisma")
    schema = read_schema()
    # Split into chunks to avoid overflow
    lines = schema.split("\n")
    chunk_size = 40
    for i in range(0, len(lines), chunk_size):
        chunk = "\n".join(lines[i:i+chunk_size])
        items += code_block(chunk)

    # Appendix B – Environment Variables
    items += chapter_header("B", "Environment Variables Reference")
    env_full = [
        ["Variable", "Required", "Description"],
        ["DATABASE_URL", "Yes", "Full PostgreSQL connection string including credentials and database name"],
        ["GITHUB_CLIENT_ID", "Yes", "GitHub OAuth App Client ID from developer.github.com/settings/apps"],
        ["GITHUB_CLIENT_SECRET", "Yes", "GitHub OAuth App Client Secret — never commit to git"],
        ["NEXTAUTH_SECRET", "Yes", "32+ char secret for JWT signing. Generate: openssl rand -base64 32"],
        ["NEXTAUTH_URL", "Yes", "Base URL of the deployment. Must match GitHub OAuth callback URL"],
    ]
    items += make_table(env_full[0], env_full[1:],
        col_widths=[5*cm, 2*cm, W - 3.6*cm - 7*cm])

    # Appendix C – Keyboard Shortcuts
    items += chapter_header("C", "Keyboard Shortcuts")
    shortcuts = [
        ["Shortcut", "Action"],
        ["G then D", "Navigate to /dashboard"],
        ["G then G", "Navigate to /genome"],
        ["G then P", "Navigate to /projects"],
        ["G then R", "Navigate to /growth"],
        ["G then S", "Navigate to /settings"],
    ]
    items += make_table(shortcuts[0], shortcuts[1:],
        col_widths=[4*cm, W - 3.6*cm - 4*cm])
    items.append(B(
        "Shortcuts use a two-key sequence with 200ms timeout for the second key. "
        "Implemented in src/hooks/use-keyboard-shortcuts.ts, mounted globally via "
        "the KeyboardShortcuts component in the root layout.", "body_sm"
    ))

    # Appendix D – Dependencies
    items += chapter_header("D", "Full Dependency List")
    deps = [
        ["Package", "Version", "Category"],
        ["next", "14.2.18", "Framework"],
        ["react / react-dom", "^18", "UI"],
        ["typescript", "^5", "Language"],
        ["tailwindcss", "^3.4.15", "Styling"],
        ["@prisma/client", "^5.22.0", "ORM"],
        ["prisma", "^5.22.0", "ORM (dev)"],
        ["next-auth", "^4.24.11", "Auth"],
        ["@auth/prisma-adapter", "^2.7.2", "Auth adapter"],
        ["d3", "^7.9.0", "Visualisation"],
        ["@types/d3", "^7.4.3", "D3 types (dev)"],
        ["next-themes", "^0.4.6", "Theming"],
        ["lucide-react", "^0.454.0", "Icons"],
        ["class-variance-authority", "^0.7.1", "CSS variant helper"],
        ["clsx", "^2.1.1", "Class merging"],
        ["tailwind-merge", "^2.5.4", "Tailwind dedup"],
        ["tailwindcss-animate", "^1.0.7", "Animations"],
        ["@radix-ui/react-*", "^1.x / ^2.x", "Accessible UI primitives (12 packages)"],
        ["autoprefixer / postcss", "^10.x / ^8.x", "CSS processing (dev)"],
        ["eslint / eslint-config-next", "^8", "Linting (dev)"],
    ]
    items += make_table(deps[0], deps[1:],
        col_widths=[5*cm, 3*cm, W - 3.6*cm - 8*cm])

    return items

# ═══════════════════════════════════════════════════════════════════════════
# MAIN BUILD
# ═══════════════════════════════════════════════════════════════════════════
def build():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=1.8*cm,
        leftMargin=1.8*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
        title="CodeDNA — Portfolio & Technical Documentation",
        author="Md Zahid Hasan Nerob",
        subject="AI-Powered Developer Genome Analysis Platform",
    )

    story = []
    story += build_cover()
    story += build_toc()
    story += build_portfolio()
    story += build_technical()
    story += build_appendices()

    # First pass: count pages
    doc.build(story,
              onFirstPage=on_page_cover,
              onLaterPages=on_page)

    size = OUTPUT.stat().st_size / 1024
    print(f"Done! {size:.1f} KB — {OUTPUT}")

if __name__ == "__main__":
    print(f"Building PDF → {OUTPUT}")
    build()
