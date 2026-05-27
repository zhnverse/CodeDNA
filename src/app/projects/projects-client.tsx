"use client";

import { useState, useMemo } from "react";
import { FolderGit2 } from "lucide-react";
import { ProjectCard } from "@/components/projects/project-card";
import { cn } from "@/lib/utils";

interface AnalysisData {
  architecturePattern?: string;
  complexityScore?: number;
  qualityIndicators?: { overallQuality?: number };
  projectSummary?: string;
  projectHighlights?: string[];
  skillsDemonstrated?: Array<{ skill: string; category: string }>;
  isTutorialClone?: boolean;
}

interface Repo {
  id: string;
  name: string;
  fullName: string;
  url: string;
  description: string | null;
  primaryLanguage: string | null;
  stars: number;
  forks: number;
  isPrivate: boolean;
  complexityScore: number | null;
  analysisData: unknown;
  lastAnalyzedAt: string | null;
}

type SortKey = "quality" | "complexity" | "stars" | "recent";

const SORT_LABELS: Record<SortKey, string> = {
  quality: "Quality", complexity: "Complexity", stars: "Stars", recent: "Recent",
};

export function ProjectsClient({ repos }: { repos: Repo[] }) {
  const [sort, setSort] = useState<SortKey>("quality");
  const [langFilter, setLangFilter] = useState("ALL");
  const [archFilter, setArchFilter] = useState("ALL");

  const langs = ["ALL", ...Array.from(new Set(repos.map((r) => r.primaryLanguage).filter(Boolean))) as string[]];
  const archs = ["ALL", ...Array.from(new Set(repos.map((r) => (r.analysisData as AnalysisData | null)?.architecturePattern).filter(Boolean))) as string[]];

  const sorted = useMemo(() => {
    return [...repos]
      .filter((r) => langFilter === "ALL" || r.primaryLanguage === langFilter)
      .filter((r) => archFilter === "ALL" || (r.analysisData as AnalysisData | null)?.architecturePattern === archFilter)
      .sort((a, b) => {
        const aData = a.analysisData as AnalysisData | null;
        const bData = b.analysisData as AnalysisData | null;
        if (sort === "quality") return (bData?.qualityIndicators?.overallQuality ?? 0) - (aData?.qualityIndicators?.overallQuality ?? 0);
        if (sort === "complexity") return (b.complexityScore ?? 0) - (a.complexityScore ?? 0);
        if (sort === "stars") return b.stars - a.stars;
        if (sort === "recent") return (b.lastAnalyzedAt ?? "").localeCompare(a.lastAnalyzedAt ?? "");
        return 0;
      });
  }, [repos, sort, langFilter, archFilter]);

  // Best work: top 3 by quality + complexity, exclude tutorials
  const bestWork = useMemo(() => {
    return [...repos]
      .filter((r) => !(r.analysisData as AnalysisData | null)?.isTutorialClone)
      .sort((a, b) => {
        const aData = a.analysisData as AnalysisData | null;
        const bData = b.analysisData as AnalysisData | null;
        const aScore = (aData?.qualityIndicators?.overallQuality ?? 0) + (a.complexityScore ?? 0);
        const bScore = (bData?.qualityIndicators?.overallQuality ?? 0) + (b.complexityScore ?? 0);
        return bScore - aScore;
      })
      .slice(0, 3);
  }, [repos]);

  if (repos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
        <FolderGit2 className="h-16 w-16 text-muted-foreground/30" />
        <p className="text-lg font-medium">No analyzed projects yet</p>
        <p className="text-sm text-muted-foreground">Sync repos from the Dashboard and run analysis to see your projects here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Best work */}
      {bestWork.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-4">Best Work</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {bestWork.map((r) => (
              <ProjectCard key={r.id} {...r} analysisData={r.analysisData as AnalysisData | null} highlight />
            ))}
          </div>
        </section>
      )}

      {/* All repos with sort/filter */}
      <section>
        <div className="flex items-center justify-between gap-4 flex-wrap mb-4">
          <h2 className="text-lg font-semibold">All Projects <span className="text-sm font-normal text-muted-foreground">({sorted.length})</span></h2>

          <div className="flex items-center gap-2 flex-wrap">
            {/* Sort */}
            <div className="flex rounded-lg border border-border/60 overflow-hidden text-xs">
              {(Object.keys(SORT_LABELS) as SortKey[]).map((k) => (
                <button key={k} onClick={() => setSort(k)}
                  className={cn("px-2.5 py-1.5 transition-colors",
                    sort === k ? "bg-dna-green/15 text-dna-green" : "text-muted-foreground hover:text-foreground")}>
                  {SORT_LABELS[k]}
                </button>
              ))}
            </div>
            {/* Lang filter */}
            {langs.length > 2 && (
              <select value={langFilter} onChange={(e) => setLangFilter(e.target.value)}
                className="text-xs rounded-md border border-border/60 bg-card px-2 py-1.5 text-muted-foreground focus:outline-none">
                {langs.map((l) => <option key={l} value={l}>{l === "ALL" ? "All Languages" : l}</option>)}
              </select>
            )}
            {/* Arch filter */}
            {archs.length > 2 && (
              <select value={archFilter} onChange={(e) => setArchFilter(e.target.value)}
                className="text-xs rounded-md border border-border/60 bg-card px-2 py-1.5 text-muted-foreground focus:outline-none">
                {archs.map((a) => <option key={a} value={a}>{a === "ALL" ? "All Patterns" : a}</option>)}
              </select>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {sorted.map((r) => (
            <ProjectCard key={r.id} {...r} analysisData={r.analysisData as AnalysisData | null} />
          ))}
        </div>
      </section>
    </div>
  );
}
