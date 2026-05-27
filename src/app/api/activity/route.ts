import { NextRequest, NextResponse } from "next/server";
import { getApiUser } from "@/lib/api-auth";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest) {
  const user = await getApiUser(req);
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const events = await prisma.growthEvent.findMany({
    where: { userId: user.userId },
    orderBy: { createdAt: "desc" },
    take: 10,
    include: { skillNode: { select: { name: true, category: true } } },
  });

  return NextResponse.json(events);
}
