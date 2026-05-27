import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { GenomeClient } from "./genome-client";

export default async function GenomePage() {
  const session = await getServerSession(authOptions);
  if (!session) redirect("/");

  const userId = session.user.userId;

  const [skills, user] = await Promise.all([
    prisma.skillNode.findMany({
      where: { userId },
      orderBy: { proficiencyScore: "desc" },
      select: { id: true, name: true, category: true, proficiencyScore: true, confidence: true, firstSeen: true, lastSeen: true, evidence: true },
    }),
    prisma.user.findUnique({ where: { id: userId }, select: { developerScore: true, username: true } }),
  ]);

  return (
    <div className="container py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Genome</h1>
        <p className="text-muted-foreground text-sm mt-1">Your developer DNA, visualized.</p>
      </div>
      <GenomeClient
        skills={skills.map((s) => ({ ...s, firstSeen: s.firstSeen.toISOString(), lastSeen: s.lastSeen.toISOString() }))}
        score={user?.developerScore ?? 0}
        username={user?.username ?? session.user.username}
      />
    </div>
  );
}
