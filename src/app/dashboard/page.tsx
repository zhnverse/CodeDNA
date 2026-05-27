import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { DashboardClient } from "./dashboard-client";

export default async function DashboardPage() {
  const session = await getServerSession(authOptions);
  if (!session) redirect("/");

  const userId = session.user.userId;
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

  const [repos, skillCount, dbUser, growthVelocity, langGroups, topSkills, events] =
    await Promise.all([
      prisma.repository.findMany({
        where: { userId },
        orderBy: { updatedAt: "desc" },
        select: {
          id: true, name: true, fullName: true, url: true,
          primaryLanguage: true, stars: true, forks: true,
          isPrivate: true, isAnalyzed: true, lastAnalyzedAt: true,
          complexityScore: true,
        },
      }),
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
        select: { name: true, proficiencyScore: true },
      }),
      prisma.growthEvent.findMany({
        where: { userId },
        orderBy: { createdAt: "desc" },
        take: 10,
        include: { skillNode: { select: { name: true, category: true } } },
      }),
    ]);

  const initialStats = {
    analyzedRepos: repos.filter((r) => r.isAnalyzed).length,
    skillCount,
    developerScore: dbUser?.developerScore ?? 0,
    growthVelocity,
    languageBreakdown: langGroups
      .filter((l) => l.primaryLanguage)
      .map((l) => ({ language: l.primaryLanguage!, count: l._count.primaryLanguage })),
    topSkills: topSkills.map((s) => ({ axis: s.name, value: s.proficiencyScore })),
  };

  const initialRepos = repos.map((r) => ({
    ...r,
    lastAnalyzedAt: r.lastAnalyzedAt?.toISOString() ?? null,
  }));

  const initialActivity = events.map((e) => ({
    ...e,
    createdAt: e.createdAt.toISOString(),
  }));

  return (
    <DashboardClient
      username={session.user.username}
      initialStats={initialStats}
      initialRepos={initialRepos}
      initialActivity={initialActivity}
    />
  );
}
