"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Zap, GitBranch, Dna, TrendingUp, CheckCircle, XCircle, Loader2, Languages } from "lucide-react";
import { StatCard } from "@/components/dashboard/stat-card";
import { DonutChart, DonutLegend, type DonutSlice } from "@/components/dashboard/donut-chart";
import { DashboardRadar } from "@/components/dashboard/dashboard-radar";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { RepoTable, type RepoRow } from "@/components/dashboard/repo-table";
import { SyncButton } from "@/components/dashboard/sync-button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface Stats {
  analyzedRepos: number;
  skillCount: number;
  developerScore: number;
  growthVelocity: number;
  languageBreakdown: DonutSlice[];
  topSkills: { axis: string; value: number }[];
}

interface Toast {
  id: string;
  message: string;
  type: "success" | "error";
}

interface Props {
  username: string;
  initialStats: Stats;
  initialRepos: RepoRow[];
  initialActivity: unknown[];
}

function scoreColor(score: number) {
  if (score >= 70) return "text-dna-green";
  if (score >= 40) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-500 dark:text-red-400";
}

export function DashboardClient({ username, initialStats, initialRepos, initialActivity }: Props) {
  const [stats, setStats] = useState<Stats>(initialStats);
  const [repos, setRepos] = useState<RepoRow[]>(initialRepos);
  const [activity, setActivity] = useState<unknown[]>(initialActivity);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [analyzingRepoIds, setAnalyzingRepoIds] = useState<Set<string>>(new Set());
  const [analyzeAllProgress, setAnalyzeAllProgress] = useState<{ done: number; total: number } | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);

  const pollTimers = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());
  const analyzeAllBaseIds = useRef<Set<string>>(new Set());
  const analyzeAllPollTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      pollTimers.current.forEach((t) => clearTimeout(t));
      if (analyzeAllPollTimer.current) clearTimeout(analyzeAllPollTimer.current);
    };
  }, []);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setFetchError(null);
    try {
      const [statsRes, reposRes, activityRes] = await Promise.all([
        fetch("/api/stats").then((r) => r.json()),
        fetch("/api/repos").then((r) => r.json()),
        fetch("/api/activity").then((r) => r.json()),
      ]);
      if (statsRes?.error || reposRes?.error || activityRes?.error) {
        setFetchError(statsRes?.error ?? reposRes?.error ?? activityRes?.error ?? "Failed to refresh data");
      } else {
        setStats(statsRes);
        setRepos(Array.isArray(reposRes) ? reposRes : []);
        setActivity(Array.isArray(activityRes) ? activityRes : []);
      }
    } catch (err) {
      console.error("[dashboard] fetchAll error:", err);
      setFetchError("Failed to refresh dashboard data.");
    } finally {
      setLoading(false);
    }
  }, []);

  function addToast(message: string, type: Toast["type"] = "success") {
    const id = Math.random().toString(36).slice(2);
    setToasts((t) => [...t, { id, message, type }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 4500);
  }

  function removeFromAnalyzing(repoId: string) {
    setAnalyzingRepoIds((s) => { const n = new Set(s); n.delete(repoId); return n; });
    pollTimers.current.delete(repoId);
  }

  function startPolling(repoId: string, repoName: string) {
    const poll = async () => {
      try {
        const res = await fetch(`/api/analyze/status/${repoId}`);
        if (!res.ok) { removeFromAnalyzing(repoId); return; }
        const data = await res.json();
        if (data.status === "complete") {
          removeFromAnalyzing(repoId);
          fetchAll();
          addToast(`Analysis complete for ${repoName}`);
        } else if (data.status === "error") {
          removeFromAnalyzing(repoId);
          addToast(`Analysis failed for ${repoName}`, "error");
        } else {
          pollTimers.current.set(repoId, setTimeout(poll, 2000));
        }
      } catch {
        removeFromAnalyzing(repoId);
      }
    };
    pollTimers.current.set(repoId, setTimeout(poll, 1500));
  }

  const handleAnalyzeRepo = useCallback(async (repoId: string) => {
    const repo = repos.find((r) => r.id === repoId);
    if (!repo) return;
    setAnalyzingRepoIds((s) => new Set(Array.from(s).concat(repoId)));
    try {
      const res = await fetch(`/api/analyze/${repoId}`, { method: "POST" });
      if (!res.ok) {
        const data = await res.json().catch(() => ({})) as { error?: string };
        addToast(data.error ?? "Failed to start analysis", "error");
        removeFromAnalyzing(repoId);
        return;
      }
      startPolling(repoId, repo.name);
    } catch {
      addToast("Failed to start analysis", "error");
      removeFromAnalyzing(repoId);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repos]);

  const handleAnalyzeAll = useCallback(async () => {
    const unanalyzed = repos.filter((r) => !r.isAnalyzed && !analyzingRepoIds.has(r.id));
    if (unanalyzed.length === 0) { addToast("All repos are already analyzed!"); return; }

    try {
      const res = await fetch("/api/analyze/all", { method: "POST" });
      if (!res.ok) { addToast("Failed to start bulk analysis", "error"); return; }
      const { count } = await res.json() as { count: number };
      if (!count) { addToast("Nothing to analyze"); return; }

      analyzeAllBaseIds.current = new Set(unanalyzed.map((r) => r.id));
      setAnalyzeAllProgress({ done: 0, total: count });

      const poll = async () => {
        try {
          const updated: RepoRow[] = await fetch("/api/repos").then((r) => r.json());
          if (!Array.isArray(updated)) return;
          setRepos(updated);
          const done = updated.filter((r) => analyzeAllBaseIds.current.has(r.id) && r.isAnalyzed).length;
          setAnalyzeAllProgress({ done, total: count });
          if (done >= count) {
            setAnalyzeAllProgress(null);
            analyzeAllBaseIds.current = new Set();
            fetchAll();
            addToast(`Analyzed ${count} repo${count === 1 ? "" : "s"}!`);
          } else {
            analyzeAllPollTimer.current = setTimeout(poll, 2500);
          }
        } catch {
          setAnalyzeAllProgress(null);
        }
      };
      analyzeAllPollTimer.current = setTimeout(poll, 2000);
    } catch {
      addToast("Failed to start bulk analysis", "error");
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repos, analyzingRepoIds, fetchAll]);

  const handleSyncSuccess = () => fetchAll();
  const unanalyzedCount = repos.filter((r) => !r.isAnalyzed).length;

  return (
    <div className="container py-8 space-y-6">
      {/* Toast notifications */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={cn(
              "flex items-center gap-2 rounded-lg border px-4 py-2.5 text-sm shadow-lg backdrop-blur-sm pointer-events-auto",
              toast.type === "success"
                ? "bg-card/95 border-dna-green/30 text-foreground"
                : "bg-card/95 border-red-500/30 text-foreground"
            )}
          >
            {toast.type === "success"
              ? <CheckCircle className="h-4 w-4 text-dna-green shrink-0" />
              : <XCircle className="h-4 w-4 text-red-500 dark:text-red-400 shrink-0" />}
            {toast.message}
          </div>
        ))}
      </div>

      {/* Error banner */}
      {fetchError && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-600 dark:text-red-400">
          <XCircle className="h-4 w-4 shrink-0" />
          {fetchError}
          <button onClick={fetchAll} className="ml-auto underline underline-offset-2 hover:no-underline text-xs">Retry</button>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">
            Welcome back, <span className="text-gradient-dna">{username}</span>
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Your developer genome at a glance.</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap justify-end">
          {analyzeAllProgress && (
            <span className="text-xs text-muted-foreground flex items-center gap-1.5">
              <Loader2 className="h-3 w-3 animate-spin" />
              Analyzing repo {analyzeAllProgress.done}/{analyzeAllProgress.total}…
            </span>
          )}
          {!analyzeAllProgress && unanalyzedCount > 0 && !loading && (
            <Button
              size="sm"
              variant="outline"
              className="gap-1.5 border-border/60 hover:border-dna-green/40 hover:text-dna-green text-xs"
              onClick={handleAnalyzeAll}
            >
              <Dna className="h-3.5 w-3.5" />
              Analyze All ({unanalyzedCount})
            </Button>
          )}
          <SyncButton onSuccess={handleSyncSuccess} />
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Repos Analyzed"
          value={stats.analyzedRepos}
          icon={GitBranch}
          colorClass="text-dna-blue"
          description="of synced repos"
          loading={loading}
        />
        <StatCard
          label="Skills Detected"
          value={stats.skillCount}
          icon={Dna}
          colorClass="text-dna-green"
          description="unique skills"
          loading={loading}
        />
        <StatCard
          label="Developer Score"
          value={`${stats.developerScore}`}
          icon={Zap}
          colorClass={scoreColor(stats.developerScore)}
          description={
            stats.developerScore >= 70 ? "Excellent"
            : stats.developerScore >= 40 ? "Intermediate"
            : "Getting started"
          }
          loading={loading}
        />
        <StatCard
          label="Growth Velocity"
          value={stats.growthVelocity}
          icon={TrendingUp}
          colorClass="text-dna-purple"
          description="events last 30 days"
          loading={loading}
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Languages className="h-4 w-4 text-dna-cyan" />
              Language Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center gap-8 py-4">
                <div className="w-[160px] h-[160px] rounded-full bg-muted/30 animate-pulse shrink-0" />
                <div className="space-y-2 flex-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className="h-3 bg-muted/40 rounded animate-pulse" style={{ width: `${70 - i * 10}%` }} />
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-6 py-2 flex-wrap sm:flex-nowrap">
                <DonutChart data={stats.languageBreakdown} size={180} />
                <DonutLegend data={stats.languageBreakdown} />
              </div>
            )}
          </CardContent>
        </Card>

        <DashboardRadar data={stats.topSkills} loading={loading} />
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivityFeed events={activity as never[]} loading={loading} />
        <RepoTable
          repos={repos}
          loading={loading}
          analyzingRepoIds={analyzingRepoIds}
          onAnalyze={handleAnalyzeRepo}
        />
      </div>
    </div>
  );
}
