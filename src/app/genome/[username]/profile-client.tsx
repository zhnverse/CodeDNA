"use client";

import { useState } from "react";
import { useTheme } from "next-themes";
import { Star, GitFork, Globe, Award, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DNAHelix } from "@/components/genome/dna-helix";
import { GenomeRadar } from "@/components/genome/genome-radar";
import { SkillTree } from "@/components/genome/skill-tree";
import { cn } from "@/lib/utils";

interface Skill {
  name: string;
  category: string;
  proficiencyScore: number;
  confidence: string;
  evidence?: unknown;
}

interface Project {
  id: string;
  name: string;
  url: string;
  primaryLanguage: string | null;
  stars: number;
  forks: number;
  complexityScore: number | null;
  analysisData: unknown;
}

interface Props {
  username: string;
  name: string | null;
  avatar: string | null;
  developerScore: number;
  skills: Skill[];
  projects: Project[];
}

const CAT_COLORS: Record<string, string> = {
  LANGUAGE: "bg-blue-500/20 text-blue-600 dark:text-blue-400",
  FRAMEWORK: "bg-emerald-500/20 text-emerald-600 dark:text-emerald-400",
  PATTERN: "bg-amber-500/20 text-amber-700 dark:text-amber-400",
  TOOL: "bg-purple-500/20 text-purple-600 dark:text-purple-400",
  CONCEPT: "bg-cyan-500/20 text-cyan-600 dark:text-cyan-400",
};

type View = "helix" | "radar" | "tree";

export function PublicProfileClient({ username, name, avatar, developerScore, skills, projects }: Props) {
  const [view, setView] = useState<View>("helix");
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme !== "light";

  const scoreColor = developerScore >= 70 ? "text-dna-green" : developerScore >= 40 ? "text-yellow-600 dark:text-yellow-400" : "text-red-500 dark:text-red-400";
  const scoreStroke = developerScore >= 70 ? "#00ff88" : developerScore >= 40 ? (isDark ? "#FBBF24" : "#ca8a04") : (isDark ? "#EF4444" : "#dc2626");
  const circumference = 2 * Math.PI * 44;
  const dash = (developerScore / 100) * circumference;

  const topSkills = [...skills].sort((a, b) => b.proficiencyScore - a.proficiencyScore).slice(0, 8);

  const catCounts = skills.reduce<Record<string, number>>((acc, s) => {
    acc[s.category] = (acc[s.category] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <div className="border-b border-border/40 bg-card/30">
        <div className="container max-w-5xl py-12">
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
            {avatar ? (
              <img src={avatar} alt={username} className="w-24 h-24 rounded-full border-2 border-dna-green/30 ring-4 ring-background" />
            ) : (
              <div className="w-24 h-24 rounded-full bg-dna-green/20 flex items-center justify-center text-3xl font-bold text-dna-green border-2 border-dna-green/30">
                {username[0].toUpperCase()}
              </div>
            )}

            <div className="flex-1 text-center sm:text-left">
              <h1 className="text-3xl font-bold">{name ?? username}</h1>
              <p className="text-muted-foreground">@{username}</p>
              <div className="flex flex-wrap justify-center sm:justify-start gap-2 mt-3">
                {Object.entries(catCounts).map(([cat, count]) => (
                  <span key={cat} className={cn("px-2 py-0.5 rounded text-xs font-medium", CAT_COLORS[cat] ?? "bg-muted text-muted-foreground")}>
                    {count} {cat.toLowerCase()}{count > 1 ? "s" : ""}
                  </span>
                ))}
              </div>
            </div>

            {/* Score ring */}
            <div className="flex flex-col items-center gap-2">
              <svg width="110" height="110" viewBox="0 0 110 110">
                <circle cx="55" cy="55" r="44" fill="none" stroke="hsl(var(--muted))" strokeWidth="8" />
                <circle cx="55" cy="55" r="44" fill="none"
                  stroke={scoreStroke}
                  strokeWidth="8"
                  strokeDasharray={`${dash.toFixed(1)} ${circumference.toFixed(1)}`}
                  strokeDashoffset={(circumference / 4).toFixed(1)}
                  strokeLinecap="round"
                  style={{ filter: "drop-shadow(0 0 6px currentColor)", transition: "stroke-dasharray 1s ease" }}
                />
                <text x="55" y="50" textAnchor="middle" dominantBaseline="middle" fill="currentColor"
                  style={{ fontSize: 24, fontWeight: 700, fontFamily: "Inter, sans-serif" }}>
                  {developerScore}
                </text>
                <text x="55" y="68" textAnchor="middle" dominantBaseline="middle" fill="hsl(var(--muted-foreground))"
                  style={{ fontSize: 10, fontFamily: "Inter, sans-serif" }}>
                  Dev Score
                </text>
              </svg>
              <div className="flex items-center gap-1.5">
                <Zap className={cn("h-3 w-3", scoreColor)} />
                <span className={cn("text-xs font-semibold", scoreColor)}>
                  {developerScore >= 80 ? "Expert" : developerScore >= 60 ? "Advanced" : developerScore >= 40 ? "Intermediate" : "Learning"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container max-w-5xl py-8 space-y-8">
        {/* Visualization */}
        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Developer Genome</CardTitle>
              <div className="flex rounded-lg border border-border/60 overflow-hidden text-xs">
                {(["helix", "radar", "tree"] as View[]).map((v) => (
                  <button
                    key={v}
                    onClick={() => setView(v)}
                    className={cn(
                      "px-3 py-1.5 capitalize transition-colors",
                      view === v ? "bg-dna-green/20 text-dna-green font-medium" : "text-muted-foreground hover:text-foreground"
                    )}
                  >
                    {v === "helix" ? "DNA Helix" : v === "radar" ? "Radar" : "Skill Tree"}
                  </button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[400px]">
              {view === "helix" && <DNAHelix skills={skills as never} />}
              {view === "radar" && <GenomeRadar skills={skills} />}
              {view === "tree" && <SkillTree skills={skills} />}
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top skills */}
          <Card className="bg-card/50 border-border/60">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Award className="h-4 w-4 text-dna-blue" /> Top Skills
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {topSkills.length === 0 ? (
                <p className="text-sm text-muted-foreground">No skills detected yet.</p>
              ) : topSkills.map((s) => (
                <div key={s.name} className="flex items-center gap-3">
                  <span className="text-sm w-32 truncate">{s.name}</span>
                  <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${s.proficiencyScore}%`,
                        background: s.category === "LANGUAGE" ? "#3B82F6"
                          : s.category === "FRAMEWORK" ? "#10B981"
                          : s.category === "PATTERN" ? "#F59E0B"
                          : s.category === "TOOL" ? "#8B5CF6" : "#06B6D4",
                      }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground w-8 text-right tabular-nums">{s.proficiencyScore}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Top projects */}
          <Card className="bg-card/50 border-border/60">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Globe className="h-4 w-4 text-dna-purple" /> Public Projects
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {projects.length === 0 ? (
                <p className="text-sm text-muted-foreground">No analyzed public projects yet.</p>
              ) : projects.slice(0, 5).map((p) => (
                <a
                  key={p.id}
                  href={p.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/30 transition-colors group"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate group-hover:text-dna-green transition-colors">{p.name}</p>
                    {p.primaryLanguage && (
                      <p className="text-xs text-muted-foreground">{p.primaryLanguage}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground shrink-0 ml-4">
                    <span className="flex items-center gap-1"><Star className="h-3 w-3" />{p.stars}</span>
                    <span className="flex items-center gap-1"><GitFork className="h-3 w-3" />{p.forks}</span>
                  </div>
                </a>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Embed banner */}
        <Card className="bg-card/30 border-dashed border-border/40">
          <CardContent className="p-4 text-center text-sm text-muted-foreground">
            This is a public CodeDNA developer profile.{" "}
            <a href="/" className="text-dna-green hover:underline font-medium">Create yours free</a>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
