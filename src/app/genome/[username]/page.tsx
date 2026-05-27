import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { prisma } from "@/lib/prisma";
import { PublicProfileClient } from "./profile-client";

interface Props {
  params: { username: string };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const user = await prisma.user.findFirst({
    where: { username: params.username },
    select: { username: true, developerScore: true },
  });

  if (!user) return { title: "Profile not found — CodeDNA" };

  return {
    title: `@${user.username} — CodeDNA`,
    description: `Developer genome profile for @${user.username}. Score: ${user.developerScore ?? 0}/100. Explore their skills, projects, and growth trajectory.`,
    openGraph: {
      title: `@${user.username} on CodeDNA`,
      description: `Developer score: ${user.developerScore ?? 0}/100`,
      images: [`/api/widget/${user.username}`],
    },
    twitter: {
      card: "summary",
      title: `@${user.username} on CodeDNA`,
      description: `Developer score: ${user.developerScore ?? 0}/100`,
      images: [`/api/widget/${user.username}`],
    },
  };
}

export default async function PublicProfilePage({ params }: Props) {
  const user = await prisma.user.findFirst({
    where: { username: params.username },
    select: {
      id: true, username: true, avatar: true, developerScore: true,
    },
  });

  if (!user) notFound();

  const [skills, repos] = await Promise.all([
    prisma.skillNode.findMany({
      where: { userId: user.id },
      select: { name: true, category: true, proficiencyScore: true, confidence: true },
      orderBy: { proficiencyScore: "desc" },
    }),
    prisma.repository.findMany({
      where: { userId: user.id, isAnalyzed: true, isPrivate: false },
      select: {
        id: true, name: true, url: true, primaryLanguage: true, stars: true, forks: true,
        complexityScore: true, analysisData: true,
      },
      orderBy: { stars: "desc" },
      take: 10,
    }),
  ]);

  return (
    <PublicProfileClient
      username={user.username ?? params.username}
      name={null}
      avatar={user.avatar}
      developerScore={user.developerScore ?? 0}
      skills={skills}
      projects={repos}
    />
  );
}
