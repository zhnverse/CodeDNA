import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect, notFound } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { ExternalLink, GitBranch, Cpu, BarChart3, Star, GitFork, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface AnalysisData {
  architecturePattern?: string;
  architectureConfidence?: number;
  codePatterns?: Array<{ type: string; description: string; quality: number }>;
  qualityIndicators?: { namingConsistency?: number; separationOfConcerns?: number; dryAdherence?: number; overallQuality?: number };
  skillsDemonstrated?: Array<{ skill: string; category: string; proficiency: string; evidence: string }>;
  complexityScore?: number;
  projectSummary?: string;
  projectHighlights?: string[];
}

const ARCH_BADGES: Record<string, string> = {
  MVC: "bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/20",
  microservice: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
  serverless: "bg-purple-500/15 text-purple-600 dark:text-purple-400 border-purple-500/20",
  jamstack: "bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 border-cyan-500/20",
  "event-driven": "bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/20",
  layered: "bg-slate-500/15 text-slate-600 dark:text-slate-400 border-slate-500/20",
};
const CAT_COLORS: Record<string, string> = {
  LANGUAGE: "bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/20",
  FRAMEWORK: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
  PATTERN: "bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/20",
  TOOL: "bg-purple-500/15 text-purple-600 dark:text-purple-400 border-purple-500/20",
  CONCEPT: "bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 border-cyan-500/20",
};
const PROF_COLORS: Record<string, string> = {
  beginner: "bg-muted/50 text-muted-foreground border-border/60",
  intermediate: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
  advanced: "bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20",
  expert: "bg-dna-green/10 text-dna-green border-dna-green/20",
};
const PAT_TYPE_LABELS: Record<string, string> = {
  ARCHITECTURE: "Architecture", ERROR_HANDLING: "Error Handling",
  TESTING: "Testing", API_DESIGN: "API Design",
  STATE_MANAGEMENT: "State Mgmt", NAMING_CONVENTION: "Naming",
};

function QualityBar({ label, value, color = "#00ff88" }: { label: string; value: number; color?: string }) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-semibold tabular-nums">{value}<span className="text-muted-foreground text-xs">/100</span></span>
      </div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${value}%`, background: color }} />
      </div>
    </div>
  );
}

export default async function AnalysisRepoPage({ params }: { params: { repoId: string } }) {
  const session = await getServerSession(authOptions);
  if (!session) redirect("/");

  const repo = await prisma.repository.findFirst({
    where: { id: params.repoId, userId: session.user.userId },
    include: { codePatterns: { orderBy: { qualityScore: "desc" } } },
  });

  if (!repo) notFound();

  const data = repo.analysisData as AnalysisData | null;
  const analysisStatus = (repo.analysisData as Record<string, unknown> | null)?.status;

  if (!repo.isAnalyzed || !data || analysisStatus !== "complete") {
    return (
      <div className="container py-8 max-w-2xl">
        <Link href="/projects" className="text-sm text-muted-foreground hover:text-foreground mb-6 inline-flex items-center gap-1">
          ← Projects
        </Link>
        <Card className="bg-card/50 border-border/60">
          <CardContent className="p-12 flex flex-col items-center gap-4 text-center">
            <AlertCircle className="h-10 w-10 text-muted-foreground/40" />
            <p className="font-semibold">{repo.name} has not been analyzed yet.</p>
            <p className="text-sm text-muted-foreground">Go to the Dashboard and click Analyze on this repo.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const arch = data.architecturePattern ?? "layered";
  const quality = data.qualityIndicators ?? {};
  const skills = data.skillsDemonstrated ?? [];
  const patterns = repo.codePatterns;
  const highlights = data.projectHighlights ?? [];

  return (
    <div className="container py-8 space-y-6 max-w-5xl">
      {/* Breadcrumb */}
      <Link href="/projects" className="text-sm text-muted-foreground hover:text-foreground inline-flex items-center gap-1">
        ← Projects
      </Link>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-3xl font-bold">{repo.name}</h1>
            <Badge variant="outline" className={cn("text-sm px-2", ARCH_BADGES[arch] ?? ARCH_BADGES.layered)}>
              {arch}
            </Badge>
          </div>
          <p className="text-muted-foreground text-sm mt-1">{repo.fullName}</p>
          {data.projectSummary && (
            <p className="text-sm mt-3 max-w-2xl text-foreground/80">{data.projectSummary}</p>
          )}
        </div>
        <a href={repo.url} target="_blank" rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors shrink-0 border border-border/60 rounded-lg px-3 py-1.5 hover:border-border">
          <ExternalLink className="h-4 w-4" /> GitHub
        </a>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Complexity", value: `${data.complexityScore ?? 0}/100`, icon: Cpu, color: "text-purple-600 dark:text-purple-400" },
          { label: "Quality", value: `${quality.overallQuality ?? 0}/100`, icon: BarChart3, color: "text-dna-green" },
          { label: "Stars", value: repo.stars.toString(), icon: Star, color: "text-yellow-600 dark:text-yellow-400" },
          { label: "Forks", value: repo.forks.toString(), icon: GitFork, color: "text-dna-blue" },
        ].map(({ label, value, icon: Icon, color }) => (
          <Card key={label} className="bg-card/50 border-border/60">
            <CardContent className="p-4 flex items-center gap-3">
              <Icon className={cn("h-5 w-5 shrink-0", color)} />
              <div>
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className="text-lg font-bold tabular-nums">{value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Architecture */}
        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <GitBranch className="h-4 w-4 text-dna-blue" /> Architecture
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-3">
              <Badge variant="outline" className={cn("text-base px-3 py-1", ARCH_BADGES[arch] ?? ARCH_BADGES.layered)}>
                {arch}
              </Badge>
              <span className="text-sm text-muted-foreground">
                {data.architectureConfidence ?? 70}% confidence
              </span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
              <div className="h-full rounded-full bg-dna-blue transition-all" style={{ width: `${data.architectureConfidence ?? 70}%` }} />
            </div>
            <p className="text-xs text-muted-foreground">
              Detected from code structure, dependency patterns, and file organization.
            </p>
          </CardContent>
        </Card>

        {/* Quality breakdown */}
        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-dna-green" /> Quality Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <QualityBar label="Naming Consistency" value={quality.namingConsistency ?? 0} color="#3B82F6" />
            <QualityBar label="Separation of Concerns" value={quality.separationOfConcerns ?? 0} color="#10B981" />
            <QualityBar label="DRY Adherence" value={quality.dryAdherence ?? 0} color="#F59E0B" />
            <QualityBar label="Overall Quality" value={quality.overallQuality ?? 0} color="#00ff88" />
          </CardContent>
        </Card>

        {/* Skills demonstrated */}
        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Cpu className="h-4 w-4 text-dna-purple" /> Skills Demonstrated
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {skills.map((s) => (
                <div key={s.skill} className="flex items-center gap-1">
                  <Badge variant="outline" className={cn("text-xs", CAT_COLORS[s.category])}>
                    {s.skill}
                  </Badge>
                  <Badge variant="outline" className={cn("text-xs h-5 px-1", PROF_COLORS[s.proficiency])}>
                    {s.proficiency}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Code patterns */}
        {patterns.length > 0 && (
          <Card className="bg-card/50 border-border/60">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Code Patterns</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {patterns.map((p) => (
                <div key={p.id} className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-dna-green/80">{PAT_TYPE_LABELS[p.patternType] ?? p.patternType}</p>
                    <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{p.description}</p>
                  </div>
                  {p.qualityScore != null && (
                    <span className="text-xs tabular-nums shrink-0 font-semibold">{p.qualityScore}<span className="text-muted-foreground">/100</span></span>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Highlights */}
      {highlights.length > 0 && (
        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-3"><CardTitle className="text-base">Highlights</CardTitle></CardHeader>
          <CardContent>
            <ul className="space-y-1.5">
              {highlights.map((h, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <span className="text-dna-green mt-0.5 shrink-0">•</span>
                  <span className="text-muted-foreground">{h}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
