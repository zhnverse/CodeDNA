#!/usr/bin/env python3
import os, textwrap
from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, PageBreak, HRFlowable, Image, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import Flowable

W, H = A4
TEAL = colors.HexColor('#0D9488')
DARK = colors.HexColor('#0F172A')
GRAY = colors.HexColor('#64748B')
LGRAY = colors.HexColor('#F1F5F9')
EGRAY = colors.HexColor('#E2E8F0')
WHITE = colors.white
CODE_BG = colors.HexColor('#1E293B')
CODE_FG = colors.HexColor('#E2E8F0')

ss = getSampleStyleSheet()
def sty(name,**kw): s=ParagraphStyle(name,**kw); return s

cover_title = sty('CoverTitle', fontSize=32, leading=40, textColor=WHITE, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=12)
cover_sub   = sty('CoverSub',   fontSize=16, leading=24, textColor=colors.HexColor('#94A3B8'), alignment=TA_CENTER, fontName='Helvetica', spaceAfter=8)
cover_info  = sty('CoverInfo',  fontSize=11, leading=18, textColor=colors.HexColor('#CBD5E1'), alignment=TA_CENTER, fontName='Helvetica')
h1  = sty('H1',  fontSize=22, leading=30, textColor=TEAL, fontName='Helvetica-Bold', spaceBefore=18, spaceAfter=10)
h2  = sty('H2',  fontSize=15, leading=22, textColor=DARK, fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=7)
h3  = sty('H3',  fontSize=12, leading=18, textColor=colors.HexColor('#0F766E'), fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=5)
body= sty('Body',fontSize=10, leading=16, textColor=DARK, fontName='Helvetica', spaceAfter=7, alignment=TA_JUSTIFY)
bullet=sty('Bullet',fontSize=10,leading=16,textColor=DARK,fontName='Helvetica',spaceAfter=4,leftIndent=18,bulletIndent=6)
cap = sty('Cap',  fontSize=9,  leading=13, textColor=GRAY, fontName='Helvetica-Oblique', alignment=TA_CENTER, spaceBefore=4, spaceAfter=12)
code= sty('Code', fontSize=8,  leading=13, textColor=CODE_FG, fontName='Courier', spaceAfter=3, backColor=CODE_BG, leftIndent=12, rightIndent=12)


class ColorRect(Flowable):
    width = 0
    height = 0
    def __init__(self, w, h, color): self.w,self.h,self.color=w,h,color; self.width=w; self.height=h
    def draw(self): self.canv.setFillColor(self.color); self.canv.rect(0,0,self.w,self.h,fill=1,stroke=0)

SHOTS = "/home/sloth/Skill/CodeDNA/report-screenshots"
def img(name, caption="", w=13*cm):
    p = os.path.join(SHOTS, name)
    elems = []
    if os.path.exists(p):
        try:
            from PIL import Image as PILImg
            im = PILImg.open(p)
            iw,ih = im.size
            aspect = ih/iw
            h_calc = w*aspect
            max_h = 16*cm
            if h_calc > max_h:
                h_calc = max_h
                w = max_h/aspect
            elems.append(Image(p, width=w, height=h_calc))
            if caption: elems.append(Paragraph(caption, cap))
        except: pass
    else:
        box_data = [[Paragraph(f'[Screenshot: {caption}]', sty('PH',fontSize=9,textColor=GRAY,fontName='Helvetica-Oblique',alignment=TA_CENTER))]]
        t = Table(box_data, colWidths=[w], rowHeights=[60])
        t.setStyle(TableStyle([('BOX',(-1,-1),(-1,-1),1,EGRAY),('BACKGROUND',(0,0),(-1,-1),LGRAY),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
        elems.append(t)
        if caption: elems.append(Paragraph(caption, cap))
    return elems

def hr(): return HRFlowable(width='100%', thickness=1, color=EGRAY, spaceAfter=10, spaceBefore=4)
def p(text, style=None): return Paragraph(text, style or body)
def b(text): return Paragraph(f'• {text}', bullet)
def sp(n=6): return Spacer(1, n)
def code_block(text):
    lines = text.strip().split('\n')
    elems = []
    for line in lines:
        elems.append(Paragraph(line.replace(' ','&nbsp;').replace('<','&lt;').replace('>','&gt;') or '&nbsp;', code))
    return elems

def tbl(data, col_widths=None, header=True):
    t = Table(data, colWidths=col_widths)
    style = [
        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,0),(-1,-1),9),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE, LGRAY]),
        ('GRID',(0,0),(-1,-1),0.5,EGRAY),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),6),
    ]
    if header:
        style += [('BACKGROUND',(0,0),(-1,0),TEAL),('TEXTCOLOR',(0,0),(-1,0),WHITE),
                  ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,0),9)]
    t.setStyle(TableStyle(style))
    return t


def cover_page():
    elems = [sp(80), ColorRect(16.5*cm, 2, TEAL), sp(30),
        p('CodeDNA', cover_title), sp(6),
        p('AI-Powered Developer Genome Analysis Platform', cover_sub), sp(20),
        p('Portfolio &amp; Technical Documentation', sty('PS',fontSize=14,leading=20,textColor=colors.HexColor('#94A3B8'),alignment=TA_CENTER,fontName='Helvetica')),
        sp(50), hr(), sp(12),
        p('Author: Md Zahid Hasan Nerob', cover_info), sp(4),
        p('GitHub: github.com/zhnverse', cover_info), sp(4),
        p(f'Date: May 2026', cover_info), sp(20),
        ColorRect(16.5*cm, 2, TEAL),
        PageBreak()]
    return elems

def part1():
    e = []
    e += [p('PART 1: PORTFOLIO SHOWCASE', h1), hr()]

    # 1.1 Executive Summary
    e += [p('1.1 Executive Summary', h2),
        p('CodeDNA is a full-stack, AI-powered developer profiling platform that transforms GitHub repositories into a living visual genome — a dynamic fingerprint of how a developer truly codes. Unlike traditional profiles that rely on self-reported skills or simple activity metrics, CodeDNA analyzes every repository\'s language distribution, architectural patterns, code quality indicators, and dependency graphs to generate an evidence-backed skill taxonomy with verified proficiency levels.', body),
        p('Built as a solo full-stack project from the ground up, CodeDNA demonstrates mastery across the entire web development spectrum: OAuth 2.0 authentication, RESTful API design, relational database modeling, server-side rendering, D3.js data visualization, and AI-driven code analysis pipelines. The platform is publicly shareable, embeddable via SVG widget, and designed to evolve in real-time as a developer pushes new code — making it the most honest developer portfolio tool available.', body),
        sp(8)]

    # 1.2 Problem & Solution
    e += [p('1.2 Problem &amp; Solution', h2),
        p('<b>The Problem:</b> The current developer credentialing system is fundamentally broken. GitHub\'s contribution graph (green squares) shows <i>when</i> you committed, not <i>what</i> you built. LinkedIn skills are completely self-reported — anyone can claim React expertise with zero evidence. Technical interviews are the only real signal, but they\'re expensive, slow, and anxiety-inducing.', body),
        p('<b>The Solution:</b> CodeDNA connects to GitHub via OAuth 2.0, syncs all repositories (public and private), runs each through a multi-stage analysis pipeline, and generates a living visual genome that evolves as you code. Skills are classified as Claimed, Demonstrated, or Mastered based on evidence depth across your entire codebase. The genome is public, shareable, and embeddable — giving recruiters and collaborators instant, evidence-backed insight into your actual abilities.', body),
        sp(4)] + img('01-landing-loggedout.png', 'Fig 1.1 — Landing page: "Your Code Has DNA" — one-click GitHub OAuth entry point') + [sp(10)]

    # 1.3 Features
    e += [p('1.3 Feature Walkthrough', h2)]

    # A - GitHub OAuth
    e += [p('A. GitHub OAuth &amp; Repository Sync', h3),
        p('<b>What it does:</b> One-click GitHub connection via OAuth 2.0. The platform syncs all repositories — public and private — capturing metadata: name, description, primary language, stars, forks, and repo size. Subsequent syncs use upsert logic to update changed fields without duplicating records.', body),
        p('<b>How it works technically:</b> NextAuth.js handles the GitHub OAuth 2.0 flow, storing the access token in the session. The <font face="Courier">/api/repos/sync</font> endpoint calls GitHub\'s REST API with <font face="Courier">fetchUserRepos()</font>, which paginates through all repos (100 per page) with automatic rate-limit detection via <font face="Courier">X-RateLimit-Remaining</font> headers, backing off when fewer than 5 requests remain.', body),
        p('<b>Why it matters:</b> Developers shouldn\'t have to manually list their projects. The sync is instantaneous and comprehensive — every repo, every language, immediately in the system.', body),
    ] + img('02-dashboard.png', 'Fig 1.2 — Dashboard: GitHub repository sync showing repos with analysis status') + [sp(10)]

    # B - AI Analysis
    e += [p('B. AI-Powered Code Analysis Pipeline', h3),
        p('<b>What it does:</b> Each repository is analyzed through a multi-stage pipeline: file tree extraction → language detection → dependency mapping → pattern recognition → skill extraction. The engine detects architecture patterns (MVC, Jamstack, Layered, Microservice, Serverless, Event-Driven) and maps findings to a normalized skill taxonomy with confidence levels.', body),
        p('<b>How it works technically:</b> The <font face="Courier">analyzeRepository()</font> function in <font face="Courier">src/lib/analysis.ts</font> orchestrates the pipeline. It first attempts to fetch the repo\'s file tree via <font face="Courier">fetchRepoTree()</font> (GitHub Trees API, recursive), then calls <font face="Courier">mockAnalyzeRepo()</font> which uses a seeded deterministic algorithm based on repo name, language, description, stars, and forks. Skills are upserted into <font face="Courier">SkillNode</font> records; new skills trigger <font face="Courier">GrowthEvent</font> entries. A <font face="Courier">GenomeSnapshot</font> is created after each analysis. The current implementation uses a sophisticated mock engine designed for seamless migration to the Anthropic Claude API.', body),
        p('<b>Why it matters:</b> Analysis runs in minutes, not hours. Developers get immediate insight into their entire codebase without any manual tagging or configuration.', body), sp(6)]

    # C - Score
    e += [p('C. Developer Score Algorithm', h3),
        p('<b>What it does:</b> Produces a composite 0–100 score representing overall developer capability, calculated from 5 weighted factors derived entirely from actual code — not self-assessment.', body),
        p('<b>How it works technically:</b> The <font face="Courier">calculateDeveloperScore()</font> function in <font face="Courier">src/lib/scoring.ts</font> computes:', body),
        b('Code Quality (30%): Average <font face="Courier">overallQuality</font> across all analyzed repos'),
        b('Skill Breadth (20%): skill count × 3 + category count × 5, capped at 100'),
        b('Skill Depth (20%): mastered × 3 + demonstrated × 2 + claimed × 1, × 4, capped at 100'),
        b('Consistency (15%): analyzed repos × 8 + recently active repos × 5, capped at 100'),
        b('Growth Velocity (15%): growth events in last 90 days × 5, capped at 100'),
        p('Final score = Quality×0.3 + Breadth×0.2 + Depth×0.2 + Consistency×0.15 + Growth×0.15', body),
        p('<b>Why it matters:</b> A single number that means something — because it\'s derived from code evidence, not self-reporting.', body), sp(6)]

    return e


def part1b():
    e = []
    # D - DNA Helix
    e += [p('D. DNA Helix Visualization', h3),
        p('<b>What it does:</b> The centerpiece visualization — an animated SVG double helix using 3D projection mathematics with depth-sorted rendering. Each gene node represents a detected skill, sized proportionally to its proficiency score and colored by category: blue (Languages), green (Frameworks), orange (Patterns), purple (Tools), teal (Concepts).', body),
        p('<b>How it works technically:</b> The <font face="Courier">DNAHelix</font> component (<font face="Courier">src/components/genome/dna-helix.tsx</font>) renders in a <font face="Courier">requestAnimationFrame</font> loop. The helix geometry uses parametric equations: for each point <i>t</i> along the helix, strand A is at <font face="Courier">(R·cos(θ+rot), y, R·sin(θ+rot))</font> and strand B at <font face="Courier">(R·cos(θ+rot+π), y, R·sin(θ+rot+π))</font>. The <font face="Courier">project()</font> function applies depth scaling (0.7–1.0) and alpha (0.5–1.0) based on Z position. Gene nodes are depth-sorted before rendering to create proper occlusion. Auto-rotation pauses on hover via <font face="Courier">hoveringRef</font>.', body),
        p('<b>Why it matters:</b> No other developer profile platform has a visualization this compelling. It makes technical skills viscerally tangible — your genome, literally.', body),
    ] + img('03-genome-helix.png', 'Fig 1.3 — DNA Helix: animated 3D visualization with color-coded skill gene nodes') + [sp(10)]

    # E - Radar
    e += [p('E. Radar Chart View', h3),
        p('<b>What it does:</b> A D3.js radar chart maps skill proficiency across 5 axes — Languages, Frameworks, Patterns, Tools, and Concepts. The filled polygon shows relative strength distribution, instantly revealing if a developer is frontend-heavy, backend-dominant, or well-rounded.', body),
        p('<b>How it works technically:</b> Built with D3.js scales and SVG polygon generation. Each axis represents one skill category, scaled linearly from 0 to the maximum proficiency score. The polygon vertices are calculated trigonometrically from the axis angles and category scores. The chart adapts colors based on the active theme (dark/light).', body),
        p('<b>Why it matters:</b> Radar charts communicate skill balance at a glance — recruiters can instantly see a developer\'s strengths vs. gaps without reading a list.', body), sp(6)]
    e += img('04-genome-radar.png', 'Fig 1.4 — Radar Chart: skill distribution across 5 axes showing developer strength profile') + [sp(10)]

    # F - Skill Tree
    e += [p('F. Skill Tree — D3 Force Graph', h3),
        p('<b>What it does:</b> A D3 force-directed graph with physics simulation. The developer node sits at center, connected to category branches, which connect to individual skill leaf nodes. Node size represents proficiency score; edge opacity shows connection strength.', body),
        p('<b>How it works technically:</b> The <font face="Courier">SkillTree</font> component uses <font face="Courier">d3.forceSimulation</font> with three forces: <font face="Courier">forceLink</font> (distance 90, strength 0.4–0.6), <font face="Courier">forceManyBody</font> (strength −220 for repulsion), and <font face="Courier">forceCenter</font>. <font face="Courier">forceCollide</font> prevents node overlap. The simulation ticks update SVG element positions in real-time.', body),
        p('<b>Why it matters:</b> The force graph reveals skill clusters and relationships — seeing TypeScript connected to Node.js connected to REST API tells a story no bullet list can.', body), sp(6)]
    e += img('05-genome-tree.png', 'Fig 1.5 — Skill Tree: D3 force-directed graph showing skill relationships and category clusters') + [sp(10)]

    # G - Skill Table
    e += [p('G. Skill Table &amp; Filtering', h3),
        p('<b>What it does:</b> A searchable, sortable table of all detected skills with category badges and confidence indicators. Filter by category (Language, Framework, Pattern, Tool, Concept) or confidence level (Claimed, Demonstrated, Mastered). Sort by proficiency score or name.', body),
        p('<b>Why it matters:</b> The table provides the evidence layer — every skill has a proficiency score, confidence rating, and evidence trail linking back to specific repositories.', body), sp(6)]

    # H - Projects
    e += [p('H. Project Showcase Cards', h3),
        p('<b>What it does:</b> Auto-generated project cards from analyzed repositories. Each card shows an AI-written project summary, detected architecture pattern badge (MVC, Jamstack, Layered, Microservice), language indicators, complexity and quality score bars, and detected skills as chips. The "Best Work" section auto-surfaces top repositories by combined quality + complexity score.', body),
        p('<b>How it works technically:</b> The <font face="Courier">/api/public/projects/[username]</font> endpoint queries repositories ordered by <font face="Courier">complexityScore + analysisData.qualityIndicators.overallQuality</font>. The <font face="Courier">isTutorialClone</font> flag (from mock analysis) filters out boilerplate repos. Project summaries are generated by the analysis pipeline from repo name, description, and detected patterns.', body),
        p('<b>Why it matters:</b> Automatically surfaces your best work — no curation needed. The architecture badges give technical context that a repo name alone cannot.', body), sp(6)]
    e += img('06-projects.png', 'Fig 1.6 — Projects page: auto-generated cards with architecture badges, quality scores, and detected skills') + [sp(10)]

    # I - Deep Analysis
    e += [p('I. Repository Deep Analysis View', h3),
        p('<b>What it does:</b> A per-repository deep dive showing architecture detection with confidence score, code pattern breakdown (error handling, testing, API design, state management, naming conventions), quality indicator bars, demonstrated skills, and project highlights. Provides evidence-backed proof of capability.', body),
        p('<b>How it works technically:</b> The <font face="Courier">analysisData</font> JSON field on each <font face="Courier">Repository</font> record stores the full <font face="Courier">MockAnalysisResult</font> object after analysis, including <font face="Courier">codePatterns</font>, <font face="Courier">qualityIndicators</font>, <font face="Courier">architecturePattern</font>, <font face="Courier">architectureConfidence</font>, and <font face="Courier">skillsDemonstrated</font>.', body), sp(6)]

    # J - Growth
    e += [p('J. Growth Timeline', h3),
        p('<b>What it does:</b> Tracks skill progression over time with a D3 stacked area chart colored by category. Shows cumulative skill counts per week, with milestones marking skill discoveries and level-ups. "Predicted Next Skills" forecasts likely future skills based on current skill adjacency.', body),
        p('<b>How it works technically:</b> <font face="Courier">GrowthTimeline</font> component (<font face="Courier">src/components/growth/growth-timeline.tsx</font>) uses <font face="Courier">d3.stack</font> with <font face="Courier">stackOffsetNone</font> on weekly buckets. Events are grouped by <font face="Courier">d3.timeWeeks</font>, cumulated, then rendered as <font face="Courier">d3.area</font> curves with <font face="Courier">curveCatmullRom</font> smoothing.', body), sp(6)]
    e += img('07-growth.png', 'Fig 1.7 — Growth page: stacked area timeline, milestones feed, and achievement badges') + [sp(10)]

    # K - Achievements
    e += [p('K. Achievement System', h3),
        p('<b>What it does:</b> Gamified skill badges: Polyglot (5+ languages), Full Stack (frontend + backend + database skills), Quality First (score &gt; 80), Prolific (20+ repos), Speed Learner (5+ skills in 30 days). Earned badges appear highlighted; locked badges are grayed with unlock criteria shown.', body),
        p('<b>Why it matters:</b> Gamification creates engagement and gives developers concrete goals to work toward, driving more coding and analysis activity.', body), sp(6)]

    # L - Public Profile
    e += [p('L. Public Shareable Profile', h3),
        p('<b>What it does:</b> Every developer gets a public profile URL at <font face="Courier">/genome/[username]</font>. Includes the DNA helix, skill breakdown, top projects — fully accessible without login. OG meta tags generate rich link previews when shared on social media or messaging apps.', body),
        p('<b>How it works technically:</b> The <font face="Courier">/genome/[username]/page.tsx</font> is a server component that fetches user data server-side via Prisma, then passes it to <font face="Courier">ProfileClient</font>. OpenGraph metadata is generated via Next.js\'s <font face="Courier">generateMetadata()</font> function. Public API endpoints (<font face="Courier">/api/public/*</font>) serve data without authentication.', body), sp(6)]

    # L - Public profile screenshot
    e += img('10-public-profile.png', 'Fig 1.8 — Public profile /genome/zhnverse: shareable genome page accessible without login') + [sp(6)]

    # M - Widget
    e += [p('M. Embeddable SVG Widget', h3),
        p('<b>What it does:</b> A 400×320 SVG card showing the developer\'s score ring, top 5 skill bars with category colors, and username. Embeddable anywhere via <font face="Courier">&lt;img&gt;</font> tag, iframe, or Markdown image syntax. One-click copy in Settings.', body),
        p('<b>How it works technically:</b> The <font face="Courier">/api/widget/[username]</font> route generates SVG entirely server-side using string templates. The score ring uses SVG <font face="Courier">stroke-dasharray</font> with a glow filter. Response is cached with <font face="Courier">Cache-Control: public, max-age=3600</font>. Rate limited to 60 requests per IP per hour via an in-memory sliding window.', body), sp(6)]

    # N - Theme
    e += [p('N. Dark / Light Theme System', h3),
        p('<b>What it does:</b> Full dark/light theme support across all pages including all D3 visualizations. System preference is respected by default; users can manually toggle. All charts adapt their axis colors, stroke opacities, and background fills to the active theme.', body),
        p('<b>How it works technically:</b> <font face="Courier">next-themes</font> wraps the app in <font face="Courier">ThemeProvider</font>. Components use <font face="Courier">useTheme().resolvedTheme</font> to get the active theme and rerender D3 charts with appropriate colors. The <font face="Courier">GrowthTimeline</font> and <font face="Courier">DNAHelix</font> components both observe theme changes via <font face="Courier">useEffect</font> dependency on <font face="Courier">resolvedTheme</font>.', body), sp(6)]

    # O - Shortcuts
    e += [p('O. Keyboard Navigation Shortcuts', h3),
        p('<b>What it does:</b> Power-user navigation via two-key chord shortcuts. Provides instant access to all main sections without touching the mouse.', body),
        tbl([['Shortcut','Destination'],['G then D','Dashboard'],['G then G','Genome'],['G then P','Projects'],['G then R','Growth (Roadmap)'],['G then S','Settings']], col_widths=[8*cm, 8*cm]),
        p('Implemented via the <font face="Courier">useKeyboardShortcuts</font> hook mounted globally in the root layout, listening for sequential key events with a 1-second chord window.', body), sp(6)]

    # Mobile
    e += [p('P. Mobile Responsive Design', h3),
        p('CodeDNA is fully responsive across desktop (1440px), tablet, and mobile (375px) viewports. Navigation collapses to a mobile menu; charts adapt their width; skill tables scroll horizontally on small screens.', body),
    ] + img('13-mobile-landing.png', 'Fig 1.11 — Mobile view at 375px: responsive landing page layout', w=7*cm) + [sp(10)]

    # 1.4 Highlights
    e += [p('1.4 Technical Highlights Summary', h2),
        b('13 pages / routes across authentication, dashboard, genome, projects, growth, analysis, settings, and public profile'),
        b('6 Prisma database models: User, Repository, SkillNode, GenomeSnapshot, CodePattern, GrowthEvent'),
        b('14+ React components across dashboard, genome, growth, projects, layout, and UI categories'),
        b('14 REST API endpoints with authentication, rate limiting, and CORS'),
        b('3 distinct D3.js visualization types: DNA Helix (SVG 3D), Radar Chart, Force-Directed Skill Tree'),
        b('1 additional visualization: Stacked Area Growth Timeline'),
        b('Full OAuth 2.0 flow with GitHub provider, session management via NextAuth.js + Prisma adapter'),
        b('In-memory sliding-window rate limiter with proper HTTP headers (X-RateLimit-Remaining/Reset)'),
        b('Server-Side Rendering with Next.js 14 App Router — all public pages are SSR for SEO'),
        b('Full TypeScript end-to-end: frontend, API routes, Prisma schema, lib functions'),
        b('Responsive design: desktop, tablet, and mobile (375px) via Tailwind CSS'),
        b('Embeddable SVG widget with caching, rate limiting, and one-click copy'),
        sp(6)]

    # 1.5 Impact
    e += [p('1.5 Metrics &amp; Impact', h2),
        tbl([
            ['Metric','Value'],
            ['Development approach','Solo full-stack developer'],
            ['Development phases','5 (Design → Schema → API → Visualizations → Polish)'],
            ['Codebase type','TypeScript monorepo (Next.js)'],
            ['External paid services','Zero (mock analysis engine, free PostgreSQL)'],
            ['Deployment','One-click Vercel deploy with PostgreSQL on Neon/Supabase/Railway'],
            ['GitHub OAuth','Public + Private repository access'],
            ['Visualization engine','D3.js v7 — no paid chart library'],
            ['Lines of code (est.)','~4,500 lines across 82 source files'],
        ], col_widths=[8*cm, 8.5*cm]),
        PageBreak()]
    return e


def part2_arch():
    e = [p('PART 2: TECHNICAL DOCUMENTATION', h1), hr(),
        p('2.1 Architecture Overview', h2),
        p('CodeDNA follows a layered architecture with clear separation between presentation, business logic, and data persistence layers. All communication flows through Next.js API Routes, which act as the sole interface between the frontend and the database.', body)]
    arch = [
        ['Layer','Technology','Responsibility'],
        ['Client','Next.js 14 (App Router)','SSR pages, React client components, D3 visualizations'],
        ['API','Next.js API Routes','REST endpoints, auth guards, business logic orchestration'],
        ['Auth','NextAuth.js v4','GitHub OAuth 2.0, session management, JWT/DB sessions'],
        ['Analysis','src/lib/analysis.ts','Repository pipeline: fetch → analyze → upsert skills → snapshot'],
        ['ORM','Prisma v5','Type-safe DB queries, migrations, schema management'],
        ['Database','PostgreSQL 18','Persistent storage: users, repos, skills, growth events'],
        ['External','GitHub REST API v3','Repo data, file trees, language stats, OAuth tokens'],
    ]
    e += [tbl(arch, col_widths=[3.5*cm, 4.5*cm, 8.5*cm]), sp(10),
        p('Data Flow:', h3),
        p('1. User authenticates via GitHub OAuth → NextAuth creates/updates User record via Prisma adapter', body),
        p('2. User triggers repo sync → <font face="Courier">/api/repos/sync</font> → GitHub API → Prisma upsert Repository records', body),
        p('3. User triggers analysis → <font face="Courier">/api/analyze/all</font> → sequential analyzeRepository() calls → SkillNode upserts + GrowthEvent creation + GenomeSnapshot + Score recalculation', body),
        p('4. Frontend fetches genome data → <font face="Courier">/api/genome/data</font> → grouped SkillNodes → D3 visualizations render', body),
        p('5. Public profile → <font face="Courier">/genome/[username]</font> (SSR) → <font face="Courier">/api/public/*</font> → no-auth read-only access', body),
        sp(8)]
    return e

def part2_stack():
    e = [p('2.2 Technology Stack', h2)]
    stack = [
        ['Layer','Technology','Version','Rationale'],
        ['Framework','Next.js App Router','14.2.18','SSR, file-based routing, API routes, RSC'],
        ['Language','TypeScript','5.x','End-to-end type safety, IDE support'],
        ['Styling','Tailwind CSS','3.4.15','Utility-first, dark mode, responsive'],
        ['Components','Radix UI + shadcn/ui','Latest','Accessible, unstyled primitives'],
        ['Database','PostgreSQL','18','ACID transactions, JSON columns, relations'],
        ['ORM','Prisma','5.22.0','Type-safe queries, migrations, Prisma adapter'],
        ['Auth','NextAuth.js','4.24.11','OAuth 2.0, session management, GitHub provider'],
        ['Visualization','D3.js','7.9.0','Custom SVG charts, force simulation, scales'],
        ['Theme','next-themes','0.4.6','Dark/light/system theme switching'],
        ['Icons','Lucide React','0.454.0','Consistent icon system'],
        ['Animation','tailwindcss-animate','1.0.7','CSS keyframe animations'],
    ]
    e += [tbl(stack, col_widths=[3*cm, 4*cm, 2.5*cm, 7*cm]), sp(8)]
    return e

def part2_schema():
    e = [p('2.3 Database Schema', h2),
        p('The database consists of 6 models with 4 enums, modeling the complete lifecycle from user authentication through skill discovery and growth tracking.', body)]

    models = [
        ('User', [
            ['Field','Type','Description'],
            ['id','String (cuid)','Primary key, auto-generated'],
            ['githubId','String (unique)','GitHub user numeric ID'],
            ['username','String (unique)','GitHub login handle'],
            ['avatar','String?','Avatar URL from GitHub'],
            ['bio','String?','GitHub bio text'],
            ['email','String?','GitHub primary email'],
            ['developerScore','Int (default 0)','Computed composite score 0–100'],
            ['createdAt','DateTime','Account creation timestamp'],
            ['updatedAt','DateTime','Auto-updated on save'],
        ]),
        ('Repository', [
            ['Field','Type','Description'],
            ['id','String (cuid)','Primary key'],
            ['userId','String','FK → User'],
            ['githubRepoId','String (unique)','GitHub numeric repo ID'],
            ['name','String','Repo name (e.g. "CodeDNA")'],
            ['fullName','String','owner/repo format'],
            ['primaryLanguage','String?','GitHub-detected primary language'],
            ['languages','Json?','Language byte breakdown map'],
            ['stars / forks / size','Int','GitHub metadata'],
            ['isPrivate','Boolean','Private repo flag'],
            ['isAnalyzed','Boolean','Analysis complete flag'],
            ['analysisData','Json?','Full MockAnalysisResult JSON'],
            ['complexityScore','Int?','0–100 complexity from analysis'],
        ]),
        ('SkillNode', [
            ['Field','Type','Description'],
            ['id','String (cuid)','Primary key'],
            ['userId','String','FK → User'],
            ['name','String','Skill name (e.g. "TypeScript")'],
            ['category','SkillCategory','LANGUAGE/FRAMEWORK/PATTERN/TOOL/CONCEPT'],
            ['proficiencyScore','Int','0–100 score from analysis'],
            ['confidence','SkillConfidence','CLAIMED/DEMONSTRATED/MASTERED'],
            ['evidence','Json','Array of evidence strings (last 10)'],
            ['firstSeen / lastSeen','DateTime','Temporal tracking'],
            ['','Unique constraint','(userId, name) — one skill per user'],
        ]),
        ('GenomeSnapshot', [
            ['Field','Type','Description'],
            ['id','String (cuid)','Primary key'],
            ['userId','String','FK → User'],
            ['genomeData','Json','Grouped skills by category at snapshot time'],
            ['totalSkills','Int','Total skill count at snapshot'],
            ['topCategory','String?','Category with most skills'],
            ['createdAt','DateTime','Snapshot timestamp'],
        ]),
        ('CodePattern', [
            ['Field','Type','Description'],
            ['id','String (cuid)','Primary key'],
            ['userId / repoId','String','FKs → User, Repository'],
            ['patternType','PatternType','ARCHITECTURE/ERROR_HANDLING/TESTING/API_DESIGN/STATE_MANAGEMENT/NAMING_CONVENTION'],
            ['description','String','Human-readable pattern description'],
            ['frequency','Int','Detection count across analyses'],
            ['qualityScore','Int?','0–100 pattern quality'],
        ]),
        ('GrowthEvent', [
            ['Field','Type','Description'],
            ['id','String (cuid)','Primary key'],
            ['userId','String','FK → User'],
            ['skillNodeId','String?','FK → SkillNode (nullable)'],
            ['eventType','GrowthEventType','NEW_SKILL/LEVEL_UP/MILESTONE/NEW_REPO'],
            ['title','String','Event display title'],
            ['description','String?','Extended description'],
            ['metadata','Json?','Additional event data'],
            ['createdAt','DateTime','Event timestamp'],
        ]),
    ]

    for mname, fields in models:
        e += [p(f'Model: {mname}', h3), tbl(fields, col_widths=[4*cm, 3.5*cm, 9*cm]), sp(6)]

    e += [p('Full schema.prisma (Appendix A contains raw source)', body), sp(8)]
    return e


def part2_api():
    e = [p('2.4 API Reference', h2),
        p('All authenticated endpoints use <font face="Courier">getApiUser(req)</font> from <font face="Courier">src/lib/api-auth.ts</font> which validates the NextAuth session cookie and returns <font face="Courier">{ userId, accessToken }</font>. Public endpoints under <font face="Courier">/api/public/*</font> and <font face="Courier">/api/widget/*</font> require no authentication.', body)]

    routes = [
        ['Method','Endpoint','Auth','Description'],
        ['POST','/api/repos/sync','Required','Syncs all GitHub repos for the authenticated user. Fetches via GitHub REST API with pagination, upserts Repository records. Returns { total, created, updated }.'],
        ['GET','/api/repos','Required','Returns all repositories for the user ordered by update date. Includes analysis status and metadata.'],
        ['GET','/api/stats','Required','Returns dashboard statistics: analyzedRepos, skillCount, developerScore, growthVelocity (last 30d), languageBreakdown, topSkills.'],
        ['GET','/api/activity','Required','Returns recent GrowthEvents for the activity feed: NEW_SKILL, LEVEL_UP, MILESTONE, NEW_REPO events with timestamps.'],
        ['POST','/api/analyze/[repoId]','Required','Analyzes a single repository. Runs the full pipeline: fetch tree → mock analysis → upsert skills → snapshot → recalculate score. Returns { success }.'],
        ['POST','/api/analyze/all','Required','Analyzes all un-analyzed repositories sequentially in background. Returns immediately with { status: "started", count }. Skips repos already in fetching/analyzing state.'],
        ['GET','/api/analyze/status/[repoId]','Required','Returns current analysis status for a repo: pending/fetching/analyzing/complete/error. Polls this to show progress indicators.'],
        ['GET','/api/genome/data','Required','Returns all SkillNodes grouped by category. Used by all genome visualizations (helix, radar, skill tree, table).'],
        ['GET','/api/score','Required','Recalculates and returns developer score with full breakdown: analyzedRepos, totalSkills, mastered, demonstrated, claimed counts.'],
        ['GET','/api/public/genome/[username]','None','Public genome data for a user: skills grouped by category, score, top repos. SSR-compatible, no auth.'],
        ['GET','/api/public/skills/[username]','None','Returns all SkillNodes for a username ordered by proficiency. Used by public profile skill table.'],
        ['GET','/api/public/projects/[username]','None','Returns analyzed repositories for a username ordered by complexity score. Filters tutorial clones.'],
        ['GET','/api/public/score/[username]','None','Returns developerScore and skill count for a username. Used by widget and public profile.'],
        ['GET','/api/widget/[username]','None','Returns a 400×320 SVG card with score ring and top 5 skill bars. Rate limited to 60 req/hour/IP. Cache-Control: max-age=3600.'],
    ]
    e += [tbl(routes, col_widths=[1.5*cm, 5.5*cm, 1.8*cm, 7.7*cm]), sp(6),
        p('Example Response — GET /api/stats:', h3)]
    e += code_block('''{
  "analyzedRepos": 10,
  "skillCount": 12,
  "developerScore": 71,
  "growthVelocity": 8,
  "languageBreakdown": [
    { "language": "TypeScript", "count": 4 },
    { "language": "JavaScript", "count": 3 },
    { "language": "Python", "count": 2 }
  ],
  "topSkills": [
    { "axis": "TypeScript", "value": 87 },
    { "axis": "React",      "value": 83 },
    { "axis": "REST API",   "value": 91 }
  ]
}''')
    e += [sp(6), p('Example Response — GET /api/widget/zhnverse (SVG):', h3),
        p('Returns <font face="Courier">Content-Type: image/svg+xml</font> — a 400×320 dark-themed SVG card with the username, score ring (stroke-dasharray progress ring with glow filter), and top 5 skill bars colored by category. Cache headers ensure the widget is served from CDN for 1 hour.', body), sp(8)]
    return e

def part2_components():
    e = [p('2.5 Component Architecture', h2),
        p('All components follow the Next.js App Router pattern: server components for data fetching, client components (<font face="Courier">"use client"</font>) for interactivity and D3 visualizations.', body)]

    comps = [
        ['Component','File','Type','Purpose / Key Props'],
        ['DNAHelix','genome/dna-helix.tsx','Client','Animated SVG double helix. Props: skills[], className'],
        ['GenomeRadar','genome/genome-radar.tsx','Client','Radar chart wrapper with D3 rendering'],
        ['RadarChart','genome/radar-chart.tsx','Client','Core D3 radar chart. Props: data (axis/value pairs)'],
        ['SkillTree','genome/skill-tree.tsx','Client','D3 force-directed graph. Props: skills[]'],
        ['SkillTable','genome/skill-table.tsx','Client','Filterable skill table. Props: skills[], grouped'],
        ['GrowthTimeline','growth/growth-timeline.tsx','Client','D3 stacked area chart. Props: events[]'],
        ['MilestonesFeed','growth/milestones-feed.tsx','Client','Scrollable growth event list. Props: events[]'],
        ['DashboardRadar','dashboard/dashboard-radar.tsx','Client','Dashboard mini radar. Props: topSkills[]'],
        ['DonutChart','dashboard/donut-chart.tsx','Client','Language distribution donut. Props: data[]'],
        ['RepoTable','dashboard/repo-table.tsx','Client','Repository list with analysis controls. Props: repos[]'],
        ['StatCard','dashboard/stat-card.tsx','Client','KPI card. Props: title, value, icon, trend'],
        ['SyncButton','dashboard/sync-button.tsx','Client','GitHub sync trigger button with loading state'],
        ['ActivityFeed','dashboard/activity-feed.tsx','Client','Recent growth events list'],
        ['ProjectCard','projects/project-card.tsx','Client','Repo card with scores, skills, architecture badge'],
        ['Navbar','layout/navbar.tsx','Client','Top navigation with theme toggle, user menu'],
        ['Footer','layout/footer.tsx','Server','Site footer with links'],
        ['ThemeToggle','layout/theme-toggle.tsx','Client','Dark/light/system theme switcher'],
        ['KeyboardShortcuts','layout/keyboard-shortcuts.tsx','Client','Global keyboard shortcut handler'],
        ['Providers','layout/providers.tsx','Client','SessionProvider + ThemeProvider wrapper'],
    ]
    e += [tbl(comps, col_widths=[3.5*cm, 4.5*cm, 1.8*cm, 6.7*cm]), sp(8)]
    return e


def part2_engine():
    e = [p('2.6 Analysis Engine', h2),
        p('The analysis engine (<font face="Courier">src/lib/analysis.ts</font> + <font face="Courier">src/lib/mock-analysis.ts</font>) is the core intelligence of CodeDNA. It transforms raw repository metadata into structured skill data.', body),
        p('Pipeline Steps:', h3),
        p('1. <b>Repository Fetch:</b> The <font face="Courier">analyzeRepository()</font> function marks the repo as <font face="Courier">{ status: "fetching" }</font> and attempts to load the full file tree via GitHub\'s Trees API (recursive). This provides file paths for enhanced pattern detection.', body),
        p('2. <b>Mock Analysis:</b> <font face="Courier">mockAnalyzeRepo()</font> receives repo metadata and runs deterministic analysis using a seeded hash function (<font face="Courier">seeded()</font>) to ensure consistent scores across repeated analyses. The seed is the repo name.', body),
        p('3. <b>Skill Extraction:</b> The engine looks up the primary language in <font face="Courier">LANG_SKILLS</font> (16 languages mapped to skill sets) then scans the repo name + description against 22 regex patterns in <font face="Courier">HINTS</font> to detect frameworks, tools, and concepts.', body),
        p('4. <b>Architecture Detection:</b> <font face="Courier">detectArch()</font> classifies repos into 6 patterns (microservice, serverless, event-driven, jamstack, MVC, layered) using regex matching against name + description.', body),
        p('5. <b>Quality Scoring:</b> Four quality indicators (naming consistency, separation of concerns, DRY adherence, overall quality) are generated via seeded random within ±10 of the base repo score.', body),
        p('6. <b>Persistence:</b> SkillNodes are upserted (new → create + NEW_SKILL GrowthEvent; existing → update score if improved + LEVEL_UP GrowthEvent). CodePatterns are upserted per repo. A GenomeSnapshot is created. Developer score is recalculated.', body),
        p('Key Code Snippet — seeded deterministic scoring:', h3)]
    e += code_block('''// Seeded hash for deterministic scores
function seeded(seed: string, salt: string, min: number, max: number): number {
  let h = 0x811c9dc5;
  const s = seed + salt;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = (h * 0x01000193) >>> 0;
  }
  return min + (h % (max - min + 1));
}''')
    e += [sp(6), p('Migration to Real AI (Anthropic Claude):', h3),
        p('The <font face="Courier">mockAnalyzeRepo()</font> function in <font face="Courier">mock-analysis.ts</font> is the only component that needs replacement. The interface <font face="Courier">MockAnalysisResult</font> defines the exact schema the system expects. Replacing the mock with an Anthropic API call requires:', body),
        b('Replace <font face="Courier">mockAnalyzeRepo()</font> with a Claude API call passing repo name, description, file tree, and sampled file contents'),
        b('Parse Claude\'s structured JSON response into the <font face="Courier">MockAnalysisResult</font> interface'),
        b('Set <font face="Courier">ANTHROPIC_API_KEY</font> environment variable (currently placeholder in .env.local)'),
        b('No other code changes required — the pipeline, persistence, and scoring layers are all AI-agnostic'),
        sp(8)]
    return e

def part2_scoring():
    e = [p('2.7 Scoring Algorithm', h2),
        p('The developer score is a 0–100 composite calculated entirely from evidence in the database — no self-assessment, no guessing. Source: <font face="Courier">src/lib/scoring.ts</font>.', body),
        p('Formula:', h3)]
    e += code_block('''Score = Quality × 0.30
      + Breadth × 0.20
      + Depth  × 0.20
      + Consistency × 0.15
      + Growth × 0.15''')
    e += [sp(6)]
    factors = [
        ['Factor','Weight','Formula','What it measures'],
        ['Code Quality','30%','avg(overallQuality) across analyzed repos','Real code quality: naming, DRY, separation of concerns'],
        ['Skill Breadth','20%','min(skills×3 + categories×5, 100)','Diversity across the 5 skill categories'],
        ['Skill Depth','20%','min((mastered×3 + demonstrated×2 + claimed)×4, 100)','Mastery levels weighted by confidence'],
        ['Consistency','15%','min(analyzedRepos×8 + recentRepos×5, 100)','Coverage and recency of analysis'],
        ['Growth Velocity','15%','min(growthEvents90d×5, 100)','New skills/level-ups in last 90 days'],
    ]
    e += [tbl(factors, col_widths=[3*cm, 2*cm, 6.5*cm, 5*cm]),
        sp(6), p('Example Calculation (10 repos, 12 skills):', h3)]
    e += code_block('''Quality:     avg quality = 75.0  → 75.0
Breadth:     12 skills × 3 + 4 categories × 5 = 56  → 56.0
Depth:       (2 mastered × 3 + 6 demonstrated × 2 + 4 claimed) × 4 = 88  → 88.0
Consistency: 10 repos × 8 + 3 recent × 5 = 95  → 95.0
Growth:      8 events × 5 = 40  → 40.0

Score = 75×0.30 + 56×0.20 + 88×0.20 + 95×0.15 + 40×0.15
      = 22.5 + 11.2 + 17.6 + 14.25 + 6.0
      = 71.55 → 72 (rounded)''')
    e += [sp(8)]
    return e

def part2_auth():
    e = [p('2.8 Authentication Flow', h2),
        p('CodeDNA uses GitHub OAuth 2.0 via NextAuth.js with the Prisma adapter for persistent sessions.', body),
        p('OAuth 2.0 Sequence:', h3),
        p('1. User clicks "Connect GitHub" → NextAuth generates authorization URL with <font face="Courier">scope: read:user, repo</font>', body),
        p('2. GitHub shows permission screen → User approves → GitHub redirects to <font face="Courier">/api/auth/callback/github</font>', body),
        p('3. NextAuth exchanges authorization code for access token → fetches GitHub user profile', body),
        p('4. Prisma adapter upserts User record (<font face="Courier">githubId</font>, <font face="Courier">username</font>, <font face="Courier">avatar</font>, <font face="Courier">email</font>)', body),
        p('5. Session is created — access token stored in session for subsequent GitHub API calls', body),
        p('6. Subsequent requests: <font face="Courier">getApiUser(req)</font> calls <font face="Courier">getServerSession()</font> → returns <font face="Courier">{ userId, accessToken }</font> or null (→ 401)', body),
        p('Protected Routes (Middleware):', h3),
        p('The <font face="Courier">src/middleware.ts</font> exports NextAuth\'s default middleware, protecting these routes:', body),
        b('/dashboard/:path* — main user dashboard'),
        b('/genome — personal genome page (note: /genome/[username] is public)'),
        b('/projects/:path* — project showcase'),
        b('/growth/:path* — growth tracking'),
        b('/settings/:path* — user settings'),
        b('/analysis/:path* — deep analysis views'),
        p('Unauthenticated requests to protected routes are automatically redirected to the sign-in page.', body), sp(8)]
    return e


def part2_viz():
    e = [p('2.9 Visualization Deep-Dive', h2)]

    # DNA Helix
    e += [p('DNA Helix — 3D Projection Mathematics', h3),
        p('The helix uses parametric equations to place points in 3D space, then projects them to 2D SVG coordinates. With N_TURNS=3, PTS_PER_TURN=24, and RADIUS=70, the helix has 72 control points total.', body)]
    e += code_block('''// 3D → 2D projection with depth scaling
function project(x3, y3, z3, w, h) {
  const d = (z3 / RADIUS + 1) / 2;  // normalize 0–1
  return {
    sx: w/2 + x3,          // center horizontally
    sy: h/2 + y3 + z3*0.12, // slight perspective tilt
    depth: z3,
    scale: 0.7 + 0.3 * d,  // front nodes larger
    alpha: 0.5 + 0.5 * d,  // front nodes brighter
  };
}
// Strand A and B are π radians apart (opposite sides)
const xA = RADIUS * Math.cos(theta + rot);
const xB = RADIUS * Math.cos(theta + rot + Math.PI);''')
    e += [p('Gene nodes are depth-sorted before rendering (<font face="Courier">sortedRenderables</font>) to ensure correct occlusion — back nodes render first, front nodes on top. The animation loop uses <font face="Courier">requestAnimationFrame</font> incrementing rotation by <font face="Courier">dt × 0.00025</font> radians per millisecond (≈ one full rotation per ~25 seconds).', body), sp(6)]

    # Skill Tree
    e += [p('Skill Tree — D3 Force Simulation', h3),
        p('The force graph uses three D3 forces working together to produce a stable, readable layout:', body)]
    e += code_block('''d3.forceSimulation(nodes)
  .force("link",   forceLink(links).distance(90).strength(0.4–0.6))
  .force("charge", forceManyBody().strength(-220))  // repulsion
  .force("center", forceCenter(cx, cy))              // gravitational pull
  .force("collide",forceCollide(r + 6))              // no overlap''')
    e += [p('Root → Category links use strength 0.4; Category → Skill links use 0.6 (tighter clustering). Charge strength −220 keeps the graph spread out. The simulation runs until velocity drops below the alpha decay threshold, then stops to save CPU.', body), sp(6)]

    # Growth Timeline
    e += [p('Growth Timeline — D3 Stacked Area', h3),
        p('The timeline groups GrowthEvents by calendar week using <font face="Courier">d3.timeWeeks()</font>, counts new skills per category per week, then computes cumulative totals before stacking:', body)]
    e += code_block('''const stack = d3.stack()
  .keys(["LANGUAGE","FRAMEWORK","PATTERN","TOOL","CONCEPT"])
  .order(d3.stackOrderNone)
  .offset(d3.stackOffsetNone);

const area = d3.area()
  .x(d => x(d.data.date))
  .y0(d => y(d[0]))
  .y1(d => y(d[1]))
  .curve(d3.curveCatmullRom);  // smooth Catmull-Rom interpolation''')
    e += [p('A hover line tracks mouse position within the chart SVG and snaps to the nearest time scale value, providing temporal context for each data point.', body), sp(8)]
    return e

def part2_structure():
    e = [p('2.10 Project File Structure', h2)]
    tree = '''src/
├── app/                          # Next.js App Router pages
│   ├── page.tsx                  # Landing page (/)
│   ├── layout.tsx                # Root layout with providers
│   ├── globals.css               # Global Tailwind styles
│   ├── dashboard/                # Dashboard page (/dashboard)
│   │   ├── page.tsx              # Server component (auth check)
│   │   └── dashboard-client.tsx  # Client component (data fetch + UI)
│   ├── genome/
│   │   ├── page.tsx              # Personal genome (/genome) — protected
│   │   ├── genome-client.tsx     # Helix/Radar/Tree view switcher
│   │   └── [username]/           # Public profile (/genome/:username)
│   │       ├── page.tsx          # SSR with generateMetadata()
│   │       └── profile-client.tsx
│   ├── projects/                 # Projects showcase (/projects)
│   ├── growth/                   # Growth tracking (/growth)
│   ├── analysis/                 # Analysis views (/analysis, /analysis/:id)
│   ├── settings/                 # Settings page (/settings)
│   └── api/                      # API Routes
│       ├── auth/[...nextauth]/   # NextAuth handler
│       ├── repos/                # sync, list, [repoId]
│       ├── analyze/              # all, [repoId], status/[repoId]
│       ├── genome/data/          # Genome data endpoint
│       ├── score/                # Score calculation
│       ├── stats/                # Dashboard stats
│       ├── activity/             # Activity feed
│       ├── public/               # Public API (no auth)
│       │   ├── genome/[username]/
│       │   ├── skills/[username]/
│       │   ├── projects/[username]/
│       │   └── score/[username]/
│       └── widget/[username]/    # SVG widget generator
├── components/
│   ├── dashboard/                # Stat cards, charts, repo table
│   ├── genome/                   # DNA helix, radar, skill tree, table
│   ├── growth/                   # Timeline, milestones feed
│   ├── landing/                  # Hero, features, genome preview, how-it-works
│   ├── layout/                   # Navbar, footer, providers, shortcuts
│   ├── projects/                 # Project card component
│   └── ui/                       # shadcn/ui primitives (button, card, etc.)
├── lib/
│   ├── analysis.ts               # Repository analysis pipeline
│   ├── mock-analysis.ts          # Deterministic mock analysis engine
│   ├── scoring.ts                # Developer score calculation
│   ├── github.ts                 # GitHub API client (fetch, paginate, rate limit)
│   ├── auth.ts                   # NextAuth configuration
│   ├── prisma.ts                 # Prisma client singleton
│   ├── api-auth.ts               # getApiUser() helper
│   ├── rate-limit.ts             # In-memory sliding window rate limiter
│   ├── format.ts                 # Date/score formatting utilities
│   └── utils.ts                  # cn() class merge utility
├── hooks/
│   └── use-keyboard-shortcuts.ts # Global keyboard shortcut hook
├── types/
│   └── next-auth.d.ts            # NextAuth session type extensions
└── middleware.ts                 # Route protection middleware'''
    for line in tree.split('\n'):
        if line.strip():
            e += code_block(line)
    e += [sp(8)]
    return e


def part2_setup():
    e = [p('2.11 Setup &amp; Installation Guide', h2),
        p('Prerequisites:', h3),
        b('Node.js 18+ and npm'),
        b('PostgreSQL 14+ (local or hosted)'),
        b('GitHub OAuth App (create at github.com/settings/developers)'),
        b('Git'),
        sp(4), p('Step-by-Step:', h3),
        p('<b>Step 1: Clone &amp; Install</b>', body)]
    e += code_block('''git clone https://github.com/zhnverse/codedna.git
cd codedna
npm install''')
    e += [p('<b>Step 2: Configure Environment</b>', body)]
    e += code_block('''cp .env.example .env.local
# Edit .env.local with your values''')
    e += [p('<b>Step 3: Database Setup</b>', body)]
    e += code_block('''# Create PostgreSQL database
createdb codedna
# Push Prisma schema
npx prisma db push
# (Optional) Open Prisma Studio
npx prisma studio''')
    e += [p('<b>Step 4: Run Development Server</b>', body)]
    e += code_block('''npm run dev
# App available at http://localhost:3000''')
    e += [sp(6), p('Environment Variables:', h3),
        tbl([
            ['Variable','Required','Description'],
            ['DATABASE_URL','Yes','PostgreSQL connection string: postgresql://user:pass@host:5432/dbname'],
            ['GITHUB_CLIENT_ID','Yes','GitHub OAuth App Client ID (from github.com/settings/developers)'],
            ['GITHUB_CLIENT_SECRET','Yes','GitHub OAuth App Client Secret'],
            ['NEXTAUTH_SECRET','Yes','Random 32-char string — generate with: openssl rand -base64 32'],
            ['NEXTAUTH_URL','Yes','App URL: http://localhost:3000 (dev) or https://yourdomain.com (prod)'],
            ['ANTHROPIC_API_KEY','Optional','Anthropic API key — enables real AI analysis (mock used if absent)'],
        ], col_widths=[4.5*cm, 2*cm, 10*cm]),
        sp(6), p('Common Troubleshooting:', h3),
        b('<b>Cannot connect to database:</b> Ensure PostgreSQL is running — <font face="Courier">sudo systemctl start postgresql</font>'),
        b('<b>GitHub OAuth 400 error:</b> Check callback URL in GitHub OAuth App matches NEXTAUTH_URL exactly'),
        b('<b>Prisma client not found:</b> Run <font face="Courier">npx prisma generate</font> after schema changes'),
        b('<b>Port 3000 in use:</b> Kill existing process or use <font face="Courier">PORT=3001 npm run dev</font>'),
        sp(8)]
    return e

def part2_deploy():
    e = [p('2.12 Deployment Guide', h2),
        p('<b>Recommended Stack:</b> Vercel (frontend + API) + Neon (PostgreSQL)', body),
        p('Vercel Deployment:', h3),
        p('1. Push code to GitHub repository', body),
        p('2. Connect repository at vercel.com/new', body),
        p('3. Set all environment variables in Vercel dashboard (Settings → Environment Variables)', body),
        p('4. For NEXTAUTH_URL set your production domain: <font face="Courier">https://codedna.yourname.dev</font>', body),
        p('5. Vercel auto-deploys on every push to main branch', body),
        p('Database Hosting Options:', h3),
        tbl([
            ['Provider','Free Tier','Connection String Format','Notes'],
            ['Neon','0.5 GB','postgresql://user:pass@ep-xxx.neon.tech/codedna?sslmode=require','Recommended — serverless PostgreSQL'],
            ['Supabase','500 MB','postgresql://postgres:pass@db.xxx.supabase.co:5432/postgres','Great dashboard + auth'],
            ['Railway','$5/month','postgresql://user:pass@monorail.proxy.rlwy.net:port/railway','Simple, dev-friendly'],
            ['PlanetScale','MySQL only','N/A — requires schema changes','Not recommended (MySQL)'],
        ], col_widths=[2.5*cm, 2*cm, 6.5*cm, 5.5*cm]),
        sp(6), p('GitHub OAuth App for Production:', h3),
        p('Create a separate GitHub OAuth App for production with:', body),
        b('Homepage URL: https://yourdomain.com'),
        b('Callback URL: https://yourdomain.com/api/auth/callback/github'),
        sp(8)]
    return e

def part2_roadmap():
    e = [p('2.13 Future Roadmap', h2),
        tbl([
            ['Feature','Priority','Description'],
            ['Real Anthropic Integration','High','Replace mock analysis with Claude API for actual file content analysis, architecture detection, and code quality assessment'],
            ['GitHub Webhooks','High','Auto-trigger re-analysis on push events — genome updates in real-time as code is pushed'],
            ['Team / Org Dashboards','Medium','Organization-level genome showing collective skill distribution across team members'],
            ['Job Matching Engine','Medium','Match developer genome against job requirements → skill gap analysis and learning roadmap'],
            ['Real-time Collaboration','Medium','Live genome comparison between two developers — useful for team formation and peer learning'],
            ['CI/CD Integration','Medium','GitHub Action to run analysis and post genome badge to PR comments'],
            ['Mobile App','Low','React Native app for genome viewing and push notifications on level-ups'],
            ['Skill Endorsements','Low','Peer-reviewed skill validation — connect two developer genomes to cross-validate skills'],
            ['Export / PDF Report','Low','One-click PDF export of genome profile for job applications'],
        ], col_widths=[4*cm, 2*cm, 10.5*cm]),
        PageBreak()]
    return e

def appendices():
    e = [p('APPENDICES', h1), hr()]

    # Appendix A - Schema
    e += [p('Appendix A: Full schema.prisma', h2)]
    schema = open('/home/sloth/Skill/CodeDNA/prisma/schema.prisma').read()
    e += code_block(schema) + [sp(8)]

    # Appendix B - Env vars
    e += [p('Appendix B: Environment Variables Reference', h2),
        tbl([
            ['Variable','Required','Example Value','Description'],
            ['DATABASE_URL','Yes','postgresql://sloth:pass@localhost:5432/codedna','Full PostgreSQL connection string'],
            ['GITHUB_CLIENT_ID','Yes','Ov23litGPZHbMqNN4ZFD','From GitHub OAuth App settings'],
            ['GITHUB_CLIENT_SECRET','Yes','c200c7cfe91361a4fea5...','From GitHub OAuth App settings'],
            ['NEXTAUTH_SECRET','Yes','0ksXaMcxYDFk8sSrE7Oi...','32-char random secret for JWT signing'],
            ['NEXTAUTH_URL','Yes','http://localhost:3000','Full URL of the application'],
            ['ANTHROPIC_API_KEY','No','sk-ant-api03-...','Enables real AI analysis via Claude'],
        ], col_widths=[4*cm, 2*cm, 4.5*cm, 6*cm]), sp(8)]

    # Appendix C - Shortcuts
    e += [p('Appendix C: Keyboard Shortcuts', h2),
        tbl([
            ['Shortcut','Action','Notes'],
            ['G then D','Navigate to Dashboard','Two-key chord, 1-second window'],
            ['G then G','Navigate to Genome','Personal genome page'],
            ['G then P','Navigate to Projects','Project showcase'],
            ['G then R','Navigate to Growth','Growth tracking page'],
            ['G then S','Navigate to Settings','Settings and embed code'],
        ], col_widths=[4*cm, 5*cm, 7.5*cm]), sp(8)]

    # Appendix D - Dependencies
    e += [p('Appendix D: Dependencies (package.json)', h2),
        p('Production Dependencies:', h3),
        tbl([
            ['Package','Version','Purpose'],
            ['next','14.2.18','React framework with App Router'],
            ['react / react-dom','^18','UI library'],
            ['next-auth','^4.24.11','Authentication with GitHub OAuth'],
            ['@auth/prisma-adapter','^2.7.2','Prisma session storage for NextAuth'],
            ['@prisma/client','^5.22.0','Type-safe database client'],
            ['d3','^7.9.0','Data visualization (helix, radar, tree, timeline)'],
            ['next-themes','^0.4.6','Dark/light theme management'],
            ['lucide-react','^0.454.0','Icon system'],
            ['@radix-ui/*','Various','Accessible UI primitives (8 packages)'],
            ['class-variance-authority','^0.7.1','Component variant management'],
            ['clsx','^2.1.1','Conditional class names'],
            ['tailwind-merge','^2.5.4','Tailwind class deduplication'],
            ['tailwindcss-animate','^1.0.7','CSS animations'],
        ], col_widths=[5*cm, 3*cm, 8.5*cm]),
        sp(6), p('Dev Dependencies:', h3),
        tbl([
            ['Package','Version','Purpose'],
            ['typescript','^5','Type system'],
            ['prisma','^5.22.0','Schema management and migrations'],
            ['tailwindcss','^3.4.15','CSS framework'],
            ['@types/d3','^7.4.3','D3 TypeScript definitions'],
            ['eslint + eslint-config-next','8.x / 14.2.18','Code linting'],
            ['autoprefixer / postcss','Latest','CSS processing'],
        ], col_widths=[5*cm, 3*cm, 8.5*cm])]
    return e


def header_footer(canvas, doc):
    canvas.saveState()
    W, H = A4
    # Header line
    canvas.setStrokeColorRGB(0.05, 0.58, 0.53)
    canvas.setLineWidth(1.5)
    canvas.line(2*cm, H-1.8*cm, W-2*cm, H-1.8*cm)
    # Header text
    canvas.setFont('Helvetica-Bold', 8)
    canvas.setFillColorRGB(0.05, 0.58, 0.53)
    canvas.drawString(2*cm, H-1.5*cm, 'CodeDNA — AI-Powered Developer Genome Analysis Platform')
    canvas.setFont('Helvetica', 8)
    canvas.setFillColorRGB(0.39, 0.45, 0.54)
    canvas.drawRightString(W-2*cm, H-1.5*cm, 'github.com/zhnverse')
    # Footer line
    canvas.setStrokeColorRGB(0.88, 0.91, 0.94)
    canvas.line(2*cm, 1.5*cm, W-2*cm, 1.5*cm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColorRGB(0.39, 0.45, 0.54)
    canvas.drawString(2*cm, 1.1*cm, 'Portfolio & Technical Documentation | May 2026')
    canvas.drawRightString(W-2*cm, 1.1*cm, f'Page {doc.page}')
    canvas.restoreState()

def build():
    OUT = '/home/sloth/Skill/CodeDNA/CodeDNA-Report-Full.pdf'
    doc = SimpleDocTemplate(OUT, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm)

    story = []
    story += cover_page()
    story += part1()
    story += part1b()
    story += part2_arch()
    story += part2_stack()
    story += part2_schema()
    story += [PageBreak()]
    story += part2_api()
    story += [PageBreak()]
    story += part2_components()
    story += part2_engine()
    story += part2_scoring()
    story += part2_auth()
    story += part2_viz()
    story += part2_structure()
    story += part2_setup()
    story += part2_deploy()
    story += part2_roadmap()
    story += appendices()

    print(f'Building PDF → {OUT}')
    doc.build(story, onFirstPage=lambda c,d: None, onLaterPages=header_footer)
    size = os.path.getsize(OUT)
    print(f'Done! {size/1024:.1f} KB — {OUT}')

build()
