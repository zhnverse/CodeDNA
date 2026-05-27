import { NextRequest, NextResponse } from "next/server";
import { getApiUser } from "@/lib/api-auth";
import { prisma } from "@/lib/prisma";
import { fetchUserRepos } from "@/lib/github";

export async function POST(req: NextRequest) {
  const user = await getApiUser(req);
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { userId, accessToken } = user;
  if (!accessToken) return NextResponse.json({ error: "No GitHub token" }, { status: 400 });

  let githubRepos;
  try {
    githubRepos = await fetchUserRepos(accessToken);
  } catch {
    return NextResponse.json({ error: "GitHub API error" }, { status: 502 });
  }

  let created = 0;
  let updated = 0;

  await Promise.all(
    githubRepos.map(async (repo) => {
      const existing = await prisma.repository.findUnique({
        where: { githubRepoId: String(repo.id) },
        select: { id: true },
      });

      const payload = {
        userId,
        githubRepoId: String(repo.id),
        name: repo.name,
        fullName: repo.full_name,
        url: repo.html_url,
        description: repo.description ?? null,
        primaryLanguage: repo.language ?? null,
        stars: repo.stargazers_count,
        forks: repo.forks_count,
        size: repo.size,
        isPrivate: repo.private,
      };

      await prisma.repository.upsert({
        where: { githubRepoId: String(repo.id) },
        create: payload,
        update: {
          name: payload.name,
          description: payload.description,
          primaryLanguage: payload.primaryLanguage,
          stars: payload.stars,
          forks: payload.forks,
          size: payload.size,
          isPrivate: payload.isPrivate,
        },
      });

      if (existing) updated++;
      else created++;
    })
  );

  return NextResponse.json({ total: githubRepos.length, created, updated });
}
