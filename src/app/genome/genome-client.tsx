"use client";

import { useState } from "react";
import { useTheme } from "next-themes";
import { Dna, Network, BarChart3 } from "lucide-react";
import { DNAHelix } from "@/components/genome/dna-helix";
import { GenomeRadar } from "@/components/genome/genome-radar";
import { SkillTree } from "@/components/genome/skill-tree";
import { SkillTable } from "@/components/genome/skill-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface Skill {
  id: string;
  name: string;
  category: string;
  proficiencyScore: number;
  confidence: string;
  firstSeen: string;
  lastSeen: string;
  evidence: unknown;
}

interface GenomeClientProps {
  skills: Skill[];
  score: number;
  username: string;
}

type ViewMode = "helix" | "radar" | "tree";

function ScoreRing({ score }: { score: number }) {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme !== "light";
  const color = score >= 70 ? "#00ff88" : score >= 40 ? (isDark ? "#facc15" : "#ca8a04") : (isDark ? "#f87171" : "#dc2626");
  const r = 54;
  const circ = 2 * Math.PI * r;
  const fill = (score / 100) * circ;

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-36 h-36">
        <svg viewBox="0 0 140 140" className="w-full h-full -rotate-90">
          <circle cx="70" cy="70" r={r} fill="none" stroke="hsl(var(--muted))" strokeWidth="8" />
          <circle cx="70" cy="70" r={r} fill="none" stroke={color} strokeWidth="8"
            strokeDasharray={`${fill} ${circ}`} strokeLinecap="round"
            style={{ transition: "stroke-dasharray 1s ease-out", filter: `drop-shadow(0 0 8px ${color}80)` }} />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold tabular-nums" style={{ color }}>{score}</span>
          <span className="text-xs text-muted-foreground">/ 100</span>
        </div>
      </div>
      <p className="text-sm text-muted-foreground font-medium">
        {score >= 70 ? "Excellent" : score >= 40 ? "Intermediate" : "Getting started"}
      </p>
    </div>
  );
}

function CategoryBar({ label, skills, color }: { label: string; skills: Skill[]; color: string }) {
  if (!skills.length) return null;
  const avg = Math.round(skills.reduce((a, s) => a + s.proficiencyScore, 0) / skills.length);
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium tabular-nums">{avg}</span>
      </div>
      <div className="h-1.5 rounded-full bg-muted overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${avg}%`, background: color }} />
      </div>
    </div>
  );
}

const CAT_META = [
  { key: "LANGUAGE",  label: "Languages",  color: "#3B82F6" },
  { key: "FRAMEWORK", label: "Frameworks", color: "#10B981" },
  { key: "PATTERN",   label: "Patterns",   color: "#F59E0B" },
  { key: "TOOL",      label: "Tools",      color: "#8B5CF6" },
  { key: "CONCEPT",   label: "Concepts",   color: "#06B6D4" },
];

const VIEWS: Array<{ key: ViewMode; label: string; icon: typeof Dna }> = [
  { key: "helix", label: "DNA Helix", icon: Dna },
  { key: "radar", label: "Radar",     icon: BarChart3 },
  { key: "tree",  label: "Skill Tree",icon: Network },
];

export function GenomeClient({ skills, score, username }: GenomeClientProps) {
  const [view, setView] = useState<ViewMode>("helix");

  const byCategory = CAT_META.reduce<Record<string, Skill[]>>((acc, { key }) => {
    acc[key] = skills.filter((s) => s.category === key);
    return acc;
  }, {});

  if (skills.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
        <Dna className="h-16 w-16 text-muted-foreground/30" />
        <p className="text-lg font-medium">No genome yet</p>
        <p className="text-sm text-muted-foreground">Analyze your repos from the Dashboard to build your genome.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Score + breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-[auto_1fr] gap-6">
        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-2"><CardTitle className="text-base text-center">Developer Score</CardTitle></CardHeader>
          <CardContent className="flex justify-center pb-4"><ScoreRing score={score} /></CardContent>
        </Card>

        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Genome Breakdown</CardTitle>
            <p className="text-xs text-muted-foreground">{skills.length} skills across {Object.values(byCategory).filter((v) => v.length > 0).length} categories</p>
          </CardHeader>
          <CardContent className="space-y-3">
            {CAT_META.map(({ key, label, color }) => (
              <CategoryBar key={key} label={`${label} (${byCategory[key]?.length ?? 0})`} skills={byCategory[key] ?? []} color={color} />
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Main viz + sidebar */}
      <div className="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-6">
        {/* Visualization */}
        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between gap-2 flex-wrap">
              <CardTitle className="text-base">{username}&apos;s Genome</CardTitle>
              <div className="flex rounded-lg border border-border/60 overflow-hidden">
                {VIEWS.map(({ key, label, icon: Icon }) => (
                  <button key={key} onClick={() => setView(key)}
                    className={cn("flex items-center gap-1.5 px-3 py-1.5 text-xs transition-colors",
                      view === key ? "bg-dna-green/15 text-dna-green" : "text-muted-foreground hover:text-foreground hover:bg-muted/30")}>
                    <Icon className="h-3.5 w-3.5" />{label}
                  </button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="h-[420px] lg:h-[520px] w-full relative">
              {view === "helix" && <DNAHelix skills={skills} />}
              {view === "radar" && <GenomeRadar skills={skills} />}
              {view === "tree"  && <SkillTree  skills={skills} />}
            </div>
          </CardContent>
        </Card>

        {/* Skill table sidebar */}
        <Card className="bg-card/50 border-border/60 flex flex-col">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">All Skills</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-hidden">
            <SkillTable skills={skills as Parameters<typeof SkillTable>[0]["skills"]} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
