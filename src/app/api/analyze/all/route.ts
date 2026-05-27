import { NextRequest, NextResponse } from "next/server";
import { getApiUser } from "@/lib/api-auth";
import { prisma } from "@/lib/prisma";
import { analyzeRepository } from "@/lib/analysis";

export async function POST(req: NextRequest) {
  const user = await getApiUser(req);
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { userId, accessToken } = user;

  const repos = await prisma.repository.findMany({
    where: { userId, isAnalyzed: false },
    select: { id: true, analysisData: true },
  });

  const toRun = repos.filter((r) => {
    const d = r.analysisData as Record<string, unknown> | null;
    return d?.status !== "fetching" && d?.status !== "analyzing";
  });

  if (toRun.length === 0) {
    return NextResponse.json({ status: "nothing_to_analyze", count: 0 });
  }

  async function runSequential() {
    for (const repo of toRun) {
      try {
        await analyzeRepository(userId, repo.id, accessToken);
      } catch (e) {
        console.error("[analyze/all] repo failed:", repo.id, e);
      }
    }
  }

  runSequential().catch(console.error);

  return NextResponse.json({ status: "started", count: toRun.length });
}
