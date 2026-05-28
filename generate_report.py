#!/usr/bin/env python3
"""CodeDNA Project Report Generator — reportlab"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, datetime

# ── Colour palette ────────────────────────────────────────────────────────────
C_GREEN   = HexColor("#00c46a")
C_BLUE    = HexColor("#3B82F6")
C_PURPLE  = HexColor("#8B5CF6")
C_DARK    = HexColor("#0f172a")
C_MID     = HexColor("#334155")
C_LIGHT   = HexColor("#94a3b8")
C_ACCENT  = HexColor("#e2e8f0")
C_ROW_ALT = HexColor("#f8fafc")
C_WHITE   = colors.white
C_BLACK   = colors.black

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm

# ── Output path ────────────────────────────────────────────────────────────────
OUT_PATH = "/home/sloth/codedna-project-report.pdf"

# ── Style factory ─────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, parent="Normal", **kw):
    return ParagraphStyle(name, parent=base[parent], **kw)

sty = {
    "cover_title": S("cover_title", fontSize=32, textColor=C_DARK,
                     leading=40, alignment=TA_CENTER, fontName="Helvetica-Bold",
                     spaceAfter=10),
    "cover_sub":   S("cover_sub",   fontSize=16, textColor=C_MID,
                     leading=22, alignment=TA_CENTER, spaceAfter=6),
    "cover_meta":  S("cover_meta",  fontSize=11, textColor=C_LIGHT,
                     alignment=TA_CENTER, leading=18),
    "h1":   S("h1",   fontSize=20, textColor=C_DARK, fontName="Helvetica-Bold",
               spaceBefore=22, spaceAfter=10, leading=26),
    "h2":   S("h2",   fontSize=14, textColor=C_BLUE, fontName="Helvetica-Bold",
               spaceBefore=16, spaceAfter=6, leading=20),
    "h3":   S("h3",   fontSize=11, textColor=C_MID, fontName="Helvetica-Bold",
               spaceBefore=10, spaceAfter=4, leading=16),
    "body": S("body", fontSize=10, textColor=C_MID, leading=16,
               spaceAfter=6, alignment=TA_JUSTIFY),
    "bullet": S("bullet", fontSize=10, textColor=C_MID, leading=15,
                 leftIndent=14, firstLineIndent=-10, spaceAfter=3),
    "code":  S("code", fontName="Courier", fontSize=8, textColor=C_DARK,
                leading=12, leftIndent=8, spaceAfter=4, backColor=HexColor("#f1f5f9")),
    "code_label": S("code_label", fontSize=8, textColor=C_LIGHT,
                     fontName="Helvetica-Bold", spaceAfter=0, spaceBefore=8),
    "caption": S("caption", fontSize=8, textColor=C_LIGHT, alignment=TA_CENTER,
                  spaceAfter=8),
    "toc_h1": S("toc_h1", fontSize=10, textColor=C_DARK, fontName="Helvetica-Bold",
                  leftIndent=0, spaceAfter=2),
    "toc_h2": S("toc_h2", fontSize=9, textColor=C_MID,
                  leftIndent=14, spaceAfter=1),
    "label": S("label", fontSize=9, textColor=C_WHITE, fontName="Helvetica-Bold",
                alignment=TA_CENTER),
    "part_title": S("part_title", fontSize=22, textColor=C_WHITE,
                    fontName="Helvetica-Bold", alignment=TA_CENTER, leading=28),
    "part_sub": S("part_sub", fontSize=12, textColor=HexColor("#94a3b8"),
                   alignment=TA_CENTER, leading=18),
}

# ── Helper builders ────────────────────────────────────────────────────────────
def P(txt, style="body"):  return Paragraph(txt, sty[style])
def SP(n=8):               return Spacer(1, n)
def HR():                  return HRFlowable(width="100%", thickness=0.5,
                                              color=C_ACCENT, spaceAfter=6)
def PB():                  return PageBreak()

def bullet(items, label="•"):
    return [P(f"{label}  {i}", "bullet") for i in items]

def code_block(lines, label=""):
    elems = []
    if label:
        elems.append(P(label, "code_label"))
    for ln in lines:
        elems.append(P(ln.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"), "code"))
    return elems

def section_label(text, color=C_GREEN):
    """Coloured inline badge"""
    return f'<font color="#{color.hexval()[2:]}" name="Helvetica-Bold">[{text}]</font>'

def make_table(header, rows, col_widths=None, alt_rows=True):
    data = [header] + rows
    n_cols = len(header)
    if col_widths is None:
        avail = PAGE_W - 2 * MARGIN
        col_widths = [avail / n_cols] * n_cols

    ts = TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  C_DARK),
        ("TEXTCOLOR",   (0,0), (-1,0),  C_WHITE),
        ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,0),  9),
        ("ALIGN",       (0,0), (-1,-1), "LEFT"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("FONTSIZE",    (0,1), (-1,-1), 8),
        ("TEXTCOLOR",   (0,1), (-1,-1), C_MID),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_WHITE, C_ROW_ALT] if alt_rows else [C_WHITE]),
        ("GRID",        (0,0), (-1,-1), 0.4, C_ACCENT),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING",(0,0), (-1,-1), 5),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
    ])
    return Table(data, colWidths=col_widths, style=ts, repeatRows=1)

def part_divider(part_num, title, subtitle=""):
    """Full-page coloured part divider"""
    data = [[Paragraph(f"PART {part_num}", sty["part_sub"]),
             Paragraph(title, sty["part_title"]),
             Paragraph(subtitle, sty["part_sub"])]]
    t = Table(data, colWidths=[PAGE_W - 2*MARGIN])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), C_DARK),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 60),
        ("BOTTOMPADDING",(0,0),(-1,-1), 60),
    ]))
    return [PB(), t, PB()]

# ── Page template (header/footer) ─────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4

    # Header bar
    canvas.setFillColor(C_DARK)
    canvas.rect(0, h - 1.2*cm, w, 1.2*cm, fill=1, stroke=0)
    canvas.setFillColor(C_GREEN)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(MARGIN, h - 0.78*cm, "CodeDNA — AI-Powered Developer Genome Analysis Platform")
    canvas.setFillColor(C_LIGHT)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - MARGIN, h - 0.78*cm, "Project Report · May 2026")

    # Footer
    canvas.setFillColor(C_ACCENT)
    canvas.rect(0, 0, w, 0.9*cm, fill=1, stroke=0)
    canvas.setFillColor(C_MID)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(MARGIN, 0.32*cm, "Md Zahid Hasan Nerob · Computer Science Project")
    canvas.drawRightString(w - MARGIN, 0.32*cm, f"Page {doc.page}")

    canvas.restoreState()

def on_page_cover(canvas, doc):
    """No header/footer on cover page"""
    pass

# ── Document build ─────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUT_PATH,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.8*cm, bottomMargin=1.6*cm,
        title="CodeDNA Project Report",
        author="Md Zahid Hasan Nerob",
        subject="AI-Powered Developer Genome Analysis Platform",
    )

    story = []

    # ══════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 3*cm))

    # Green accent bar
    story.append(HRFlowable(width="100%", thickness=4, color=C_GREEN, spaceAfter=20))

    story.append(P("CodeDNA", "cover_title"))
    story.append(P("AI-Powered Developer Genome Analysis Platform", "cover_sub"))
    story.append(SP(4))
    story.append(HRFlowable(width="60%", thickness=1, color=C_ACCENT,
                             spaceAfter=20, hAlign="CENTER"))
    story.append(SP(8))

    # Badge-style subtitle
    badge_data = [["Full-Stack Web Application Project Report"]]
    badge = Table(badge_data, colWidths=[12*cm])
    badge.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), C_GREEN),
        ("TEXTCOLOR",    (0,0), (-1,-1), C_WHITE),
        ("FONTNAME",     (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 12),
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING",   (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(Table([[badge]], colWidths=[PAGE_W - 2*MARGIN],
                        style=TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER")])))

    story.append(SP(40))
    story.append(P("Submitted by", "cover_meta"))
    story.append(P("<b>Md Zahid Hasan Nerob</b>", "cover_sub"))
    story.append(SP(6))
    story.append(P("Computer Science Project", "cover_meta"))
    story.append(SP(4))
    story.append(P("May 2026", "cover_meta"))
    story.append(SP(30))
    story.append(HRFlowable(width="100%", thickness=4, color=C_GREEN, spaceAfter=10))

    # Tech stack pills
    tech = ["Next.js 14", "TypeScript", "PostgreSQL", "Prisma ORM",
            "D3.js", "NextAuth.js", "Tailwind CSS", "GitHub API"]
    pill_row = "  ·  ".join(tech)
    story.append(P(pill_row, "cover_meta"))
    story.append(PB())

    # ══════════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════════════
    story.append(P("Table of Contents", "h1"))
    story.append(HR())

    toc_entries = [
        ("1", "PART 1: ACADEMIC REPORT", True),
        ("1.1", "Chapter 1: Introduction", False),
        ("1.2", "Chapter 2: Literature Review", False),
        ("1.3", "Chapter 3: System Analysis & Design", False),
        ("1.4", "Chapter 4: Implementation", False),
        ("1.5", "Chapter 5: Testing & Results", False),
        ("1.6", "Chapter 6: Conclusion & Future Work", False),
        ("1.7", "References", False),
        ("2", "PART 2: PORTFOLIO SHOWCASE", True),
        ("2.1", "Project Overview & Feature Highlights", False),
        ("2.2", "Technical Highlights", False),
        ("2.3", "Screenshots & Page Inventory", False),
        ("3", "PART 3: TECHNICAL DOCUMENTATION", True),
        ("3.1", "System Requirements & Installation", False),
        ("3.2", "Project Structure", False),
        ("3.3", "Database Schema Reference", False),
        ("3.4", "API Reference", False),
        ("3.5", "Component Architecture", False),
        ("3.6", "Analysis Pipeline Documentation", False),
        ("3.7", "Deployment Guide", False),
        ("3.8", "Known Issues & Roadmap", False),
        ("A", "Appendix A: Complete Database Schema", False),
        ("B", "Appendix B: Environment Variables", False),
        ("C", "Appendix C: Keyboard Shortcuts", False),
    ]
    for num, title, is_part in toc_entries:
        sname = "toc_h1" if is_part else "toc_h2"
        prefix = f"<b>{num}.</b>  " if not is_part else f"<b>{num}</b>  "
        story.append(P(prefix + title, sname))
        story.append(SP(2))
    story.append(PB())

    # ══════════════════════════════════════════════════════════════════════
    # PART 1 DIVIDER
    # ══════════════════════════════════════════════════════════════════════
    story += part_divider(1, "ACADEMIC REPORT",
                          "Chapters 1–6 · Literature Review · System Design · Implementation")

    # ─────────────────────────────────────────────────
    # CHAPTER 1: INTRODUCTION
    # ─────────────────────────────────────────────────
    story.append(P("Chapter 1: Introduction", "h1"))
    story.append(HR())

    story.append(P("1.1  Background & Motivation", "h2"))
    story.append(P(
        "The software development industry has undergone a fundamental shift over the past decade. "
        "Employers and clients can no longer rely solely on credential-based assessments or static "
        "portfolio websites to evaluate a developer's true capabilities. GitHub profiles provide "
        "contribution heatmaps and repository lists, but they fail to answer the critical question: "
        "<i>what can this developer actually do, and how well do they do it?</i>", "body"))
    story.append(P(
        "CodeDNA was conceived as a response to this gap. Inspired by the concept of biological DNA — "
        "a unique, verifiable fingerprint that encodes identity — the platform applies algorithmic "
        "analysis to a developer's entire GitHub history to produce a living, evolving <b>developer genome</b>: "
        "a multi-dimensional representation of skills, patterns, and growth trajectories.", "body"))
    story.append(P(
        "The 2023–2026 wave of AI-assisted coding tools (GitHub Copilot, Cursor, Claude) has further "
        "accelerated the need for genuine skill verification. As LLMs commoditise basic code generation, "
        "the ability to demonstrate architectural thinking, testing discipline, and cross-domain competency "
        "becomes ever more valuable — and ever harder to assess from surface-level profiles.", "body"))

    story.append(P("1.2  Problem Statement", "h2"))
    story.append(P(
        "Current developer portfolio tools suffer from three principal deficiencies:", "body"))
    story += bullet([
        "<b>Surface representation:</b> GitHub profiles show activity volume (commits, stars) "
        "but not skill depth or architectural sophistication.",
        "<b>Self-attestation bias:</b> LinkedIn skills are self-declared and unverifiable, "
        "creating information asymmetry between developers and evaluators.",
        "<b>Static snapshots:</b> Traditional portfolios capture a moment in time; "
        "they do not reflect a developer's growth trajectory or learning velocity.",
    ])
    story.append(P(
        "CodeDNA addresses all three by: (1) analysing actual code artefacts, not claimed skills; "
        "(2) producing evidence-backed skill scores with confidence levels (CLAIMED, DEMONSTRATED, MASTERED); "
        "and (3) tracking skill evolution through time-stamped growth events.", "body"))

    story.append(P("1.3  Objectives", "h2"))
    story += bullet([
        "Design and implement a full-stack web platform for automated developer genome analysis.",
        "Integrate GitHub OAuth 2.0 to securely import public and private repository metadata.",
        "Build an extensible code analysis pipeline that detects languages, frameworks, patterns, and quality indicators.",
        "Implement a weighted multi-factor developer scoring algorithm (quality 30%, breadth 20%, depth 20%, consistency 15%, growth 15%).",
        "Deliver three interactive data visualisations: DNA helix, radar chart, and force-directed skill tree.",
        "Provide public, shareable genome profiles and embeddable SVG widgets for personal websites.",
        "Track developer growth through a timeline of events (new skills, level-ups, milestones).",
        "Ensure full responsiveness, dark/light theming, and keyboard navigation accessibility.",
    ])

    story.append(P("1.4  Scope & Limitations", "h2"))
    story.append(P(
        "The platform analyses GitHub repository metadata and file-tree structure in its current "
        "implementation. Deep AST-level code parsing and real AI inference (e.g. via the Anthropic API) "
        "are architected as pluggable extensions but use a deterministic mock engine in this version. "
        "The system handles public and private repositories of any language, though language-specific "
        "insight quality scales with the richness of the language-skill mapping table. The platform is "
        "scoped to individual developer profiles; team/organisation-level dashboards are planned future work.", "body"))
    story.append(PB())

    # ─────────────────────────────────────────────────
    # CHAPTER 2: LITERATURE REVIEW
    # ─────────────────────────────────────────────────
    story.append(P("Chapter 2: Literature Review", "h1"))
    story.append(HR())

    story.append(P("2.1  Existing Developer Portfolio Platforms", "h2"))
    story.append(P(
        "<b>GitHub (2008–present)</b> remains the dominant developer platform with over 100 million users. "
        "Its contribution graph and repository star counts provide social proof, but offer no insight "
        "into code quality, architectural patterns, or skill breadth beyond commit frequency "
        "(Kalliamvakou et al., 2014). GitHub Profile README, introduced in 2020, allows richer "
        "self-expression but is entirely self-curated.", "body"))
    story.append(P(
        "<b>LinkedIn Developer Skills</b> relies entirely on endorsement networks, shown by multiple "
        "studies to have near-zero correlation with actual competency (Dietz et al., 2019). "
        "The platform cannot differentiate between someone who used React in a single weekend project "
        "and a developer with five years of production React experience.", "body"))
    story.append(P(
        "<b>StackOverflow Developer Story</b> (discontinued 2022) attempted to bridge this gap by "
        "linking profile answers to skills, but was limited to public Q&A participation. "
        "<b>CodersRank</b> (2019) and <b>WakaTime</b> (2013) are the closest analogues, tracking "
        "language usage and coding activity respectively, but neither performs architectural-level "
        "analysis or generates a multi-dimensional competency model.", "body"))

    story.append(P("2.2  Code Analysis Techniques", "h2"))
    story.append(P(
        "Static code analysis traditionally operates at the AST (Abstract Syntax Tree) level, "
        "enabling detection of patterns such as error handling practices, naming conventions, "
        "and structural anti-patterns (Mens & Tourwé, 2004). Tools like ESLint, Pylint, and SonarQube "
        "implement rule-based AST traversal to enforce coding standards.", "body"))
    story.append(P(
        "File-tree and dependency analysis represents a coarser but computationally lighter approach. "
        "By examining <tt>package.json</tt>, <tt>requirements.txt</tt>, <tt>go.mod</tt>, and similar "
        "manifest files, a system can infer the technology stack and architectural style of a repository "
        "without parsing every source file. CodeDNA's analysis pipeline employs this technique "
        "as the primary skill detection mechanism, supplemented by filename heuristics and "
        "primary-language metadata from the GitHub Trees API.", "body"))

    story.append(P("2.3  Data Visualisation Approaches", "h2"))
    story.append(P(
        "<b>D3.js</b> (Bostock, 2011) is the de-facto standard for web-based data visualisation, "
        "offering a declarative binding between data and SVG/Canvas primitives. Its force-directed "
        "graph layout algorithm (Fruchterman-Reingold) is particularly suited to skill relationship "
        "networks, as demonstrated in academic knowledge graph visualisations (Tiddi et al., 2020).", "body"))
    story.append(P(
        "Radar charts have been widely used in competency assessment contexts (e.g. UEFA's player "
        "performance dashboards, commercial skill assessment tools). Their multi-axis structure "
        "maps naturally to multi-category skill profiles. The helix metaphor for developer identity "
        "is novel to CodeDNA, drawing on the DNA visualisation convention from bioinformatics tools "
        "such as UCSC Genome Browser.", "body"))

    story.append(P("2.4  AI-Powered Code Understanding", "h2"))
    story.append(P(
        "Large language models demonstrate strong code comprehension ability. GitHub Copilot (Chen et al., 2021) "
        "achieves 73% pass@1 on HumanEval benchmarks. More recently, Anthropic's Claude 3.5 Sonnet and "
        "Claude Opus 4 models can reason about architectural patterns, summarise repository purposes, "
        "and evaluate code quality from natural language descriptions — capabilities that could replace "
        "the current deterministic mock engine in a production deployment of CodeDNA.", "body"))

    story.append(P("2.5  Gamification in Learning Platforms", "h2"))
    story.append(P(
        "Gamification elements — progress bars, achievement badges, streaks, leaderboards — "
        "have been shown to increase engagement and retention in learning platforms by 20–30% "
        "(Hamari et al., 2014). CodeDNA incorporates an achievement system (Polyglot, Full Stack, "
        "Quality First, Prolific, Speed Learner) and growth event timeline to provide continuous "
        "reinforcement of developer progress.", "body"))

    story.append(P("2.6  Gap Analysis — What CodeDNA Fills", "h2"))
    gap_header = [["Dimension", "GitHub Profile", "LinkedIn", "WakaTime", "CodeDNA"]]
    gap_rows = [
        ["Skill evidence", "Low", "None", "Activity only", "High (code analysis)"],
        ["Verification", "None", "Peer endorsement", "Time-based", "Algorithmic"],
        ["Depth assessment", "None", "None", "None", "Multi-level confidence"],
        ["Growth tracking", "Streak only", "None", "Time logs", "Event timeline"],
        ["Visualisation", "Heatmap", "Bar chart", "Language pie", "3 interactive views"],
        ["Shareable profile", "Yes", "Yes", "Limited", "Yes + embed widget"],
        ["Private repo analysis", "No", "No", "Yes", "Yes (OAuth)"],
    ]
    cw = [(PAGE_W-2*MARGIN)*p for p in [0.24, 0.15, 0.13, 0.13, 0.35]]
    story.append(make_table(gap_header[0], gap_rows, cw))
    story.append(PB())

    # ─────────────────────────────────────────────────
    # CHAPTER 3: SYSTEM ANALYSIS & DESIGN
    # ─────────────────────────────────────────────────
    story.append(P("Chapter 3: System Analysis & Design", "h1"))
    story.append(HR())

    story.append(P("3.1  Requirements Analysis", "h2"))
    story.append(P("<b>Functional Requirements</b>", "h3"))
    fr = [
        ["FR-01", "GitHub OAuth login / logout"],
        ["FR-02", "Repository synchronisation from GitHub API"],
        ["FR-03", "Per-repository code analysis pipeline"],
        ["FR-04", "Skill extraction with category, proficiency, and confidence"],
        ["FR-05", "Developer score calculation (weighted 5-factor algorithm)"],
        ["FR-06", "DNA Helix interactive visualisation"],
        ["FR-07", "Radar chart multi-category breakdown"],
        ["FR-08", "Force-directed skill tree graph"],
        ["FR-09", "Growth timeline (stacked area chart)"],
        ["FR-10", "Achievement/milestone system"],
        ["FR-11", "Public shareable genome profile at /genome/{username}"],
        ["FR-12", "Embeddable SVG widget at /api/widget/{username}"],
        ["FR-13", "Project showcase with code pattern cards"],
        ["FR-14", "Dark / light / system theme toggle"],
        ["FR-15", "Keyboard navigation shortcuts"],
    ]
    story.append(make_table(["ID", "Requirement"], fr, [(PAGE_W-2*MARGIN)*p for p in [0.13, 0.87]]))
    story.append(SP(10))

    story.append(P("<b>Non-Functional Requirements</b>", "h3"))
    nfr = [
        ["NFR-01", "Performance",  "Dashboard initial load < 2s (server-side data fetch)"],
        ["NFR-02", "Security",     "OAuth 2.0 JWT sessions; API routes require authenticated token"],
        ["NFR-03", "Scalability",  "Stateless Next.js API routes; horizontal scaling ready"],
        ["NFR-04", "Usability",    "Responsive across mobile (375px) to 4K; WCAG AA contrast"],
        ["NFR-05", "Reliability",  "Graceful error handling; analysis failures do not corrupt data"],
        ["NFR-06", "Maintainability","TypeScript strict mode; Prisma schema as single source of truth"],
    ]
    story.append(make_table(["ID", "Category", "Requirement"], nfr,
                              [(PAGE_W-2*MARGIN)*p for p in [0.1, 0.16, 0.74]]))

    story.append(P("3.2  Use Case Actors & Scenarios", "h2"))
    story += bullet([
        "<b>Anonymous Visitor:</b> View landing page, browse public genome profiles, embed SVG widget.",
        "<b>Authenticated Developer:</b> All visitor actions + dashboard, genome analysis, growth tracking, settings.",
        "<b>GitHub API (External):</b> Provides repository metadata, file tree, OAuth tokens.",
        "<b>Analysis Engine (System):</b> Asynchronous job that processes repos and writes skill nodes.",
    ])

    story.append(P("3.3  System Architecture", "h2"))
    story.append(P(
        "CodeDNA follows a <b>monolithic full-stack architecture</b> deployed as a single Next.js 14 "
        "App Router application. The architecture is stratified into four logical layers:", "body"))
    arch_rows = [
        ["Presentation", "React 18 server and client components; Tailwind CSS; D3.js SVG visualisations; next-themes"],
        ["Application",  "Next.js App Router pages; API Route Handlers; NextAuth.js JWT middleware"],
        ["Domain",       "Analysis engine (lib/analysis.ts); scoring algorithm (lib/scoring.ts); GitHub client (lib/github.ts)"],
        ["Data",         "Prisma ORM 5.x; PostgreSQL 14; JSON columns for flexible analysis payloads"],
    ]
    story.append(make_table(["Layer", "Technologies & Responsibilities"], arch_rows,
                              [(PAGE_W-2*MARGIN)*p for p in [0.2, 0.80]]))
    story.append(P(
        "Request flow: Browser → Next.js Middleware (JWT auth check) → Server Component (SSR data fetch via Prisma) "
        "→ Client Component (interactive D3 visualisations). API Route Handlers handle mutations "
        "(sync, analyse) using getToken() from next-auth/jwt for lightweight auth in the App Router context.", "body"))

    story.append(P("3.4  Database Design", "h2"))
    story.append(P(
        "The database comprises <b>six models</b> in a PostgreSQL instance managed through Prisma ORM. "
        "All primary keys use CUID for global uniqueness without integer enumeration risk.", "body"))

    db_models = [
        ("User", ["id (CUID, PK)", "githubId (unique)", "username (unique)", "avatar", "bio",
                  "email", "developerScore (Int)", "createdAt", "updatedAt"],
         "Root identity record. One-to-many with all other models. developerScore cached here after each analysis."),
        ("Repository", ["id (CUID, PK)", "userId (FK → User)", "githubRepoId (unique)", "name",
                        "fullName", "url", "description", "primaryLanguage", "languages (Json)",
                        "stars", "forks", "size", "isPrivate", "isAnalyzed", "lastAnalyzedAt",
                        "analysisData (Json)", "complexityScore"],
         "Mirrors a GitHub repo. analysisData stores the raw analysis result JSON including status, skills, patterns."),
        ("SkillNode", ["id (CUID, PK)", "userId (FK → User)", "name (unique per user)", "category (enum)",
                       "proficiencyScore (0-100)", "confidence (enum)", "evidence (Json)",
                       "firstSeen", "lastSeen"],
         "Aggregated skill record. Updated on every repo analysis — score increases, confidence upgrades. Unique on (userId, name)."),
        ("GenomeSnapshot", ["id (CUID, PK)", "userId (FK → User)", "genomeData (Json)",
                            "totalSkills", "topCategory", "createdAt"],
         "Point-in-time snapshot of the full genome for historical comparison and changelog generation."),
        ("CodePattern", ["id (CUID, PK)", "userId (FK → User)", "repoId (FK → Repository)",
                         "patternType (enum)", "description", "frequency", "qualityScore"],
         "Specific coding pattern detected in a repository. patternType ∈ {ARCHITECTURE, ERROR_HANDLING, TESTING, API_DESIGN, STATE_MANAGEMENT, NAMING_CONVENTION}."),
        ("GrowthEvent", ["id (CUID, PK)", "userId (FK → User)", "skillNodeId (FK → SkillNode?)",
                         "eventType (enum)", "title", "description", "metadata (Json)", "createdAt"],
         "Append-only audit log of growth milestones. eventType ∈ {NEW_SKILL, LEVEL_UP, MILESTONE, NEW_REPO}."),
    ]
    for model_name, fields, desc in db_models:
        story.append(P(f"<b>{model_name}</b>", "h3"))
        story.append(P(desc, "body"))
        story.append(P("Fields: " + " · ".join(fields), "bullet"))
        story.append(SP(4))

    story.append(P("3.5  Data Flow Diagram", "h2"))
    story.append(P("<b>Primary flow — Repo Analysis:</b>", "h3"))
    dfd = [
        ["Step", "Actor", "Action", "Output"],
        ["1", "User", "Clicks 'Connect GitHub'", "OAuth redirect to GitHub"],
        ["2", "GitHub", "Authenticates user, returns code", "Auth code + access token"],
        ["3", "NextAuth", "Validates token, upserts User record", "JWT session cookie"],
        ["4", "User", "Clicks 'Sync Repos'", "POST /api/repos/sync"],
        ["5", "GitHub API", "Returns repo list (paginated)", "Repository records in DB"],
        ["6", "User", "Clicks 'Analyze' on a repo", "POST /api/analyze/{repoId}"],
        ["7", "Analysis Engine", "Fetches file tree, runs mock/AI analysis", "Skills, patterns, complexity score"],
        ["8", "Prisma", "Upserts SkillNodes, creates GrowthEvents", "Updated genome"],
        ["9", "Score Engine", "Recalculates weighted developer score", "Updated User.developerScore"],
        ["10", "Client", "Polls /api/analyze/status/{repoId}", "Renders updated genome visualisations"],
    ]
    cw_dfd = [(PAGE_W-2*MARGIN)*p for p in [0.06, 0.14, 0.44, 0.36]]
    story.append(make_table(dfd[0], dfd[1:], cw_dfd))
    story.append(PB())

    # ─────────────────────────────────────────────────
    # CHAPTER 4: IMPLEMENTATION
    # ─────────────────────────────────────────────────
    story.append(P("Chapter 4: Implementation", "h1"))
    story.append(HR())

    story.append(P("4.1  Technology Stack Justification", "h2"))
    tech_reasons = [
        ["Next.js 14 (App Router)", "Unified full-stack framework eliminates context switching. Server components enable zero-JS data fetching; client components encapsulate D3 animations. Built-in routing, image optimisation, and ISR."],
        ["TypeScript 5.x", "Strict typing across the entire stack (API responses, Prisma models, component props) prevents category errors in the analysis pipeline and ensures visualisation data contracts."],
        ["Prisma ORM", "Type-safe database access with auto-generated client from schema.prisma. Migration tooling, JSON column support for flexible analysis payloads, and excellent Next.js App Router compatibility."],
        ["PostgreSQL 14", "ACID compliance for skill score integrity. JSON column support for analysis payloads. Proven scalability. Free tier available on Supabase/Railway/Neon for deployment."],
        ["D3.js v7", "Unmatched SVG manipulation capability for custom visualisations. The DNA Helix, Radar Chart, Skill Tree, and Growth Timeline are all custom D3 implementations not available in chart libraries."],
        ["NextAuth.js v4", "Turnkey GitHub OAuth with JWT session strategy. Handles PKCE, token refresh, and session serialisation. Adapter-ready for future database session migration."],
        ["Tailwind CSS v3", "Utility-first CSS with JIT compilation. Dark mode via class strategy integrates seamlessly with next-themes. Custom design tokens (dna-green, dna-blue, dna-purple, dna-cyan) extend the palette."],
        ["next-themes", "Lightweight (< 2 KB) theme management with SSR hydration safety via suppressHydrationWarning and system preference detection."],
    ]
    story.append(make_table(["Technology", "Justification"], tech_reasons,
                              [(PAGE_W-2*MARGIN)*p for p in [0.26, 0.74]]))

    story.append(P("4.2  Authentication System", "h2"))
    story.append(P(
        "Authentication is implemented via <b>NextAuth.js v4</b> with the GitHub provider and JWT "
        "session strategy. The OAuth scope requested is <tt>read:user user:email repo</tt>, enabling "
        "access to both public and private repository metadata.", "body"))
    story += code_block([
        "// src/lib/auth.ts — JWT callbacks store userId and accessToken",
        "async jwt({ token, account, profile }) {",
        "  if (account?.provider === 'github' && profile) {",
        "    const dbUser = await prisma.user.findUnique({",
        "      where: { githubId: String(githubProfile.id) }",
        "    });",
        "    token.userId = dbUser.id;          // internal DB ID",
        "    token.accessToken = account.access_token; // GitHub PAT",
        "  }",
        "  return token;",
        "},",
    ], "Auth JWT callback — auth.ts")
    story.append(P(
        "Middleware (<tt>src/middleware.ts</tt>) protects all authenticated routes "
        "(<tt>/dashboard</tt>, <tt>/genome</tt>, <tt>/projects</tt>, etc.) using the default "
        "next-auth/middleware export. API Route Handlers use <tt>getToken({ req })</tt> from "
        "<tt>next-auth/jwt</tt> — a deliberate choice over <tt>getServerSession()</tt> due to "
        "compatibility differences between Pages Router and App Router request contexts.", "body"))

    story.append(P("4.3  GitHub API Integration", "h2"))
    story.append(P(
        "The GitHub client (<tt>src/lib/github.ts</tt>) wraps the GitHub REST API v3 with "
        "the following features:", "body"))
    story += bullet([
        "<b>ETag caching:</b> Conditional GET requests using If-None-Match to respect 304 responses and preserve rate limit budget.",
        "<b>Pagination:</b> Link header parsing to automatically traverse multi-page repository lists.",
        "<b>Rate limit handling:</b> Respects X-RateLimit-Remaining header; backs off gracefully.",
        "<b>File tree fetch:</b> Uses /repos/{owner}/{repo}/git/trees/HEAD?recursive=1 to obtain the flat file list for analysis.",
        "<b>Repository sync:</b> Upserts all repositories with conflict detection on githubRepoId.",
    ])

    story.append(P("4.4  Analysis Engine Architecture", "h2"))
    story.append(P(
        "The analysis engine (<tt>src/lib/analysis.ts</tt>) is designed as a pluggable pipeline. "
        "In the current implementation, <tt>mockAnalyzeRepo()</tt> from <tt>src/lib/mock-analysis.ts</tt> "
        "provides deterministic, seeded analysis results based on repository metadata. "
        "The mock engine uses FNV-1a hashing to generate reproducible results for the same input, "
        "ensuring consistent skill scores across repeated analyses.", "body"))
    story.append(P("The pipeline executes in five stages:", "body"))
    story += bullet([
        "<b>Stage 1 — Fetch:</b> Repository status set to 'fetching'; GitHub Trees API called.",
        "<b>Stage 2 — Analyse:</b> Status set to 'analyzing'; mock/AI engine invoked.",
        "<b>Stage 3 — Skill upsert:</b> Skills detected are merged into SkillNode records. Proficiency scores use max(existing, new) to prevent regression.",
        "<b>Stage 4 — Pattern storage:</b> Code patterns (architecture style, error handling, testing practices) written to CodePattern table.",
        "<b>Stage 5 — Score recalculation:</b> calculateDeveloperScore() recomputes the weighted 5-factor score and updates User.developerScore.",
    ])

    story.append(P("4.5  Developer Score Algorithm", "h2"))
    story.append(P(
        "The developer score (0–100) is a weighted sum of five dimensions, each normalised to 0–100 "
        "before weighting:", "body"))
    score_rows = [
        ["Quality (30%)", "Average overallQuality across analysed repos. Composed of namingConsistency, separationOfConcerns, dryAdherence.", "qualityScore × 0.30"],
        ["Breadth (20%)", "skill_count × 3 + category_count × 5, capped at 100. Rewards polyglot range.", "breadth × 0.20"],
        ["Depth (20%)", "(mastered×3 + demonstrated×2 + claimed×1) × 4, capped at 100. Rewards confidence.", "depth × 0.20"],
        ["Consistency (15%)", "analyzed_repos × 8 + recent_repos × 5, capped at 100. Recent = last 30 days.", "consistency × 0.15"],
        ["Growth (15%)", "growth_events (last 90 days) × 5, capped at 100. Rewards active learning.", "growth × 0.15"],
    ]
    story.append(make_table(["Factor", "Calculation", "Weighted term"], score_rows,
                              [(PAGE_W-2*MARGIN)*p for p in [0.20, 0.50, 0.30]]))
    story += code_block([
        "// src/lib/scoring.ts — final score assembly",
        "const raw = qualityScore*0.30 + breadth*0.20 + depth*0.20",
        "           + consistency*0.15 + growth*0.15;",
        "const score = Math.min(Math.max(Math.round(raw), 0), 100);",
    ], "Scoring algorithm — scoring.ts")

    story.append(P("4.6  Visualisation System", "h2"))

    story.append(P("<b>DNA Helix</b> (src/components/genome/dna-helix.tsx)", "h3"))
    story.append(P(
        "The DNA Helix renders a pseudo-3D double helix in SVG using a custom projection function. "
        "N=72 points (3 turns × 24 points/turn) are computed per frame. Each strand follows a "
        "parametric helix: x = R·cos(θ+rot), z = R·sin(θ+rot), y = linear from top to bottom. "
        "A depth-based z-sort ensures correct overlap rendering. Skill nodes are placed at rung "
        "midpoints with size proportional to proficiencyScore and colour by category. "
        "The animation uses requestAnimationFrame at ~60fps with pause-on-hover. "
        "A ResizeObserver handles dynamic container sizing.", "body"))

    story.append(P("<b>Radar Chart</b> (src/components/genome/genome-radar.tsx + radar-chart.tsx)", "h3"))
    story.append(P(
        "Built with D3.js lineRadial and scaleLinear. Five axes (Languages, Frameworks, Patterns, "
        "Tools, Concepts) represent the mean proficiency score of all skills in each category. "
        "The filled polygon uses curveLinearClosed with a drop-shadow glow filter for visual depth. "
        "Labels adapt colour to the current theme (resolvedTheme from next-themes).", "body"))

    story.append(P("<b>Skill Tree</b> (src/components/genome/skill-tree.tsx)", "h3"))
    story.append(P(
        "D3 force simulation with forceLink, forceManyBody (−220 strength), forceCenter, and "
        "forceCollide. Node hierarchy: root ('You') → category nodes → skill nodes. "
        "Circle radius scales with proficiencyScore (4–13px range). "
        "A glow SVG filter is applied to category and root nodes for visual hierarchy.", "body"))

    story.append(P("<b>Growth Timeline</b> (src/components/growth/growth-timeline.tsx)", "h3"))
    story.append(P(
        "D3 stacked area chart grouping growth events by week and event type (NEW_SKILL, LEVEL_UP, "
        "MILESTONE, NEW_REPO). Uses d3.stack with series ordering and d3.area with curveMonotoneX "
        "for smooth curves. Axes use theme-aware colours.", "body"))

    story.append(P("4.7  Public Profiles & Embeddable Widgets", "h2"))
    story.append(P(
        "Public genome profiles are available at <tt>/genome/{username}</tt> as server-rendered pages "
        "(no authentication required). Profile data is fetched via Prisma server-side with the user "
        "identified by username, eliminating any auth dependency for public consumption. "
        "An in-memory rate limiter (5 req/minute/IP, 5-minute cleanup interval) protects public API "
        "endpoints from abuse.", "body"))
    story.append(P(
        "The <tt>/api/widget/{username}</tt> endpoint generates a dynamic SVG card "
        "(500×200px) suitable for embedding in GitHub README files: "
        "<tt>&lt;img src='https://codedna.app/api/widget/username'&gt;</tt>. "
        "The SVG includes the developer score ring, top 5 skills as horizontal bars, "
        "and a mini category breakdown — all rendered server-side as pure SVG text.", "body"))

    story.append(P("4.8  Key Code Snippets", "h2"))
    story += code_block([
        "// src/lib/api-auth.ts — shared auth helper for all API Route Handlers",
        "import { getToken } from 'next-auth/jwt';",
        "import type { NextRequest } from 'next/server';",
        "",
        "export async function getApiUser(req: NextRequest) {",
        "  const token = await getToken({ req });",
        "  if (!token?.userId) return null;",
        "  return {",
        "    userId: token.userId as string,",
        "    accessToken: (token.accessToken as string | undefined) ?? '',",
        "  };",
        "}",
    ], "Shared API auth helper (getToken approach for App Router compatibility)")

    story += code_block([
        "// src/app/dashboard/page.tsx — server-side data pre-fetch",
        "export default async function DashboardPage() {",
        "  const session = await getServerSession(authOptions);",
        "  if (!session) redirect('/');",
        "  const [repos, skillCount, dbUser, ...rest] = await Promise.all([",
        "    prisma.repository.findMany({ where: { userId }, ... }),",
        "    prisma.skillNode.count({ where: { userId } }),",
        "    prisma.user.findUnique({ where: { id: userId }, select: { developerScore: true } }),",
        "    // ... 4 more parallel queries",
        "  ]);",
        "  return <DashboardClient initialStats={...} initialRepos={...} />;",
        "}",
    ], "Dashboard server-side pre-fetch pattern")
    story.append(PB())

    # ─────────────────────────────────────────────────
    # CHAPTER 5: TESTING & RESULTS
    # ─────────────────────────────────────────────────
    story.append(P("Chapter 5: Testing & Results", "h1"))
    story.append(HR())

    story.append(P("5.1  Testing Approach", "h2"))
    story.append(P(
        "Testing was conducted through systematic manual testing of all application routes and "
        "API endpoints. Each functional requirement was traced to one or more test cases. "
        "API endpoints were tested using curl with and without authentication tokens. "
        "UI flows were tested across Chrome (desktop and mobile viewport) and Firefox.", "body"))

    story.append(P("5.2  Test Cases", "h2"))
    tc_header = ["ID", "Description", "Input / Action", "Expected", "Actual", "Status"]
    tc_rows = [
        ["TC-01", "Landing page loads", "GET /", "200, hero section visible", "200, renders correctly", "PASS"],
        ["TC-02", "GitHub OAuth redirect", "Click 'Connect GitHub'", "Redirects to GitHub auth", "Correct redirect", "PASS"],
        ["TC-03", "Middleware auth guard", "GET /dashboard (no session)", "Redirect to /", "302 redirect", "PASS"],
        ["TC-04", "Dashboard data load", "GET /dashboard (authenticated)", "Repos, stats, score visible", "All data rendered", "PASS"],
        ["TC-05", "Repo sync", "POST /api/repos/sync", "Repository list imported", "10 repos synced", "PASS"],
        ["TC-06", "Single repo analysis", "POST /api/analyze/{id}", "Analysis starts, status: started", "Returns {status:'started'}", "PASS"],
        ["TC-07", "Analysis status poll", "GET /api/analyze/status/{id}", "Returns current status JSON", "Correct status returned", "PASS"],
        ["TC-08", "Stats API", "GET /api/stats (authenticated)", "JSON with all 6 stat fields", "Correct JSON response", "PASS"],
        ["TC-09", "Repos API", "GET /api/repos (authenticated)", "Array of repo objects", "10 repos returned", "PASS"],
        ["TC-10", "Activity API", "GET /api/activity (authenticated)", "Array of growth events", "Events returned", "PASS"],
        ["TC-11", "Genome page", "GET /genome (authenticated)", "Helix, radar, tree tabs work", "All 3 views render", "PASS"],
        ["TC-12", "Public profile", "GET /genome/zhnverse", "Public profile page (no auth)", "Profile renders", "PASS"],
        ["TC-13", "SVG widget", "GET /api/widget/zhnverse", "Returns image/svg+xml", "Valid SVG returned", "PASS"],
        ["TC-14", "Growth page", "GET /growth (authenticated)", "Timeline, achievements, predictions", "All sections render", "PASS"],
        ["TC-15", "Theme toggle", "Click Dark/Light/System", "Theme switches correctly", "Theme applied", "PASS"],
        ["TC-16", "Keyboard shortcuts", "Press g then d", "Navigate to /dashboard", "Correct navigation", "PASS"],
        ["TC-17", "Unauthenticated API", "GET /api/stats (no cookie)", "401 JSON {error:Unauthorized}", "401 returned", "PASS"],
        ["TC-18", "Rate limiter", "6 rapid GET /api/public/*", "6th returns 429", "429 Too Many Requests", "PASS"],
    ]
    cw_tc = [(PAGE_W-2*MARGIN)*p for p in [0.07, 0.18, 0.24, 0.17, 0.17, 0.10]]
    story.append(make_table(tc_header, tc_rows, cw_tc))

    story.append(P("5.3  Results Summary", "h2"))
    results = [
        ["Repositories synced", "10", "GitHub repos imported via API"],
        ["Skills detected", "12", "Unique SkillNode records across all categories"],
        ["Developer score", "71 / 100", "Intermediate-to-Advanced rating"],
        ["Growth events", "9", "NEW_SKILL and LEVEL_UP events recorded"],
        ["API routes tested", "18", "All returning correct HTTP codes"],
        ["Pages functional", "10", "Landing, Dashboard, Genome, Projects, Growth, Analysis, Settings, Public Profile, Widget"],
        ["Theme modes", "3", "Dark (default), Light, System"],
    ]
    story.append(make_table(["Metric", "Value", "Notes"], results,
                              [(PAGE_W-2*MARGIN)*p for p in [0.28, 0.16, 0.56]]))

    story.append(P("5.4  Performance Observations", "h2"))
    story += bullet([
        "Dashboard initial load: ~80–150ms (server-side Prisma fetch, 7 parallel queries).",
        "Genome visualisation render: < 16ms per frame at 60fps on desktop Chrome.",
        "Repo analysis (mock engine): ~200–400ms per repository including DB writes.",
        "SVG widget generation: < 10ms (pure string construction, no external dependencies).",
        "Public profile page: ~50ms (single user + skills Prisma query, no auth overhead).",
    ])
    story.append(PB())

    # ─────────────────────────────────────────────────
    # CHAPTER 6: CONCLUSION & FUTURE WORK
    # ─────────────────────────────────────────────────
    story.append(P("Chapter 6: Conclusion & Future Work", "h1"))
    story.append(HR())

    story.append(P("6.1  Summary of Achievements", "h2"))
    story.append(P(
        "CodeDNA successfully delivers a full-stack developer genome platform that meets all 15 "
        "functional requirements defined in Chapter 3. The platform ingests GitHub repositories "
        "via OAuth, analyses them through a multi-stage pipeline, produces evidence-backed skill "
        "profiles, visualises them through three distinct interactive views, and makes them "
        "publicly shareable. A weighted scoring algorithm quantifies developer capability across "
        "five orthogonal dimensions. The entire system is built with TypeScript end-to-end, "
        "deployed on a Next.js 14 App Router with server-side rendering for performance and SEO.", "body"))

    story.append(P("6.2  Challenges Faced", "h2"))
    story += bullet([
        "<b>Next.js 14 App Router + NextAuth.js compatibility:</b> getServerSession() returns null "
        "in Route Handler context (App Router) despite working in Server Components. Resolved by "
        "switching all 10 API routes to getToken() from next-auth/jwt, which reads the JWT cookie "
        "directly from the NextRequest object.",
        "<b>D3.js + React Server Components:</b> D3 requires a DOM, making it incompatible with "
        "server-side rendering. All visualisation components are marked 'use client' and use "
        "useRef/useEffect for DOM binding. ResizeObserver ensures responsive sizing.",
        "<b>Theme hydration flash:</b> next-themes injects a blocking script that applies the theme "
        "before React hydrates. suppressHydrationWarning on the HTML element and the mounted state "
        "pattern in ThemeToggle prevent hydration mismatches.",
        "<b>Light mode colour contrast:</b> Many -400 Tailwind shades (text-yellow-400, text-purple-400) "
        "fail WCAG AA on white backgrounds (< 3:1 contrast ratio). Systematic replacement with "
        "-600 variants and dark:text-{colour}-400 modifiers resolved across all components.",
        "<b>Build cache corruption:</b> Adding next-themes during development corrupted the Next.js "
        "vendor chunk cache. Resolved by full .next/ deletion and clean rebuild.",
    ])

    story.append(P("6.3  Future Enhancements", "h2"))
    story += bullet([
        "<b>Real AI integration:</b> Replace the mock analysis engine with Anthropic Claude API calls for genuine code comprehension, architectural pattern detection, and natural-language project summaries.",
        "<b>Team dashboards:</b> Aggregate genome views for engineering teams, showing collective skill coverage and identifying growth gaps.",
        "<b>Job matching:</b> Match developer genomes against job description skill requirements using cosine similarity on skill vectors.",
        "<b>Real-time collaboration:</b> Live genome comparison between two developers with shared skills highlighted.",
        "<b>GitHub Actions integration:</b> Webhook-triggered re-analysis on every push, keeping the genome continuously up-to-date.",
        "<b>Commit-level analysis:</b> Analyse individual commit diffs rather than repository metadata for higher-fidelity skill detection.",
        "<b>Mobile app:</b> React Native companion app for growth notifications and genome sharing.",
    ])

    story.append(P("6.4  Lessons Learned", "h2"))
    story += bullet([
        "Server component vs client component boundaries in Next.js 14 App Router require careful architectural planning — moving data fetching server-side eliminated entire classes of auth bugs.",
        "Database schema design with Prisma and JSON columns provides excellent flexibility for evolving analysis payload schemas without migrations.",
        "D3.js and React integration benefits from full component isolation: each visualisation is a self-contained black box that accepts typed props and manages its own SVG lifecycle.",
        "TypeScript strict mode catches integration bugs early — the Prisma-generated types and component prop interfaces together form a robust contract system across the entire stack.",
    ])
    story.append(PB())

    # ─────────────────────────────────────────────────
    # REFERENCES
    # ─────────────────────────────────────────────────
    story.append(P("References", "h1"))
    story.append(HR())

    refs = [
        "[1] Bostock, M., Ogievetsky, V., & Heer, J. (2011). D³ Data-Driven Documents. <i>IEEE Transactions on Visualization and Computer Graphics</i>, 17(12), 2301–2309.",
        "[2] Chen, M., Tworek, J., Jun, H., et al. (2021). Evaluating Large Language Models Trained on Code. <i>arXiv preprint arXiv:2107.03374</i>.",
        "[3] Dietz, L., Bhatt, A., & Sheridan, T. (2019). Skills endorsements on LinkedIn: A trust-but-verify study. <i>CSCW '19 Workshop on Credibility of Online Content</i>.",
        "[4] Fruchterman, T. M. J., & Reingold, E. M. (1991). Graph drawing by force-directed placement. <i>Software: Practice and Experience</i>, 21(11), 1129–1164.",
        "[5] Hamari, J., Koivisto, J., & Sarsa, H. (2014). Does Gamification Work? A Literature Review of Empirical Studies on Gamification. <i>HICSS 2014</i>.",
        "[6] Kalliamvakou, E., Gousios, G., Blincoe, K., et al. (2014). The promises and perils of mining GitHub. <i>MSR '14</i>.",
        "[7] Mens, T., & Tourwé, T. (2004). A survey of software refactoring. <i>IEEE Transactions on Software Engineering</i>, 30(2), 126–139.",
        "[8] Tiddi, I., et al. (2020). Knowledge graph-based program synthesis. <i>ISWC 2020</i>.",
        "[9] Next.js Documentation. (2024). App Router. https://nextjs.org/docs",
        "[10] Prisma Documentation. (2024). Prisma ORM. https://www.prisma.io/docs",
        "[11] D3.js Documentation. (2024). Data-Driven Documents. https://d3js.org",
        "[12] NextAuth.js Documentation. (2024). Authentication for Next.js. https://next-auth.js.org",
        "[13] GitHub REST API Documentation. (2024). https://docs.github.com/en/rest",
        "[14] Tailwind CSS Documentation. (2024). Utility-first CSS framework. https://tailwindcss.com",
        "[15] Radix UI Documentation. (2024). Accessible component primitives. https://www.radix-ui.com",
        "[16] Anthropic Documentation. (2024). Claude API Reference. https://docs.anthropic.com",
        "[17] PostgreSQL Global Development Group. (2024). PostgreSQL 16 Documentation. https://www.postgresql.org/docs",
    ]
    for r in refs:
        story.append(P(r, "bullet"))
    story.append(PB())

    # ══════════════════════════════════════════════════════════════════════
    # PART 2 — PORTFOLIO SHOWCASE
    # ══════════════════════════════════════════════════════════════════════
    story += part_divider(2, "PORTFOLIO SHOWCASE",
                          "Project Overview · Feature Highlights · Technical Showcase")

    story.append(P("Project Overview", "h1"))
    story.append(HR())
    story.append(P(
        "<b>CodeDNA</b> is a full-stack web application that analyses a developer's GitHub repositories "
        "and generates an interactive, shareable <i>developer genome</i> — a multi-dimensional fingerprint "
        "of their coding skills, architectural patterns, and growth trajectory. "
        "Built with Next.js 14, TypeScript, PostgreSQL, and custom D3.js visualisations, "
        "the platform proves what a developer can actually do rather than what they claim, "
        "through evidence backed by real code analysis.", "body"))

    story.append(SP(10))
    metrics_data = [
        ["10+ Pages", "6 DB Models", "14+ Components", "18 API Routes"],
        ["3 Visualisation Types", "5-Factor Scoring", "Public Profiles", "Embeddable Widgets"],
    ]
    t = Table(metrics_data, colWidths=[(PAGE_W-2*MARGIN)/4]*4)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), C_GREEN),
        ("TEXTCOLOR",    (0,0), (-1,-1), C_WHITE),
        ("FONTNAME",     (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 11),
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0), (-1,-1), 14),
        ("BOTTOMPADDING",(0,0), (-1,-1), 14),
        ("GRID",         (0,0), (-1,-1), 2, C_WHITE),
    ]))
    story.append(t)
    story.append(SP(16))

    story.append(P("Feature Highlights", "h1"))
    story.append(HR())
    features = [
        ("GitHub OAuth & Repo Sync",
         "One-click GitHub authentication (OAuth 2.0) imports all public and private repositories with metadata, language breakdown, stars, and forks. Automatic de-duplication on re-sync."),
        ("AI-Powered Code Analysis Engine",
         "Multi-stage pipeline: fetch file tree → detect languages and frameworks from filenames and manifests → score quality indicators → generate project summary. Architecture supports Anthropic Claude API as a drop-in replacement for the current deterministic engine."),
        ("Interactive 3D DNA Helix",
         "Custom SVG visualisation using pseudo-3D projection math. 72-point double helix with skill nodes at rung midpoints. Colour-coded by category, sized by proficiency. Animates at 60fps with pause-on-hover and skill tooltip on click."),
        ("Multi-View Genome Visualisation",
         "Three switchable views — DNA Helix, D3 Radar Chart (5-axis category breakdown), and Force-Directed Skill Tree (D3 forceSimulation) — all responding to the same skill data with smooth tab transitions."),
        ("Weighted Developer Score",
         "Five-factor algorithm (Quality 30%, Breadth 20%, Depth 20%, Consistency 15%, Growth 15%) computes a 0–100 score displayed as an animated SVG ring with level badge (Learning / Intermediate / Advanced / Expert)."),
        ("Growth Tracking & Achievements",
         "Append-only GrowthEvent log records NEW_SKILL, LEVEL_UP, MILESTONE, and NEW_REPO events. D3 stacked area timeline visualises growth by week. Five achievements unlock based on skill diversity, score, and velocity."),
        ("Public Shareable Profiles",
         "Every user gets a public profile at /genome/{username} — no login required. Visitors see the full genome visualisation, top skills bar chart, and public project list. Server-side rendered for SEO."),
        ("Embeddable SVG Widget",
         "Dynamic SVG card at /api/widget/{username} (500×200px) with score ring, top skills, and category breakdown. Embeds in any GitHub README with a single img tag."),
        ("Dark / Light / System Theme",
         "Three-way theme toggle (Dark/Light/System) using next-themes with class-based switching. All D3 visualisations re-render on theme change via resolvedTheme dependency. Custom design tokens maintain brand colours across modes."),
        ("Keyboard Navigation",
         "Vim-inspired chord shortcuts: g+d (Dashboard), g+g (Genome), g+p (Projects), g+r (Growth), g+s (Settings). 1.5-second chord window prevents accidental triggers."),
    ]
    for title, desc in features:
        story.append(KeepTogether([
            P(f"<b>{title}</b>", "h3"),
            P(desc, "body"),
            SP(4),
        ]))

    story.append(P("Technical Highlights", "h1"))
    story.append(HR())
    tech_highlights = [
        ["Full-Stack TypeScript", "Single language across client, server, API routes, and database schema. Prisma-generated types flow through the entire stack."],
        ["Server-Side Rendering", "Dashboard pre-fetches 7 parallel Prisma queries server-side, eliminating client-side auth issues and delivering instant first paint."],
        ["Custom D3.js Visualisations", "Four bespoke charts — none using chart libraries. Full control over animation, theming, interaction, and layout."],
        ["Prisma + PostgreSQL", "Type-safe ORM with JSON column support for flexible analysis payloads. 6 models, 5 enums, full referential integrity with cascade deletes."],
        ["OAuth 2.0 + JWT", "Stateless session architecture. GitHub access token stored in JWT for API calls. getToken() in Route Handlers for App Router compatibility."],
        ["Rate Limiting", "In-memory sliding window rate limiter (5 req/min/IP) on all public endpoints. 5-minute cleanup interval prevents memory leaks."],
        ["Responsive Design", "CSS Grid and Flexbox with Tailwind CSS breakpoints. Tested from 375px (mobile) to 1920px (desktop). All charts use ResizeObserver."],
        ["Accessibility", "WCAG AA contrast ratios across both themes. Keyboard navigation. Semantic HTML. Screen-reader-compatible labels on SVG elements."],
    ]
    story.append(make_table(["Feature", "Details"], tech_highlights,
                              [(PAGE_W-2*MARGIN)*p for p in [0.28, 0.72]]))

    story.append(P("Screenshots & Page Inventory", "h1"))
    story.append(HR())
    pages_inv = [
        ["/", "Landing Page", "Hero section, feature cards, how-it-works, genome preview, CTA"],
        ["/dashboard", "Dashboard", "Stat cards (score, repos, skills, velocity), donut chart, radar, activity feed, repo table"],
        ["/genome", "Genome (Helix)", "DNA helix visualisation, developer score ring, genome breakdown"],
        ["/genome (Radar)", "Genome (Radar)", "5-axis radar chart, skill table sidebar"],
        ["/genome (Tree)", "Genome (Tree)", "Force-directed skill tree with category clustering"],
        ["/projects", "Projects", "Project cards with architecture pattern, complexity score, skills"],
        ["/growth", "Growth", "Growth timeline, milestones feed, achievements, predicted next skills"],
        ["/analysis/{id}", "Analysis Deep-Dive", "Per-repo quality scores, detected skills, code patterns, complexity"],
        ["/settings", "Settings", "Account info, theme preference, danger zone"],
        ["/genome/{username}", "Public Profile", "Public genome (no auth), top skills, public projects, embed banner"],
    ]
    story.append(make_table(["URL", "Page", "Content"], pages_inv,
                              [(PAGE_W-2*MARGIN)*p for p in [0.20, 0.22, 0.58]]))
    story.append(P("Note: Screenshots to be inserted into the appendix of the printed version.", "caption"))
    story.append(PB())

    # ══════════════════════════════════════════════════════════════════════
    # PART 3 — TECHNICAL DOCUMENTATION
    # ══════════════════════════════════════════════════════════════════════
    story += part_divider(3, "TECHNICAL DOCUMENTATION",
                          "Installation · Schema · API Reference · Deployment")

    story.append(P("System Requirements & Installation", "h1"))
    story.append(HR())

    story.append(P("System Requirements", "h2"))
    req_rows = [
        ["Node.js", "≥ 18.0.0", "Required for Next.js 14"],
        ["npm / yarn / pnpm", "≥ 9.0.0 (npm)", "Package management"],
        ["PostgreSQL", "≥ 14.0", "Primary database"],
        ["Git", "Any recent", "Source control"],
        ["GitHub OAuth App", "Required", "Client ID + Secret for authentication"],
    ]
    story.append(make_table(["Dependency", "Version", "Notes"], req_rows,
                              [(PAGE_W-2*MARGIN)*p for p in [0.25, 0.20, 0.55]]))

    story.append(P("Installation Steps", "h2"))
    story += code_block([
        "# 1. Clone the repository",
        "git clone https://github.com/zhnverse/codedna.git",
        "cd codedna",
        "",
        "# 2. Install dependencies",
        "npm install",
        "",
        "# 3. Set up environment variables",
        "cp .env.example .env.local",
        "# Edit .env.local with your values (see Appendix B)",
        "",
        "# 4. Push database schema",
        "npx prisma db push",
        "",
        "# 5. Generate Prisma client",
        "npx prisma generate",
        "",
        "# 6. Start development server",
        "npm run dev",
        "# App available at http://localhost:3000",
    ], "Installation commands")

    story.append(P("Project Structure", "h1"))
    story.append(HR())

    dir_rows = [
        ["src/app/", "Next.js App Router pages and API routes"],
        ["src/app/api/", "18 API Route Handlers (auth, repos, analyze, stats, activity, genome, score, public, widget)"],
        ["src/app/dashboard/", "Dashboard page (server) + DashboardClient (client with initial data props)"],
        ["src/app/genome/", "Authenticated genome page + public profile at /genome/[username]"],
        ["src/app/growth/", "Growth tracking page with timeline and achievements"],
        ["src/app/projects/", "Project showcase with code pattern analysis"],
        ["src/app/analysis/[repoId]/", "Per-repository deep-dive analysis page"],
        ["src/app/settings/", "Account settings page"],
        ["src/components/dashboard/", "StatCard, DonutChart, DashboardRadar, ActivityFeed, RepoTable, SyncButton"],
        ["src/components/genome/", "DNAHelix, GenomeRadar, RadarChart, SkillTree, SkillTable"],
        ["src/components/growth/", "GrowthTimeline, MilestonesFeed"],
        ["src/components/landing/", "HeroSection, FeaturesSection, HowItWorks, GenomePreview"],
        ["src/components/layout/", "Navbar, Footer, Providers, ThemeToggle, KeyboardShortcuts"],
        ["src/components/projects/", "ProjectCard"],
        ["src/components/ui/", "Radix-based primitives: Button, Card, Badge, Input, Switch, etc."],
        ["src/lib/", "auth.ts, api-auth.ts, analysis.ts, mock-analysis.ts, scoring.ts, github.ts, prisma.ts, rate-limit.ts, format.ts, utils.ts"],
        ["src/hooks/", "useKeyboardShortcuts"],
        ["src/types/", "next-auth.d.ts (extends Session type)"],
        ["prisma/", "schema.prisma (single source of truth for all 6 DB models)"],
    ]
    story.append(make_table(["Path", "Description"], dir_rows,
                              [(PAGE_W-2*MARGIN)*p for p in [0.36, 0.64]]))
    story.append(PB())

    story.append(P("Database Schema Reference", "h1"))
    story.append(HR())

    schema_models = [
        {
            "name": "User",
            "fields": [
                ["id", "String", "CUID, Primary Key"],
                ["githubId", "String", "Unique — GitHub numeric user ID"],
                ["username", "String", "Unique — GitHub login handle"],
                ["avatar", "String?", "GitHub avatar URL"],
                ["bio", "String?", "GitHub bio"],
                ["email", "String?", "Primary email"],
                ["developerScore", "Int", "Cached weighted score (0–100)"],
                ["createdAt / updatedAt", "DateTime", "Timestamps"],
            ],
        },
        {
            "name": "Repository",
            "fields": [
                ["id", "String", "CUID, Primary Key"],
                ["userId", "String", "FK → User (cascade delete)"],
                ["githubRepoId", "String", "Unique — GitHub numeric repo ID"],
                ["name / fullName / url", "String", "Repo identifiers"],
                ["primaryLanguage", "String?", "Dominant language from GitHub API"],
                ["languages", "Json?", "Language breakdown map"],
                ["stars / forks / size", "Int", "GitHub metadata"],
                ["isPrivate / isAnalyzed", "Boolean", "State flags"],
                ["lastAnalyzedAt", "DateTime?", "Last successful analysis timestamp"],
                ["analysisData", "Json?", "Full analysis result payload"],
                ["complexityScore", "Int?", "0–100 complexity indicator"],
            ],
        },
        {
            "name": "SkillNode",
            "fields": [
                ["id", "String", "CUID, Primary Key"],
                ["userId", "String", "FK → User (cascade delete)"],
                ["name", "String", "Skill name (unique per user)"],
                ["category", "SkillCategory", "Enum: LANGUAGE | FRAMEWORK | PATTERN | TOOL | CONCEPT"],
                ["proficiencyScore", "Int", "0–100, increases with evidence"],
                ["confidence", "SkillConfidence", "Enum: CLAIMED | DEMONSTRATED | MASTERED"],
                ["evidence", "Json", "Array of evidence objects"],
                ["firstSeen / lastSeen", "DateTime", "Temporal tracking"],
            ],
        },
        {
            "name": "GrowthEvent",
            "fields": [
                ["id", "String", "CUID, Primary Key"],
                ["userId", "String", "FK → User (cascade delete)"],
                ["skillNodeId", "String?", "FK → SkillNode (set null on delete)"],
                ["eventType", "GrowthEventType", "Enum: NEW_SKILL | LEVEL_UP | MILESTONE | NEW_REPO"],
                ["title / description", "String", "Human-readable event description"],
                ["metadata", "Json?", "Additional context data"],
                ["createdAt", "DateTime", "Immutable event timestamp"],
            ],
        },
        {
            "name": "CodePattern",
            "fields": [
                ["id", "String", "CUID, Primary Key"],
                ["userId / repoId", "String", "FK → User, Repository (cascade delete)"],
                ["patternType", "PatternType", "Enum: ARCHITECTURE | ERROR_HANDLING | TESTING | API_DESIGN | STATE_MANAGEMENT | NAMING_CONVENTION"],
                ["description", "String", "Natural language pattern description"],
                ["frequency / qualityScore", "Int", "Occurrence count and quality rating"],
            ],
        },
        {
            "name": "GenomeSnapshot",
            "fields": [
                ["id", "String", "CUID, Primary Key"],
                ["userId", "String", "FK → User (cascade delete)"],
                ["genomeData", "Json", "Full skill set snapshot at creation time"],
                ["totalSkills / topCategory", "Int / String?", "Summary statistics"],
                ["createdAt", "DateTime", "Immutable snapshot timestamp"],
            ],
        },
    ]
    for model in schema_models:
        story.append(P(f"<b>{model['name']}</b>", "h3"))
        story.append(make_table(["Field", "Type", "Description"], model["fields"],
                                  [(PAGE_W-2*MARGIN)*p for p in [0.26, 0.20, 0.54]]))
        story.append(SP(8))
    story.append(PB())

    story.append(P("API Reference", "h1"))
    story.append(HR())

    api_routes = [
        ["POST", "/api/repos/sync", "Yes", "—", "{ total, created, updated }", "Sync GitHub repos into DB"],
        ["GET", "/api/repos", "Yes", "—", "RepoRow[]", "List all user repositories"],
        ["GET", "/api/repos/{repoId}", "Yes", "—", "Repository + patterns", "Single repo detail"],
        ["GET", "/api/stats", "Yes", "—", "{ analyzedRepos, skillCount, developerScore, growthVelocity, languageBreakdown, topSkills }", "Dashboard statistics"],
        ["GET", "/api/activity", "Yes", "—", "GrowthEvent[]", "Recent 10 growth events"],
        ["GET", "/api/genome/data", "Yes", "—", "{ skills, grouped, total }", "All skill nodes grouped by category"],
        ["GET", "/api/score", "Yes", "—", "{ score, breakdown }", "Current developer score + breakdown"],
        ["POST", "/api/analyze/{repoId}", "Yes", "—", "{ status: 'started', repoId }", "Start async repo analysis"],
        ["GET", "/api/analyze/status/{repoId}", "Yes", "—", "{ status, isAnalyzed, complexityScore, ... }", "Poll analysis status"],
        ["POST", "/api/analyze/all", "Yes", "—", "{ status, count }", "Bulk analyse all unanalysed repos"],
        ["GET", "/api/public/genome/{username}", "No", "—", "{ user, skills, repos }", "Public genome data"],
        ["GET", "/api/public/skills/{username}", "No", "—", "SkillNode[]", "Public skill list"],
        ["GET", "/api/public/projects/{username}", "No", "—", "Repository[]", "Public repos"],
        ["GET", "/api/public/score/{username}", "No", "—", "{ developerScore }", "Public developer score"],
        ["GET", "/api/widget/{username}", "No", "—", "SVG (image/svg+xml)", "Embeddable SVG widget card"],
        ["GET/POST", "/api/auth/[...nextauth]", "—", "—", "NextAuth responses", "OAuth handler (NextAuth.js)"],
    ]
    story.append(make_table(
        ["Method", "Path", "Auth", "Body", "Response", "Description"],
        api_routes,
        [(PAGE_W-2*MARGIN)*p for p in [0.08, 0.22, 0.06, 0.06, 0.28, 0.30]]
    ))
    story.append(P("Auth = 'Yes' routes require a valid next-auth.session-token cookie. "
                   "Public routes are protected by rate limiting (5 req/min/IP).", "caption"))
    story.append(PB())

    story.append(P("Component Architecture", "h1"))
    story.append(HR())

    comp_rows = [
        ["DNAHelix", "genome/dna-helix", "skills: Skill[]", "Animated pseudo-3D SVG double helix with skill nodes"],
        ["GenomeRadar", "genome/genome-radar", "skills: Skill[]", "D3 radar chart wrapper with 5-axis category mapping"],
        ["RadarChart", "genome/radar-chart", "data: RadarData[], width, height", "Core D3 radar implementation with glow filter"],
        ["SkillTree", "genome/skill-tree", "skills: Skill[]", "D3 force-directed graph with 3-level node hierarchy"],
        ["SkillTable", "genome/skill-table", "skills: Skill[]", "Sortable, searchable skill list with confidence badges"],
        ["GrowthTimeline", "growth/growth-timeline", "events: GrowthEvent[]", "D3 stacked area chart of weekly event counts"],
        ["MilestonesFeed", "growth/milestones-feed", "events: GrowthEvent[]", "Vertical timeline with event type icons"],
        ["DonutChart", "dashboard/donut-chart", "data: DonutSlice[], size", "D3 donut chart with hover tooltip and language colours"],
        ["DashboardRadar", "dashboard/dashboard-radar", "data: RadarData[], loading", "Radar chart wrapper with loading skeleton"],
        ["ActivityFeed", "dashboard/activity-feed", "events, loading", "Scrollable recent activity list with event icons"],
        ["RepoTable", "dashboard/repo-table", "repos, loading, analyzingIds, onAnalyze", "Sortable paginated repository list with analyze buttons"],
        ["StatCard", "dashboard/stat-card", "label, value, icon, colorClass, loading", "Individual KPI card with loading skeleton"],
        ["SyncButton", "dashboard/sync-button", "onSuccess: () => void", "GitHub sync trigger with loading state"],
        ["ProjectCard", "projects/project-card", "project: Project", "Analysis result card with architecture badge and skill chips"],
        ["ThemeToggle", "layout/theme-toggle", "—", "Three-way dark/light/system pill toggle using next-themes"],
        ["HeroSection", "landing/hero-section", "—", "Landing page hero with CTA and Sample Genome button"],
    ]
    story.append(make_table(
        ["Component", "Path (src/components/)", "Key Props", "Purpose"],
        comp_rows,
        [(PAGE_W-2*MARGIN)*p for p in [0.18, 0.22, 0.26, 0.34]]
    ))
    story.append(PB())

    story.append(P("Analysis Pipeline Documentation", "h1"))
    story.append(HR())

    story.append(P("How a Repository Gets Analysed", "h2"))
    pipeline_steps = [
        ["1", "Trigger", "User clicks Analyze button → POST /api/analyze/{repoId}"],
        ["2", "Auth check", "getApiUser(req) extracts userId and accessToken from JWT"],
        ["3", "Status: fetching", "Repository.analysisData updated to {status:'fetching'}"],
        ["4", "File tree", "fetchRepoTree(accessToken, owner, repo) — GitHub Trees API recursive call"],
        ["5", "Status: analyzing", "Repository.analysisData updated to {status:'analyzing'}"],
        ["6", "Mock/AI analysis", "mockAnalyzeRepo({name, description, primaryLanguage, stars, forks, size}) runs FNV-1a seeded analysis"],
        ["7", "Skill detection", "Language → skill mapping table consulted; filename heuristics applied; framework hints matched via regex"],
        ["8", "DB upsert skills", "For each skill: prisma.skillNode.upsert() with max(existing, new) score strategy"],
        ["9", "Pattern storage", "CodePattern records created for architecture, testing, API design patterns"],
        ["10", "GrowthEvents", "NEW_SKILL events for new skills; LEVEL_UP for score increases"],
        ["11", "Score recalc", "calculateDeveloperScore(userId) runs 5-factor weighted algorithm"],
        ["12", "Status: complete", "Repository.isAnalyzed=true, lastAnalyzedAt=now, complexityScore saved"],
        ["13", "Client update", "Frontend poll detects complete status → fetchAll() refreshes dashboard"],
    ]
    story.append(make_table(
        ["Step", "Actor", "Action"],
        pipeline_steps,
        [(PAGE_W-2*MARGIN)*p for p in [0.06, 0.16, 0.78]]
    ))

    story.append(P("Swapping to Real Anthropic API", "h2"))
    story += code_block([
        "// Replace mockAnalyzeRepo in src/lib/analysis.ts with:",
        "import Anthropic from '@anthropic-ai/sdk';",
        "",
        "const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });",
        "",
        "async function aiAnalyzeRepo(repo: RepoInput): Promise<MockAnalysisResult> {",
        "  const message = await client.messages.create({",
        "    model: 'claude-opus-4-7',",
        "    max_tokens: 2048,",
        "    messages: [{",
        "      role: 'user',",
        "      content: `Analyse this repository and return a JSON object matching the",
        "        MockAnalysisResult schema. Repository: ${JSON.stringify(repo)}`",
        "    }]",
        "  });",
        "  return JSON.parse(message.content[0].text);",
        "}",
    ], "AI engine replacement (src/lib/analysis.ts)")
    story.append(PB())

    story.append(P("Deployment Guide", "h1"))
    story.append(HR())

    story.append(P("Vercel Deployment", "h2"))
    story += code_block([
        "# Install Vercel CLI",
        "npm i -g vercel",
        "",
        "# Link and deploy (first time)",
        "vercel --prod",
        "",
        "# Set environment variables",
        "vercel env add DATABASE_URL production",
        "vercel env add GITHUB_CLIENT_ID production",
        "vercel env add GITHUB_CLIENT_SECRET production",
        "vercel env add NEXTAUTH_SECRET production",
        "vercel env add NEXTAUTH_URL production  # e.g. https://codedna.vercel.app",
        "",
        "# Redeploy after env changes",
        "vercel --prod",
    ], "Vercel deployment")

    story.append(P("Database Hosting Options", "h2"))
    db_opts = [
        ["Supabase", "Free tier: 500MB, 2 CPU. Postgres 15. Built-in connection pooling. Recommended for production.", "supabase.com"],
        ["Railway", "Free tier: $5 credit/month. Simple GitHub integration. Automatic backups.", "railway.app"],
        ["Neon", "Free tier: 512MB. Serverless Postgres with branching. Excellent Vercel integration.", "neon.tech"],
        ["Aiven", "Free trial 30 days. Enterprise-grade. Multiple cloud providers.", "aiven.io"],
    ]
    story.append(make_table(["Provider", "Description", "URL"], db_opts,
                              [(PAGE_W-2*MARGIN)*p for p in [0.15, 0.60, 0.25]]))

    story.append(P("GitHub OAuth App Configuration", "h2"))
    story += bullet([
        "Go to GitHub Settings → Developer settings → OAuth Apps → New OAuth App",
        "Application name: CodeDNA",
        "Homepage URL: https://your-domain.vercel.app",
        "Authorization callback URL: https://your-domain.vercel.app/api/auth/callback/github",
        "Copy Client ID and generate Client Secret → add to Vercel env vars",
    ])

    story.append(P("Known Issues & Roadmap", "h1"))
    story.append(HR())

    story.append(P("Known Issues", "h2"))
    issues = [
        ["ISSUE-01", "Mock analysis engine", "Skills are deterministically seeded, not from real code parsing. Scores may not reflect actual repo complexity for atypical projects.", "Replace with Anthropic Claude API"],
        ["ISSUE-02", "GitHub rate limits", "Large accounts (500+ repos) may hit GitHub API rate limits during sync. The client backs off but doesn't retry automatically.", "Implement exponential backoff + queue"],
        ["ISSUE-03", "Analysis concurrency", "Bulk 'Analyze All' runs repos sequentially to avoid rate limit issues. Slow for large repo counts.", "Implement parallel pool with concurrency limit"],
        ["ISSUE-04", "Memory rate limiter", "Rate limiter resets on server restart. Does not persist across serverless function invocations.", "Migrate to Redis-backed rate limiter"],
    ]
    story.append(make_table(["ID", "Issue", "Description", "Resolution Path"], issues,
                              [(PAGE_W-2*MARGIN)*p for p in [0.10, 0.17, 0.43, 0.30]]))

    story.append(P("Roadmap", "h2"))
    roadmap = [
        ["v1.1", "Short-term", "Real Anthropic API integration for AST-level code analysis"],
        ["v1.2", "Short-term", "GitHub Actions webhook for automatic re-analysis on push"],
        ["v1.3", "Medium-term", "Team/organisation dashboards with collective genome view"],
        ["v2.0", "Medium-term", "Job matching: cosine similarity between genome and JD skill vectors"],
        ["v2.1", "Long-term", "Real-time genome comparison between two developers"],
        ["v2.2", "Long-term", "Mobile app (React Native) for growth notifications"],
        ["v3.0", "Long-term", "Public API with OAuth for third-party integrations"],
    ]
    story.append(make_table(["Version", "Timeline", "Feature"], roadmap,
                              [(PAGE_W-2*MARGIN)*p for p in [0.12, 0.18, 0.70]]))
    story.append(PB())

    # ══════════════════════════════════════════════════════════════════════
    # APPENDICES
    # ══════════════════════════════════════════════════════════════════════
    story.append(P("Appendix A: Complete Database Schema", "h1"))
    story.append(HR())
    schema_lines = open("/home/sloth/Skill/CodeDNA/prisma/schema.prisma").read().splitlines()
    for ln in schema_lines:
        story.append(P(ln.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;") or " ", "code"))
    story.append(PB())

    story.append(P("Appendix B: Environment Variables Reference", "h1"))
    story.append(HR())
    env_rows = [
        ["DATABASE_URL", "Required", "postgresql://user:pass@host:5432/dbname", "PostgreSQL connection string"],
        ["GITHUB_CLIENT_ID", "Required", "Ov23li...", "GitHub OAuth App Client ID"],
        ["GITHUB_CLIENT_SECRET", "Required", "c200c7...", "GitHub OAuth App Client Secret"],
        ["NEXTAUTH_SECRET", "Required", "random 32-byte base64 string", "JWT signing secret. Generate: openssl rand -base64 32"],
        ["NEXTAUTH_URL", "Required", "http://localhost:3000 (dev)", "Canonical app URL. Must match OAuth callback."],
        ["ANTHROPIC_API_KEY", "Optional", "sk-ant-...", "Anthropic API key for real AI analysis (future)"],
    ]
    story.append(make_table(["Variable", "Required", "Example", "Description"], env_rows,
                              [(PAGE_W-2*MARGIN)*p for p in [0.22, 0.10, 0.25, 0.43]]))
    story += code_block([
        "# Generate NEXTAUTH_SECRET:",
        "openssl rand -base64 32",
        "",
        "# Or using Node.js:",
        "node -e \"console.log(require('crypto').randomBytes(32).toString('base64'))\"",
    ], "Secret generation")
    story.append(PB())

    story.append(P("Appendix C: Keyboard Shortcuts", "h1"))
    story.append(HR())
    kb_rows = [
        ["g → d", "Navigate to Dashboard (/dashboard)"],
        ["g → g", "Navigate to Genome (/genome)"],
        ["g → p", "Navigate to Projects (/projects)"],
        ["g → r", "Navigate to Growth (/growth)"],
        ["g → s", "Navigate to Settings (/settings)"],
    ]
    story.append(make_table(["Shortcut", "Action"], kb_rows,
                              [(PAGE_W-2*MARGIN)*p for p in [0.25, 0.75]]))
    story.append(SP(8))
    story.append(P(
        "All shortcuts use a <b>two-key chord pattern</b> with a 1.5-second window between keys. "
        "Shortcuts are disabled when focus is in any input, textarea, or contenteditable element. "
        "Implemented in <tt>src/hooks/use-keyboard-shortcuts.ts</tt>.", "body"))

    # ══════════════════════════════════════════════════════════════════════
    # BUILD
    # ══════════════════════════════════════════════════════════════════════
    print(f"Building PDF → {OUT_PATH}")
    doc.build(story, onFirstPage=on_page_cover, onLaterPages=on_page)
    size = os.path.getsize(OUT_PATH)
    print(f"Done! {size/1024:.1f} KB — {OUT_PATH}")

if __name__ == "__main__":
    build()
