import { Star, GitFork, ExternalLink, Lock, Cpu } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface AnalysisData {
  architecturePattern?: string;
  architectureConfidence?: number;
  complexityScore?: number;
  qualityIndicators?: { overallQuality?: number };
  projectSummary?: string;
  projectHighlights?: string[];
  skillsDemonstrated?: Array<{ skill: string; category: string }>;
}

interface ProjectCardProps {
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
  analysisData: AnalysisData | null;
  highlight?: boolean;
}

const ARCH_COLORS: Record<string, string> = {
  MVC: "bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/20",
  microservice: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
  serverless: "bg-purple-500/15 text-purple-600 dark:text-purple-400 border-purple-500/20",
  jamstack: "bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 border-cyan-500/20",
  "event-driven": "bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/20",
  layered: "bg-slate-500/15 text-slate-600 dark:text-slate-400 border-slate-500/20",
  monolith: "bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/20",
};

const LANG_COLORS: Record<string, string> = {
  TypeScript: "#3178c6", JavaScript: "#f7df1e", Python: "#3572a5",
  Go: "#00add8", Rust: "#dea584", Java: "#b07219", Ruby: "#701516",
  "C#": "#178600", Dart: "#00b4ab", Swift: "#f05138",
};

function QualityBar({ label, value, color = "#00ff88" }: { label: string; value: number; color?: string }) {
  return (
    <div>
      <div className="flex justify-between text-xs text-muted-foreground mb-0.5">
        <span>{label}</span><span>{value}</span>
      </div>
      <div className="h-1.5 rounded-full bg-muted overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${value}%`, background: color }} />
      </div>
    </div>
  );
}

export function ProjectCard({ id, name, fullName, url, description, primaryLanguage, stars, forks, isPrivate, complexityScore, analysisData, highlight }: ProjectCardProps) {
  const arch = analysisData?.architecturePattern;
  const quality = analysisData?.qualityIndicators?.overallQuality ?? 0;
  const summary = analysisData?.projectSummary ?? description ?? "No description available.";
  const skills = (analysisData?.skillsDemonstrated ?? []).slice(0, 4);

  return (
    <Card className={cn(
      "bg-card/50 border-border/60 hover:border-border transition-colors group flex flex-col",
      highlight && "border-dna-green/30 bg-card/70"
    )}>
      {highlight && (
        <div className="px-4 pt-3 pb-0">
          <span className="text-xs font-semibold text-dna-green flex items-center gap-1">
            <Star className="h-3 w-3" /> Top Work
          </span>
        </div>
      )}
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap">
              {isPrivate && <Lock className="h-3 w-3 text-muted-foreground/60 shrink-0" />}
              <Link href={`/analysis/${id}`} className="font-semibold text-sm hover:text-dna-green transition-colors truncate">
                {name}
              </Link>
              {arch && (
                <Badge variant="outline" className={cn("text-xs h-5 px-1.5 shrink-0", ARCH_COLORS[arch] ?? ARCH_COLORS.layered)}>
                  {arch}
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">{fullName}</p>
          </div>
          <a href={url} target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground transition-colors shrink-0 opacity-0 group-hover:opacity-100">
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>
      </CardHeader>

      <CardContent className="flex flex-col gap-3 flex-1">
        <p className="text-xs text-muted-foreground line-clamp-2">{summary}</p>

        {/* Stats row */}
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          {primaryLanguage && (
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ background: LANG_COLORS[primaryLanguage] ?? "#888" }} />
              {primaryLanguage}
            </span>
          )}
          {stars > 0 && (
            <span className="flex items-center gap-0.5"><Star className="h-3 w-3" />{stars}</span>
          )}
          {forks > 0 && (
            <span className="flex items-center gap-0.5"><GitFork className="h-3 w-3" />{forks}</span>
          )}
        </div>

        {/* Skill chips */}
        {skills.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            {skills.map((s) => (
              <span key={s.skill} className="text-xs px-1.5 py-0.5 rounded-full bg-muted/50 text-muted-foreground border border-border/40">
                {s.skill}
              </span>
            ))}
          </div>
        )}

        {/* Quality bars */}
        {(complexityScore != null || quality > 0) && (
          <div className="space-y-1.5 mt-auto">
            {complexityScore != null && <QualityBar label="Complexity" value={complexityScore} color="#8B5CF6" />}
            {quality > 0 && <QualityBar label="Quality" value={quality} color="#10B981" />}
          </div>
        )}

        <div className="flex items-center justify-between mt-auto pt-1">
          <Link href={`/analysis/${id}`}
            className="text-xs text-dna-green/80 hover:text-dna-green transition-colors flex items-center gap-0.5">
            <Cpu className="h-3 w-3" /> View Analysis
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
