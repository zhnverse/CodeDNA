"use client";

import { useState, useMemo } from "react";
import { Star, GitFork, Lock, ArrowUpDown, ArrowUp, ArrowDown, Cpu, CheckCircle, Clock, Loader2, ExternalLink } from "lucide-react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/format";
import { cn } from "@/lib/utils";

export interface RepoRow {
  id: string;
  name: string;
  fullName: string;
  url: string;
  primaryLanguage: string | null;
  stars: number;
  forks: number;
  isPrivate: boolean;
  isAnalyzed: boolean;
  lastAnalyzedAt: string | null;
  complexityScore: number | null;
}

type SortKey = "name" | "stars" | "lastAnalyzedAt";
type SortDir = "asc" | "desc";

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  if (!active) return <ArrowUpDown className="h-3 w-3 opacity-40" />;
  return dir === "asc" ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />;
}

interface RepoTableProps {
  repos: RepoRow[];
  loading?: boolean;
  analyzingRepoIds?: Set<string>;
  onAnalyze?: (repoId: string) => void;
}

export function RepoTable({ repos, loading, analyzingRepoIds, onAnalyze }: RepoTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("stars");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 8;

  const sorted = useMemo(() => {
    return [...repos].sort((a, b) => {
      let av: string | number = a[sortKey] ?? "";
      let bv: string | number = b[sortKey] ?? "";
      if (sortKey === "lastAnalyzedAt") {
        av = av ? new Date(av as string).getTime() : 0;
        bv = bv ? new Date(bv as string).getTime() : 0;
      }
      return sortDir === "asc" ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
    });
  }, [repos, sortKey, sortDir]);

  const paged = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const totalPages = Math.ceil(repos.length / PAGE_SIZE);

  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("desc"); }
    setPage(0);
  }

  const ColHeader = ({ label, sk }: { label: string; sk: SortKey }) => (
    <button
      onClick={() => toggleSort(sk)}
      className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
    >
      {label}
      <SortIcon active={sortKey === sk} dir={sortDir} />
    </button>
  );

  return (
    <Card className="bg-card/50 border-border/60 h-full flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Cpu className="h-4 w-4 text-dna-blue" />
          Repositories
          <span className="ml-auto text-xs font-normal text-muted-foreground">{repos.length} total</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="px-4 pb-4 flex-1 flex flex-col">
        {loading ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-10 bg-muted/40 rounded animate-pulse" />
            ))}
          </div>
        ) : repos.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-2 text-center py-8">
            <Cpu className="h-8 w-8 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">No repositories synced yet.</p>
            <p className="text-xs text-muted-foreground/60">Click "Sync Repos" to import from GitHub.</p>
          </div>
        ) : (
          <>
            {/* Header row */}
            <div className="grid grid-cols-[1fr_80px_80px_100px_90px] gap-2 px-2 pb-2 border-b border-border/40">
              <ColHeader label="Repository" sk="name" />
              <ColHeader label="Stars" sk="stars" />
              <div className="text-xs font-medium text-muted-foreground">Language</div>
              <ColHeader label="Last Analyzed" sk="lastAnalyzedAt" />
              <div />
            </div>

            {/* Rows */}
            <div className="flex-1 divide-y divide-border/30">
              {paged.map((repo) => (
                <div
                  key={repo.id}
                  className="grid grid-cols-[1fr_80px_80px_100px_90px] gap-2 px-2 py-2.5 items-center hover:bg-muted/20 transition-colors group"
                >
                  <div className="flex items-center gap-1.5 min-w-0">
                    {repo.isPrivate && <Lock className="h-3 w-3 text-muted-foreground/60 shrink-0" />}
                    <Link
                      href={`/analysis/${repo.id}`}
                      className="text-sm font-medium truncate hover:text-dna-green transition-colors"
                    >
                      {repo.name}
                    </Link>
                    {repo.isAnalyzed && (
                      <CheckCircle className="h-3 w-3 text-dna-green shrink-0" />
                    )}
                    <a
                      href={repo.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="shrink-0 text-muted-foreground/40 hover:text-muted-foreground transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground tabular-nums">
                    <Star className="h-3 w-3" />
                    {repo.stars.toLocaleString()}
                  </div>
                  <div>
                    {repo.primaryLanguage ? (
                      <span className="text-xs text-muted-foreground truncate">{repo.primaryLanguage}</span>
                    ) : (
                      <span className="text-xs text-muted-foreground/40">—</span>
                    )}
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3 shrink-0" />
                    <span className="truncate">{formatDate(repo.lastAnalyzedAt)}</span>
                  </div>
                  <div>
                    {(() => {
                      const isRunning = analyzingRepoIds?.has(repo.id) ?? false;
                      return (
                        <Button
                          size="sm"
                          variant="outline"
                          className={cn(
                            "h-7 text-xs px-2 border-border/60",
                            !repo.isAnalyzed && !isRunning && "hover:border-dna-green/40 hover:text-dna-green",
                            isRunning && "opacity-70"
                          )}
                          disabled={isRunning}
                          onClick={() => onAnalyze?.(repo.id)}
                        >
                          {isRunning ? (
                            <><Loader2 className="h-3 w-3 animate-spin mr-1" />Analyzing</>
                          ) : repo.isAnalyzed ? "Re-analyze" : "Analyze"}
                        </Button>
                      );
                    })()}
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between pt-3 border-t border-border/40">
                <span className="text-xs text-muted-foreground">
                  Page {page + 1} of {totalPages}
                </span>
                <div className="flex gap-1">
                  <Button size="sm" variant="ghost" className="h-7 text-xs" onClick={() => setPage((p) => p - 1)} disabled={page === 0}>
                    Prev
                  </Button>
                  <Button size="sm" variant="ghost" className="h-7 text-xs" onClick={() => setPage((p) => p + 1)} disabled={page >= totalPages - 1}>
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
