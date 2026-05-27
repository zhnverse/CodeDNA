import { NextRequest, NextResponse } from "next/server";
import { getApiUser } from "@/lib/api-auth";
import { prisma } from "@/lib/prisma";
import { calculateDeveloperScore } from "@/lib/scoring";

export async function GET(req: NextRequest) {
  const user = await getApiUser(req);
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { userId } = user;
  const score = await calculateDeveloperScore(userId);

  const skills = await prisma.skillNode.findMany({
    where: { userId },
    select: { confidence: true, category: true },
  });

  return NextResponse.json({
    score,
    breakdown: {
      analyzedRepos: await prisma.repository.count({ where: { userId, isAnalyzed: true } }),
      totalSkills: skills.length,
      mastered: skills.filter((s) => s.confidence === "MASTERED").length,
      demonstrated: skills.filter((s) => s.confidence === "DEMONSTRATED").length,
      claimed: skills.filter((s) => s.confidence === "CLAIMED").length,
    },
  });
}
