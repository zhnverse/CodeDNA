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
    select: {
      id: true, username: true, avatar: true,
      developerScore: true, createdAt: true,
    },
  });

  if (!user) {
    return NextResponse.json({ error: "User not found" }, { status: 404, headers: CORS });
  }

  const [skillNodes, repoCount] = await Promise.all([
    prisma.skillNode.findMany({
      where: { userId: user.id },
      select: { name: true, category: true, proficiencyScore: true, confidence: true },
      orderBy: { proficiencyScore: "desc" },
    }),
    prisma.repository.count({ where: { userId: user.id, isAnalyzed: true } }),
  ]);

  return NextResponse.json({
    username: user.username,
    avatar: user.avatar,
    developerScore: user.developerScore,
    skillCount: skillNodes.length,
    reposAnalyzed: repoCount,
    skills: skillNodes,
    memberSince: user.createdAt,
  }, { headers: { ...CORS, ...rateLimitHeaders(rl) } });
}
