import { prisma } from "./prisma";

export async function calculateDeveloperScore(userId: string): Promise<number> {
  const ninetyDaysAgo = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

  const [analyzedRepos, skills, recentRepos, growthEvents] = await Promise.all([
    prisma.repository.findMany({
      where: { userId, isAnalyzed: true },
      select: { analysisData: true },
    }),
    prisma.skillNode.findMany({
      where: { userId },
      select: { confidence: true, category: true },
    }),
    prisma.repository.count({ where: { userId, lastAnalyzedAt: { gte: thirtyDaysAgo } } }),
    prisma.growthEvent.count({ where: { userId, createdAt: { gte: ninetyDaysAgo } } }),
  ]);

  if (analyzedRepos.length === 0 && skills.length === 0) {
    await prisma.user.update({ where: { id: userId }, data: { developerScore: 0 } });
    return 0;
  }

  // Quality (30%): avg overallQuality across analyzed repos
  const qualities = analyzedRepos
    .map((r) => ((r.analysisData as Record<string, unknown> | null)?.qualityIndicators as Record<string, number> | undefined)?.overallQuality ?? 0)
    .filter((q) => q > 0);
  const qualityScore = qualities.length > 0 ? qualities.reduce((a, b) => a + b, 0) / qualities.length : 0;

  // Breadth (20%): skill count + category diversity
  const categories = new Set(skills.map((s) => s.category)).size;
  const breadth = Math.min(skills.length * 3 + categories * 5, 100);

  // Depth (20%): weighted by confidence
  const mastered = skills.filter((s) => s.confidence === "MASTERED").length;
  const demonstrated = skills.filter((s) => s.confidence === "DEMONSTRATED").length;
  const claimed = skills.filter((s) => s.confidence === "CLAIMED").length;
  const depth = Math.min((mastered * 3 + demonstrated * 2 + claimed) * 4, 100);

  // Consistency (15%): repos analyzed + recency
  const consistency = Math.min(analyzedRepos.length * 8 + recentRepos * 5, 100);

  // Growth (15%): growth events last 90 days
  const growth = Math.min(growthEvents * 5, 100);

  const raw = qualityScore * 0.3 + breadth * 0.2 + depth * 0.2 + consistency * 0.15 + growth * 0.15;
  const score = Math.min(Math.max(Math.round(raw), 0), 100);

  await prisma.user.update({ where: { id: userId }, data: { developerScore: score } });
  return score;
}
