import { NextRequest, NextResponse } from "next/server";
import { getApiUser } from "@/lib/api-auth";
import { prisma } from "@/lib/prisma";
import { analyzeRepository } from "@/lib/analysis";

export async function POST(req: NextRequest, { params }: { params: { repoId: string } }) {
  const user = await getApiUser(req);
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { userId, accessToken } = user;
  const { repoId } = params;

  const repo = await prisma.repository.findFirst({
    where: { id: repoId, userId },
    select: { id: true, analysisData: true },
  });
  if (!repo) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const current = repo.analysisData as Record<string, unknown> | null;
  if (current?.status === "fetching" || current?.status === "analyzing") {
    return NextResponse.json({ error: "Analysis already in progress" }, { status: 409 });
  }

  analyzeRepository(userId, repoId, accessToken).catch(console.error);

  return NextResponse.json({ status: "started", repoId });
}
