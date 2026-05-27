import { NextRequest, NextResponse } from "next/server";
import { getApiUser } from "@/lib/api-auth";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest, { params }: { params: { repoId: string } }) {
  const user = await getApiUser(req);
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const repo = await prisma.repository.findFirst({
    where: { id: params.repoId, userId: user.userId },
    select: { id: true, name: true, isAnalyzed: true, analysisData: true, lastAnalyzedAt: true, complexityScore: true },
  });

  if (!repo) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const data = repo.analysisData as Record<string, unknown> | null;
  const status = data?.status ?? (repo.isAnalyzed ? "complete" : "idle");

  return NextResponse.json({
    repoId: repo.id,
    name: repo.name,
    status,
    isAnalyzed: repo.isAnalyzed,
    lastAnalyzedAt: repo.lastAnalyzedAt,
    complexityScore: repo.complexityScore,
  });
}
