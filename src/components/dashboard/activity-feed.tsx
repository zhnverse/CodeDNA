"use client";

import { GitBranch, TrendingUp, Star, Zap, Activity } from "lucide-react";
import { formatRelativeTime } from "@/lib/format";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface GrowthEvent {
  id: string;
  eventType: "NEW_SKILL" | "LEVEL_UP" | "MILESTONE" | "NEW_REPO";
  title: string;
  description: string | null;
  createdAt: string;
  skillNode: { name: string; category: string } | null;
}

const EVENT_CONFIG = {
  NEW_SKILL: { icon: Zap, color: "text-dna-green", bg: "bg-dna-green/10" },
  LEVEL_UP: { icon: TrendingUp, color: "text-dna-blue", bg: "bg-dna-blue/10" },
  MILESTONE: { icon: Star, color: "text-yellow-600 dark:text-yellow-400", bg: "bg-yellow-400/10" },
  NEW_REPO: { icon: GitBranch, color: "text-dna-purple", bg: "bg-dna-purple/10" },
};

interface ActivityFeedProps {
  events: GrowthEvent[];
  loading?: boolean;
}

export function ActivityFeed({ events, loading }: ActivityFeedProps) {
  return (
    <Card className="bg-card/50 border-border/60 h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Activity className="h-4 w-4 text-dna-green" />
          Recent Activity
        </CardTitle>
      </CardHeader>
      <CardContent className="px-4 pb-4">
        {loading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex gap-3 items-start">
                <div className="w-8 h-8 rounded-full bg-muted/60 animate-pulse shrink-0" />
                <div className="flex-1 space-y-1.5">
                  <div className="h-3.5 w-3/4 bg-muted/60 rounded animate-pulse" />
                  <div className="h-3 w-1/2 bg-muted/40 rounded animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        ) : events.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-center gap-2">
            <Activity className="h-8 w-8 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">No activity yet.</p>
            <p className="text-xs text-muted-foreground/60">Analyze repos to generate growth events.</p>
          </div>
        ) : (
          <div className="space-y-1 max-h-72 overflow-y-auto pr-1">
            {events.map((event) => {
              const cfg = EVENT_CONFIG[event.eventType];
              const Icon = cfg.icon;
              return (
                <div key={event.id} className="flex gap-3 items-start py-2 group">
                  <div className={`w-8 h-8 rounded-full ${cfg.bg} flex items-center justify-center shrink-0`}>
                    <Icon className={`h-3.5 w-3.5 ${cfg.color}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium leading-tight truncate">{event.title}</p>
                    {event.description && (
                      <p className="text-xs text-muted-foreground truncate mt-0.5">{event.description}</p>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground/60 shrink-0 mt-0.5">
                    {formatRelativeTime(event.createdAt)}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
