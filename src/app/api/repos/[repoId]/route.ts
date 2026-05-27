import { NextRequest, NextResponse } from "next/server";
import { getApiUser } from "@/lib/api-auth";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest, { params }: { params: { repoId: string } }) {
  const user = await getApiUser(req);
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const repo = await prisma.repository.findFirst({
    where: { id: params.repoId, userId: user.userId },
    include: { codePatterns: true },
  });

  if (!repo) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(repo);
}
