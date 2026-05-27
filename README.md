# CodeDNA — Your Developer Genome

> Connect GitHub. See your true developer genome. Analyze your code, track your growth, showcase your skills.

CodeDNA is a full-stack Next.js application that analyzes your GitHub repositories to build a living developer genome — a visual fingerprint of your skills, patterns, and growth trajectory.

---

## Features

### Genome Visualization
- **3D DNA Helix** — animated SVG helix where each rung represents a detected skill
- **Radar Chart** — pentagon view across 5 skill categories
- **Force-Directed Skill Tree** — D3 force simulation showing skill relationships

### Code Analysis Engine
- Deterministic mock analysis engine (no external AI API needed)
- Detects languages, frameworks, patterns, tools, and concepts from repo metadata
- Produces quality scores, complexity scores, and architecture type classification
- Growth events (NEW_SKILL, LEVEL_UP, MILESTONE) with a timestamped timeline

### Developer Score
Weighted scoring formula:
- Quality × 0.30 — average code quality across repos
- Breadth × 0.20 — number of distinct skill categories
- Depth × 0.20 — average proficiency depth
- Consistency × 0.15 — sustained activity over time
- Growth × 0.15 — new skills in the last 30 days

### Growth Tracking
- Stacked area timeline by skill category per week
- Milestone feed with event icons
- Predicted next skills based on skill adjacency graph
- Achievements: Polyglot, Full Stack, Quality First, Prolific, Speed Learner

### Public Profiles
- Shareable profile at `/genome/[username]`
- Embeddable SVG widget card via `/api/widget/[username]`
- REST API for external integrations (rate-limited: 100 req/hour)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 14 App Router |
| Auth | NextAuth.js v4 (GitHub OAuth) |
| Database | PostgreSQL 18 + Prisma ORM |
| Charts | D3.js (SVG-based, no canvas) |
| Styling | Tailwind CSS + shadcn/ui |
| Language | TypeScript |

No external AI API keys required — analysis is fully local and deterministic.

---

## Getting Started

### Prerequisites
- Node.js 18+
- PostgreSQL running locally
- GitHub OAuth App

### Setup

```bash
git clone <repo>
cd CodeDNA
npm install
```

Copy `.env.local.example` to `.env.local` and fill in:

```env
DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/codedna"
GITHUB_CLIENT_ID="your-client-id"
GITHUB_CLIENT_SECRET="your-client-secret"
NEXTAUTH_SECRET="run: openssl rand -base64 32"
NEXTAUTH_URL="http://localhost:3000"
```

```bash
npx prisma migrate dev
npm run dev
```

Open [http://localhost:3000](http://localhost:3000), sign in with GitHub, and click **Sync Repos** to start.

---

## Public API

All endpoints are rate-limited to 100 requests/hour per IP and return CORS headers.

| Endpoint | Description |
|---|---|
| `GET /api/public/genome/[username]` | Full genome summary |
| `GET /api/public/skills/[username]` | Skills list + by-category breakdown |
| `GET /api/public/projects/[username]` | Analyzed public repos |
| `GET /api/public/score/[username]` | Developer score |
| `GET /api/widget/[username]` | SVG badge card (400×320) |

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `g` then `d` | Go to Dashboard |
| `g` then `g` | Go to Genome |
| `g` then `p` | Go to Projects |
| `g` then `r` | Go to Growth |
| `g` then `s` | Go to Settings |

---

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── api/               # API routes
│   │   ├── analyze/       # Repo analysis endpoints
│   │   ├── public/        # Public read-only API
│   │   └── widget/        # SVG widget generator
│   ├── analysis/[repoId]/ # Deep-dive repo page
│   ├── dashboard/         # Main dashboard
│   ├── genome/            # Authenticated genome view
│   │   └── [username]/    # Public profile page
│   ├── growth/            # Growth timeline + achievements
│   ├── projects/          # Projects grid
│   └── settings/          # Account settings + embed codes
├── components/
│   ├── genome/            # DNA helix, radar, skill tree, table
│   ├── growth/            # Timeline, milestones feed
│   ├── dashboard/         # Repo table, stats cards
│   ├── projects/          # Project card
│   └── layout/            # Navbar, footer, providers, shortcuts
├── lib/
│   ├── analysis.ts        # Full analysis pipeline
│   ├── mock-analysis.ts   # Deterministic mock engine
│   ├── scoring.ts         # Developer score calculator
│   ├── rate-limit.ts      # In-memory rate limiter
│   └── auth.ts            # NextAuth config
└── hooks/
    └── use-keyboard-shortcuts.ts
```

---

## License

MIT
