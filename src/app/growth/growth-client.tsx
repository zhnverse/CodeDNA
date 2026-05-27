"use client";

import { useMemo } from "react";
import { TrendingUp, Zap, Star, Trophy, Globe, Layers, Award } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GrowthTimeline } from "@/components/growth/growth-timeline";
import { MilestonesFeed } from "@/components/growth/milestones-feed";
import { cn } from "@/lib/utils";

interface GrowthEvent {
  id: string;
  eventType: "NEW_SKILL" | "LEVEL_UP" | "MILESTONE" | "NEW_REPO";
  title: string;
  description: string | null;
  createdAt: string;
  skillNode: { name: string; category: string } | null;
}

interface Skill {
  id: string;
  name: string;
  category: string;
  proficiencyScore: number;
  confidence: string;
  firstSeen: string;
}

const SKILL_ADJACENCIES: Record<string, string[]> = {
  "TypeScript":  ["Next.js", "Zod", "tRPC", "Vitest", "Deno", "Bun"],
  "JavaScript":  ["TypeScript", "React", "Express.js"],
  "React":       ["Next.js", "React Query", "Redux", "Zustand"],
  "Next.js":     ["Prisma ORM", "tRPC", "Vercel"],
  "Python":      ["FastAPI", "Django", "Pandas", "Pytest"],
  "Node.js":     ["Express.js", "NestJS", "GraphQL"],
  "Go":          ["gRPC", "Gin", "PostgreSQL"],
  "Docker":      ["Kubernetes", "GitHub Actions", "Terraform"],
  "PostgreSQL":  ["Redis", "Prisma ORM", "SQLAlchemy"],
  "REST API":    ["GraphQL", "OpenAPI", "Authentication"],
  "Authentication": ["JWT", "OAuth", "Auth.js"],
  "Git":         ["GitHub Actions", "GitFlow", "CI/CD"],
  "Testing":     ["TDD", "Playwright", "Jest"],
  "Rust":        ["WebAssembly", "Tokio"],
  "Java":        ["Spring Boot", "Gradle", "Hibernate"],
};

type Achievement = {
  id: string; name: string; desc: string; icon: typeof Trophy;
  check: (skills: Skill[], events: GrowthEvent[], velocity: number, score?: number) => boolean;
};

const ACHIEVEMENTS: Achievement[] = [
  { id: "polyglot",    name: "Polyglot",       desc: "5+ programming languages", icon: Globe,
    check: (s) => s.filter(x => x.category === "LANGUAGE").length >= 5 },
  { id: "fullstack",   name: "Full Stack",      desc: "Frontend + Backend + Database skills", icon: Layers,
    check: (s) => {
      const names = s.map(x => x.name.toLowerCase());
      const fe = names.some(n => /react|vue|angular|svelte|next|html|css/.test(n));
      const be = names.some(n => /node|express|django|flask|fastapi|rails|spring/.test(n));
      const db = names.some(n => /postgres|mysql|mongo|redis|prisma|sql/.test(n));
      return fe && be && db;
    } },
  { id: "quality",     name: "Quality First",   desc: "Developer score above 80", icon: Star,
    check: (_s, _e, _v, score?: number) => (score ?? 0) >= 80 },
  { id: "prolific",    name: "Prolific",         desc: "20+ repos analyzed", icon: Award,
    check: (s, e) => {
      const newRepo = e.filter(x => x.eventType === "NEW_REPO").length;
      return newRepo >= 20;
    } },
  { id: "speedlearn",  name: "Speed Learner",   desc: "5+ new skills in 30 days", icon: Zap,
    check: (_s, _e, v) => v >= 5 },
];

export function GrowthClient({ events, skills, score, growthVelocity }: {
  events: GrowthEvent[];
  skills: Skill[];
  score: number;
  growthVelocity: number;
}) {
  const skillNames = useMemo(() => new Set(skills.map((s) => s.name)), [skills]);

  const predictions = useMemo(() => {
    const preds = new Map<string, number>();
    skills.forEach((s) => {
      (SKILL_ADJACENCIES[s.name] ?? []).forEach((adj) => {
        if (!skillNames.has(adj)) preds.set(adj, (preds.get(adj) ?? 0) + s.proficiencyScore);
      });
    });
    return Array.from(preds.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6)
      .map(([name, score]) => ({ name, score }));
  }, [skills, skillNames]);

  const achievements = useMemo(() =>
    ACHIEVEMENTS.map((a) => ({
      ...a,
      unlocked: a.check(skills, events, growthVelocity, score),
    }))
  , [skills, events, growthVelocity, score]);

  const hasData = events.length > 0;

  return (
    <div className="space-y-6">
      {/* Hero stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Developer Score", value: score, icon: Zap, color: score >= 70 ? "text-dna-green" : score >= 40 ? "text-yellow-600 dark:text-yellow-400" : "text-red-500 dark:text-red-400" },
          { label: "Skills Detected", value: skills.length, icon: Star, color: "text-dna-blue" },
          { label: "Growth Velocity", value: growthVelocity, icon: TrendingUp, color: "text-dna-purple", suffix: "/ 30d" },
          { label: "Growth Events", value: events.length, icon: Award, color: "text-amber-600 dark:text-amber-400" },
        ].map(({ label, value, icon: Icon, color, suffix }) => (
          <Card key={label} className="bg-card/50 border-border/60">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-muted-foreground">{label}</p>
                <Icon className={cn("h-4 w-4", color)} />
              </div>
              <p className={cn("text-3xl font-bold tabular-nums", color)}>
                {value}{suffix && <span className="text-sm text-muted-foreground ml-1">{suffix}</span>}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Timeline */}
      <Card className="bg-card/50 border-border/60">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-dna-green" /> Skill Growth Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          {hasData
            ? <GrowthTimeline events={events} />
            : <div className="h-40 flex items-center justify-center text-sm text-muted-foreground">Analyze repos to populate timeline</div>
          }
        </CardContent>
      </Card>

      {/* Milestones + Predictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Milestones</CardTitle>
          </CardHeader>
          <CardContent className="max-h-96 overflow-y-auto">
            <MilestonesFeed events={events as Parameters<typeof MilestonesFeed>[0]["events"]} />
          </CardContent>
        </Card>

        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Zap className="h-4 w-4 text-dna-purple" /> Predicted Next Skills
            </CardTitle>
          </CardHeader>
          <CardContent>
            {predictions.length === 0 ? (
              <p className="text-sm text-muted-foreground py-4 text-center">Analyze more repos to get predictions</p>
            ) : (
              <div className="space-y-2">
                {predictions.map(({ name, score: adj }) => (
                  <div key={name} className="flex items-center justify-between gap-3">
                    <span className="text-sm">{name}</span>
                    <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden max-w-24">
                      <div className="h-full rounded-full bg-dna-purple/70" style={{ width: `${Math.min((adj / 200) * 100, 100)}%` }} />
                    </div>
                    <span className="text-xs text-muted-foreground shrink-0">likely</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Achievements */}
      <Card className="bg-card/50 border-border/60">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Trophy className="h-4 w-4 text-yellow-600 dark:text-yellow-400" /> Achievements
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {achievements.map((a) => {
              const Icon = a.icon;
              return (
                <div key={a.id}
                  className={cn("flex flex-col items-center gap-2 p-3 rounded-xl border text-center transition-colors",
                    a.unlocked
                      ? "border-dna-green/30 bg-dna-green/5 text-foreground"
                      : "border-border/40 bg-muted/20 text-muted-foreground/50 grayscale"
                  )}>
                  <div className={cn("w-10 h-10 rounded-full flex items-center justify-center",
                    a.unlocked ? "bg-dna-green/15" : "bg-muted/30")}>
                    <Icon className={cn("h-5 w-5", a.unlocked ? "text-dna-green" : "text-muted-foreground/40")} />
                  </div>
                  <p className="text-xs font-semibold leading-tight">{a.name}</p>
                  <p className="text-xs leading-tight opacity-70">{a.desc}</p>
                  {a.unlocked && <span className="text-xs text-dna-green font-medium">Earned ✓</span>}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
