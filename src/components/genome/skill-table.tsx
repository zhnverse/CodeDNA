"use client";

import { useState, useMemo } from "react";
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Skill {
  id: string;
  name: string;
  category: string;
  proficiencyScore: number;
  confidence: string;
  firstSeen: string;
  lastSeen: string;
}

const CAT_COLORS: Record<string, string> = {
  LANGUAGE: "bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/20",
  FRAMEWORK: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
  PATTERN: "bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/20",
  TOOL: "bg-purple-500/15 text-purple-600 dark:text-purple-400 border-purple-500/20",
  CONCEPT: "bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 border-cyan-500/20",
};
const CONF_COLORS: Record<string, string> = {
  CLAIMED: "bg-muted/50 text-muted-foreground border-border/60",
  DEMONSTRATED: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
  MASTERED: "bg-dna-green/10 text-dna-green border-dna-green/20",
};
const CAT_BAR_COLORS: Record<string, string> = {
  LANGUAGE: "#3B82F6", FRAMEWORK: "#10B981",
  PATTERN: "#F59E0B", TOOL: "#8B5CF6", CONCEPT: "#06B6D4",
};

type SortKey = "name" | "proficiencyScore" | "category" | "confidence";
type SortDir = "asc" | "desc";

export function SkillTable({ skills }: { skills: Skill[] }) {
  const [sortKey, setSortKey] = useState<SortKey>("proficiencyScore");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [catFilter, setCatFilter] = useState<string>("ALL");
  const [confFilter, setConfFilter] = useState<string>("ALL");
  const [search, setSearch] = useState("");

  const categories = ["ALL", ...Array.from(new Set(skills.map((s) => s.category)))];
  const confidences = ["ALL", "CLAIMED", "DEMONSTRATED", "MASTERED"];

  const sorted = useMemo(() => {
    return [...skills]
      .filter((s) => catFilter === "ALL" || s.category === catFilter)
      .filter((s) => confFilter === "ALL" || s.confidence === confFilter)
      .filter((s) => !search || s.name.toLowerCase().includes(search.toLowerCase()))
      .sort((a, b) => {
        let av: string | number = a[sortKey];
        let bv: string | number = b[sortKey];
        if (typeof av === "string") av = av.toLowerCase();
        if (typeof bv === "string") bv = bv.toLowerCase();
        return sortDir === "asc" ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
      });
  }, [skills, sortKey, sortDir, catFilter, confFilter, search]);

  function toggleSort(k: SortKey) {
    if (k === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(k); setSortDir("desc"); }
  }

  function SortIcon({ k }: { k: SortKey }) {
    if (k !== sortKey) return <ArrowUpDown className="h-3 w-3 opacity-30" />;
    return sortDir === "asc" ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />;
  }

  return (
    <div className="flex flex-col gap-3 h-full">
      {/* Filters */}
      <input
        type="text" placeholder="Search skills…" value={search} onChange={(e) => setSearch(e.target.value)}
        className="w-full rounded-md border border-border/60 bg-muted/30 px-3 py-1.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-dna-green/40"
      />
      <div className="flex gap-1.5 flex-wrap">
        {categories.map((c) => (
          <button key={c} onClick={() => setCatFilter(c)}
            className={cn("px-2 py-0.5 text-xs rounded-full border transition-colors",
              catFilter === c ? "border-dna-green/50 bg-dna-green/10 text-dna-green" : "border-border/60 text-muted-foreground hover:text-foreground")}>
            {c === "ALL" ? "All" : c.charAt(0) + c.slice(1).toLowerCase()}
          </button>
        ))}
        {confidences.filter((c) => c !== "ALL").map((c) => (
          <button key={c} onClick={() => setConfFilter(confFilter === c ? "ALL" : c)}
            className={cn("px-2 py-0.5 text-xs rounded-full border transition-colors",
              confFilter === c ? "border-dna-green/50 bg-dna-green/10 text-dna-green" : "border-border/60 text-muted-foreground hover:text-foreground")}>
            {c.charAt(0) + c.slice(1).toLowerCase()}
          </button>
        ))}
      </div>

      {/* Header */}
      <div className="grid grid-cols-[1fr_80px_90px_90px] gap-2 px-2 border-b border-border/40 pb-1.5">
        {(["name", "category", "confidence", "proficiencyScore"] as const).map((k) => (
          <button key={k} onClick={() => toggleSort(k)}
            className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors text-left">
            {k === "name" ? "Skill" : k === "proficiencyScore" ? "Score" : k.charAt(0).toUpperCase() + k.slice(1)}
            <SortIcon k={k} />
          </button>
        ))}
      </div>

      {/* Rows */}
      <div className="flex-1 overflow-y-auto space-y-0.5 pr-1">
        {sorted.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">No skills match</p>
        ) : sorted.map((s) => (
          <div key={s.id} className="grid grid-cols-[1fr_80px_90px_90px] gap-2 px-2 py-1.5 rounded hover:bg-muted/20 transition-colors items-center">
            <span className="text-sm font-medium truncate">{s.name}</span>
            <Badge variant="outline" className={cn("text-xs h-5 shrink-0 px-1.5", CAT_COLORS[s.category])}>
              {s.category.charAt(0) + s.category.slice(1).toLowerCase()}
            </Badge>
            <Badge variant="outline" className={cn("text-xs h-5 shrink-0 px-1.5", CONF_COLORS[s.confidence])}>
              {s.confidence.charAt(0) + s.confidence.slice(1).toLowerCase()}
            </Badge>
            <div className="flex items-center gap-1.5">
              <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
                <div className="h-full rounded-full transition-all" style={{ width: `${s.proficiencyScore}%`, background: CAT_BAR_COLORS[s.category] }} />
              </div>
              <span className="text-xs tabular-nums text-muted-foreground w-7 text-right">{s.proficiencyScore}</span>
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-muted-foreground text-right">{sorted.length} of {skills.length} skills</p>
    </div>
  );
}
