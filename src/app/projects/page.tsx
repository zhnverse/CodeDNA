import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { ProjectsClient } from "./projects-client";

export default async function ProjectsPage() {
  const session = await getServerSession(authOptions);
  if (!session) redirect("/");

  const repos = await prisma.repository.findMany({
    where: { userId: session.user.userId, isAnalyzed: true },
    orderBy: { lastAnalyzedAt: "desc" },
    select: {
      id: true, name: true, fullName: true, url: true, description: true,
      primaryLanguage: true, stars: true, forks: true, isPrivate: true,
      complexityScore: true, analysisData: true, lastAnalyzedAt: true,
    },
  });

  return (
    <div className="container py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Projects</h1>
        <p className="text-muted-foreground text-sm mt-1">Your analyzed repositories.</p>
      </div>
      <ProjectsClient repos={repos.map((r) => ({ ...r, lastAnalyzedAt: r.lastAnalyzedAt?.toISOString() ?? null }))} />
    </div>
  );
}
