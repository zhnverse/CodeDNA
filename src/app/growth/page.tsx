import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { GrowthClient } from "./growth-client";

export default async function GrowthPage() {
  const session = await getServerSession(authOptions);
  if (!session) redirect("/");

  const userId = session.user.userId;
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

  const [events, skills, user, recentCount] = await Promise.all([
    prisma.growthEvent.findMany({
      where: { userId },
      orderBy: { createdAt: "desc" },
      take: 50,
      include: { skillNode: { select: { name: true, category: true } } },
    }),
    prisma.skillNode.findMany({
      where: { userId },
      select: { id: true, name: true, category: true, proficiencyScore: true, confidence: true, firstSeen: true },
    }),
    prisma.user.findUnique({ where: { id: userId }, select: { developerScore: true } }),
    prisma.growthEvent.count({ where: { userId, createdAt: { gte: thirtyDaysAgo } } }),
  ]);

  return (
    <div className="container py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Growth</h1>
        <p className="text-muted-foreground text-sm mt-1">Your skill progression over time.</p>
      </div>
      <GrowthClient
        events={events.map((e) => ({ ...e, createdAt: e.createdAt.toISOString() }))}
        skills={skills.map((s) => ({ ...s, firstSeen: s.firstSeen.toISOString() }))}
        score={user?.developerScore ?? 0}
        growthVelocity={recentCount}
      />
    </div>
  );
}
