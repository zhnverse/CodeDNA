import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { rateLimit, rateLimitHeaders } from "@/lib/rate-limit";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

export async function OPTIONS() {
  return new NextResponse(null, { status: 204, headers: CORS });
}

export async function GET(req: NextRequest, { params }: { params: { username: string } }) {
  const ip = req.headers.get("x-forwarded-for") ?? "anon";
  const rl = rateLimit(ip);
  if (!rl.allowed) {
    return NextResponse.json({ error: "Rate limit exceeded" }, {
      status: 429,
      headers: { ...CORS, ...rateLimitHeaders(rl) },
    });
  }

  const user = await prisma.user.findFirst({
    where: { username: params.username },
    select: { id: true, developerScore: true, username: true },
  });

  if (!user) {
    return NextResponse.json({ error: "User not found" }, { status: 404, headers: CORS });
  }

  const [skillCount, repoCount] = await Promise.all([
    prisma.skillNode.count({ where: { userId: user.id } }),
    prisma.repository.count({ where: { userId: user.id, isAnalyzed: true } }),
  ]);

  return NextResponse.json({
    username: user.username,
    developerScore: user.developerScore ?? 0,
    skillCount,
    reposAnalyzed: repoCount,
  }, { headers: { ...CORS, ...rateLimitHeaders(rl) } });
}
