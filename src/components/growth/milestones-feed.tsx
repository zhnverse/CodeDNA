"use client";

import { Zap, TrendingUp, Star, GitBranch, Trophy } from "lucide-react";
import { formatRelativeTime } from "@/lib/format";

interface GrowthEvent {
  id: string;
  eventType: "NEW_SKILL" | "LEVEL_UP" | "MILESTONE" | "NEW_REPO";
  title: string;
  description: string | null;
  createdAt: string;
  skillNode: { name: string; category: string } | null;
}

const EVENT_CONFIG = {
  NEW_SKILL: { icon: Zap,       color: "text-dna-green",  bg: "bg-dna-green/10",  border: "border-dna-green/20" },
  LEVEL_UP:  { icon: TrendingUp, color: "text-dna-blue",  bg: "bg-dna-blue/10",   border: "border-dna-blue/20"  },
  MILESTONE: { icon: Trophy,    color: "text-yellow-600 dark:text-yellow-400", bg: "bg-yellow-400/10", border: "border-yellow-400/20" },
  NEW_REPO:  { icon: GitBranch, color: "text-dna-purple", bg: "bg-dna-purple/10", border: "border-dna-purple/20" },
};

export function MilestonesFeed({ events }: { events: GrowthEvent[] }) {
  if (events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-3 text-center">
        <Star className="h-10 w-10 text-muted-foreground/30" />
        <p className="text-sm text-muted-foreground">No growth events yet.</p>
        <p className="text-xs text-muted-foreground/60">Analyze repos to start tracking your journey.</p>
      </div>
    );
  }

  return (
    <div className="relative pl-6">
      {/* Vertical line */}
      <div className="absolute left-2.5 top-0 bottom-0 w-px bg-border/40" />

      <div className="space-y-4">
        {events.map((ev) => {
          const cfg = EVENT_CONFIG[ev.eventType] ?? EVENT_CONFIG.NEW_SKILL;
          const Icon = cfg.icon;
          return (
            <div key={ev.id} className="relative flex gap-3 items-start">
              {/* Dot on timeline */}
              <div className={`absolute -left-4 w-5 h-5 rounded-full border ${cfg.bg} ${cfg.border} flex items-center justify-center shrink-0`}>
                <Icon className={`h-2.5 w-2.5 ${cfg.color}`} />
              </div>
              <div className="flex-1 min-w-0 pb-1">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium leading-tight">{ev.title}</p>
                  <span className="text-xs text-muted-foreground/60 shrink-0 mt-0.5">
                    {formatRelativeTime(ev.createdAt)}
                  </span>
                </div>
                {ev.description && (
                  <p className="text-xs text-muted-foreground mt-0.5">{ev.description}</p>
                )}
                {ev.skillNode && (
                  <span className="inline-block mt-1 text-xs px-1.5 py-0.5 rounded-full bg-muted/50 text-muted-foreground">
                    {ev.skillNode.category.toLowerCase()} · {ev.skillNode.name}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
