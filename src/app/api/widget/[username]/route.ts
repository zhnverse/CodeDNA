import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { rateLimit, rateLimitHeaders } from "@/lib/rate-limit";

const CAT_COLORS: Record<string, string> = {
  LANGUAGE: "#3B82F6",
  FRAMEWORK: "#10B981",
  PATTERN: "#F59E0B",
  TOOL: "#8B5CF6",
  CONCEPT: "#06B6D4",
};

function scoreColor(score: number) {
  if (score >= 70) return "#00ff88";
  if (score >= 40) return "#FBBF24";
  return "#EF4444";
}

function scoreLabel(score: number) {
  if (score >= 80) return "Expert";
  if (score >= 60) return "Advanced";
  if (score >= 40) return "Intermediate";
  return "Learning";
}

export async function GET(req: NextRequest, { params }: { params: { username: string } }) {
  const ip = req.headers.get("x-forwarded-for") ?? "anon";
  const rl = rateLimit(ip, 60);
  if (!rl.allowed) {
    return new NextResponse("Rate limit exceeded", { status: 429 });
  }

  const user = await prisma.user.findFirst({
    where: { username: params.username },
    select: { id: true, username: true, avatar: true, developerScore: true },
  });

  if (!user) {
    return new NextResponse("Not found", { status: 404 });
  }

  const skills = await prisma.skillNode.findMany({
    where: { userId: user.id },
    select: { name: true, category: true, proficiencyScore: true },
    orderBy: { proficiencyScore: "desc" },
    take: 10,
  });

  const score = user.developerScore ?? 0;
  const color = scoreColor(score);
  const label = scoreLabel(score);
  const topSkills = skills.slice(0, 5);

  const skillBars = topSkills.map((s, i) => {
    const y = 170 + i * 28;
    const barW = Math.round((s.proficiencyScore / 100) * 220);
    const c = CAT_COLORS[s.category] ?? "#888";
    return `
      <text x="20" y="${y + 10}" fill="#94a3b8" font-size="11" font-family="Inter,sans-serif">${s.name}</text>
      <rect x="140" y="${y}" width="${barW}" height="10" rx="5" fill="${c}" opacity="0.7"/>
      <text x="368" y="${y + 10}" fill="#64748b" font-size="10" font-family="Inter,sans-serif" text-anchor="end">${s.proficiencyScore}</text>
    `;
  }).join("");

  const circumference = 2 * Math.PI * 36;
  const dash = (score / 100) * circumference;

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="320" viewBox="0 0 400 320">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="400" height="320" rx="16" fill="url(#bg)" stroke="#334155" stroke-width="1"/>

  <!-- Header -->
  <text x="20" y="32" fill="#f1f5f9" font-size="13" font-weight="700" font-family="Inter,sans-serif">CodeDNA</text>
  <text x="20" y="52" fill="#94a3b8" font-size="11" font-family="Inter,sans-serif">Developer Genome Profile</text>

  <!-- Username -->
  <text x="20" y="90" fill="#f1f5f9" font-size="18" font-weight="700" font-family="Inter,sans-serif">@${user.username}</text>

  <!-- Score ring -->
  <circle cx="352" cy="70" r="36" fill="none" stroke="#1e293b" stroke-width="8"/>
  <circle cx="352" cy="70" r="36" fill="none" stroke="${color}" stroke-width="8"
    stroke-dasharray="${dash.toFixed(1)} ${circumference.toFixed(1)}"
    stroke-dashoffset="${(circumference / 4).toFixed(1)}"
    stroke-linecap="round"
    filter="url(#glow)"/>
  <text x="352" y="66" fill="${color}" font-size="20" font-weight="700" font-family="Inter,sans-serif" text-anchor="middle">${score}</text>
  <text x="352" y="82" fill="#64748b" font-size="9" font-family="Inter,sans-serif" text-anchor="middle">${label}</text>

  <!-- Skills section -->
  <text x="20" y="152" fill="#475569" font-size="10" font-weight="600" font-family="Inter,sans-serif" text-transform="uppercase" letter-spacing="1">TOP SKILLS</text>

  ${skillBars}

  <!-- Footer -->
  <text x="20" y="306" fill="#334155" font-size="9" font-family="Inter,sans-serif">codedna.dev/${user.username}</text>
  <text x="380" y="306" fill="#334155" font-size="9" font-family="Inter,sans-serif" text-anchor="end">${skills.length} skills detected</text>
</svg>`;

  return new NextResponse(svg, {
    headers: {
      "Content-Type": "image/svg+xml",
      "Cache-Control": "public, max-age=3600, s-maxage=3600",
      ...rateLimitHeaders(rl),
    },
  });
}
