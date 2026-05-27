import { NextRequest, NextResponse } from "next/server";
import { getApiUser } from "@/lib/api-auth";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest) {
  const user = await getApiUser(req);
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const repos = await prisma.repository.findMany({
    where: { userId: user.userId },
    orderBy: { updatedAt: "desc" },
    select: {
      id: true,
      name: true,
      fullName: true,
      url: true,
      description: true,
      primaryLanguage: true,
      languages: true,
      stars: true,
      forks: true,
      size: true,
      isPrivate: true,
      isAnalyzed: true,
      lastAnalyzedAt: true,
      complexityScore: true,
      createdAt: true,
      updatedAt: true,
    },
  });

  return NextResponse.json(repos);
}
