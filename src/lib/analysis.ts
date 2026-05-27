import { prisma } from "./prisma";
import { fetchRepoTree } from "./github";
import { mockAnalyzeRepo } from "./mock-analysis";
import { calculateDeveloperScore } from "./scoring";

const PROFICIENCY_SCORES: Record<string, number> = {
  beginner: 25,
  intermediate: 50,
  advanced: 75,
  expert: 95,
};

const PATTERN_TYPE_MAP: Record<string, "ARCHITECTURE"|"ERROR_HANDLING"|"TESTING"|"API_DESIGN"|"STATE_MANAGEMENT"|"NAMING_CONVENTION"> = {
  architecture:       "ARCHITECTURE",
  error_handling:     "ERROR_HANDLING",
  testing:            "TESTING",
  api_design:         "API_DESIGN",
  state_management:   "STATE_MANAGEMENT",
  naming_convention:  "NAMING_CONVENTION",
};

export async function analyzeRepository(
  userId: string,
  repoId: string,
  accessToken: string
): Promise<void> {
  const repo = await prisma.repository.findUnique({ where: { id: repoId } });
  if (!repo) throw new Error("Repository not found");

  try {
    await prisma.repository.update({
      where: { id: repoId },
      data: { isAnalyzed: false, analysisData: { status: "fetching" } as never },
    });

    // Try to fetch file tree; if it fails we proceed with metadata only
    try {
      const [owner, repoName] = repo.fullName.split("/");
      await fetchRepoTree(accessToken, owner, repoName);
    } catch {
      // non-fatal
    }

    await prisma.repository.update({
      where: { id: repoId },
      data: { analysisData: { status: "analyzing" } as never },
    });

    const result = mockAnalyzeRepo({
      name: repo.name,
      description: repo.description,
      primaryLanguage: repo.primaryLanguage,
      stars: repo.stars,
      forks: repo.forks,
      size: repo.size,
    });

    const now = new Date();

    await prisma.repository.update({
      where: { id: repoId },
      data: {
        isAnalyzed: true,
        lastAnalyzedAt: now,
        complexityScore: result.complexityScore,
        analysisData: { status: "complete", ...result } as never,
      },
    });

    // Count analyzed repos for confidence calculation
    const analyzedCount = await prisma.repository.count({ where: { userId, isAnalyzed: true } });
    const confidence = analyzedCount > 5 ? "MASTERED" : analyzedCount > 2 ? "DEMONSTRATED" : "CLAIMED";

    // Upsert SkillNodes
    for (const skill of result.skillsDemonstrated) {
      const newScore = PROFICIENCY_SCORES[skill.proficiency] ?? 50;
      const existing = await prisma.skillNode.findUnique({
        where: { userId_name: { userId, name: skill.skill } },
      });

      if (existing) {
        const leveled = newScore > existing.proficiencyScore;
        const evidence = Array.isArray(existing.evidence)
          ? [...(existing.evidence as string[]), skill.evidence].slice(-10)
          : [skill.evidence];

        await prisma.skillNode.update({
          where: { id: existing.id },
          data: {
            proficiencyScore: leveled ? newScore : existing.proficiencyScore,
            confidence,
            evidence: evidence as never,
            lastSeen: now,
          },
        });

        if (leveled) {
          await prisma.growthEvent.create({
            data: {
              userId,
              skillNodeId: existing.id,
              eventType: "LEVEL_UP",
              title: `Leveled up ${skill.skill}`,
              description: `Proficiency raised to ${skill.proficiency} via ${repo.name}`,
            },
          });
        }
      } else {
        const node = await prisma.skillNode.create({
          data: {
            userId,
            name: skill.skill,
            category: skill.category as never,
            proficiencyScore: newScore,
            confidence,
            evidence: [skill.evidence] as never,
            firstSeen: now,
            lastSeen: now,
          },
        });

        await prisma.growthEvent.create({
          data: {
            userId,
            skillNodeId: node.id,
            eventType: "NEW_SKILL",
            title: `Discovered ${skill.skill}`,
            description: `New skill found in ${repo.name}`,
          },
        });
      }
    }

    // Upsert CodePatterns
    for (const pattern of result.codePatterns) {
      const patternType = PATTERN_TYPE_MAP[pattern.type];
      if (!patternType) continue;

      const existing = await prisma.codePattern.findFirst({
        where: { userId, repoId, patternType },
      });

      if (existing) {
        await prisma.codePattern.update({
          where: { id: existing.id },
          data: { description: pattern.description, qualityScore: pattern.quality, frequency: existing.frequency + 1 },
        });
      } else {
        await prisma.codePattern.create({
          data: { userId, repoId, patternType, description: pattern.description, qualityScore: pattern.quality },
        });
      }
    }

    // GenomeSnapshot
    const allSkills = await prisma.skillNode.findMany({
      where: { userId },
      select: { name: true, category: true, proficiencyScore: true, confidence: true },
    });

    const grouped = allSkills.reduce<Record<string, typeof allSkills>>((acc, s) => {
      (acc[s.category] ??= []).push(s);
      return acc;
    }, {});

    const topCategory = Object.entries(grouped).sort((a, b) => b[1].length - a[1].length)[0]?.[0] ?? null;

    await prisma.genomeSnapshot.create({
      data: {
        userId,
        genomeData: grouped as never,
        totalSkills: allSkills.length,
        topCategory,
      },
    });

    await calculateDeveloperScore(userId);

  } catch (err) {
    console.error(`[analysis] repo ${repoId} failed:`, err);
    await prisma.repository.update({
      where: { id: repoId },
      data: { analysisData: { status: "error", error: String(err) } as never },
    });
  }
}
