import { MetadataRoute } from "next";
import { prisma } from "@/lib/prisma";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXTAUTH_URL ?? "http://localhost:3000";

  const users = await prisma.user.findMany({
    where: { skillNodes: { some: {} } },
    select: { username: true, updatedAt: true },
    take: 1000,
  });

  const profileUrls: MetadataRoute.Sitemap = users
    .filter((u) => u.username)
    .map((u) => ({
      url: `${baseUrl}/genome/${u.username}`,
      lastModified: u.updatedAt,
      changeFrequency: "weekly",
      priority: 0.7,
    }));

  return [
    { url: baseUrl, lastModified: new Date(), changeFrequency: "weekly", priority: 1 },
    ...profileUrls,
  ];
}
