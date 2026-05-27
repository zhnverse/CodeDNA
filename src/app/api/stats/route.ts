import { NextRequest, NextResponse } from "next/server";
import { getApiUser } from "@/lib/api-auth";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest) {
  const user = await getApiUser(req);
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { userId } = user;
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

  const [analyzedCount, skillCount, dbUser, growthVelocity, languageBreakdown, topSkills] =
    await Promise.all([
      prisma.repository.count({ where: { userId, isAnalyzed: true } }),
      prisma.skillNode.count({ where: { userId } }),
      prisma.user.findUnique({ where: { id: userId }, select: { developerScore: true } }),
      prisma.growthEvent.count({ where: { userId, createdAt: { gte: thirtyDaysAgo } } }),
      prisma.repository.groupBy({
        by: ["primaryLanguage"],
        where: { userId, primaryLanguage: { not: null } },
        _count: { primaryLanguage: true },
        orderBy: { _count: { primaryLanguage: "desc" } },
        take: 10,
      }),
      prisma.skillNode.findMany({
        where: { userId },
        orderBy: { proficiencyScore: "desc" },
        take: 10,
        select: { name: true, proficiencyScore: true, category: true },
      }),
    ]);

  return NextResponse.json({
    analyzedRepos: analyzedCount,
    skillCount,
    developerScore: dbUser?.developerScore ?? 0,
    growthVelocity,
    languageBreakdown: languageBreakdown
      .filter((l) => l.primaryLanguage)
      .map((l) => ({ language: l.primaryLanguage!, count: l._count.primaryLanguage })),
    topSkills: topSkills.map((s) => ({ axis: s.name, value: s.proficiencyScore })),
  });
}
