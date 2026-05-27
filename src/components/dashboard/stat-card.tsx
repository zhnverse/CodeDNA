import { cn } from "@/lib/utils";
import { Card, CardContent, CardDescription, CardHeader } from "@/components/ui/card";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  colorClass?: string;
  loading?: boolean;
}

export function StatCard({ label, value, icon: Icon, description, colorClass = "text-dna-green", loading }: StatCardProps) {
  if (loading) {
    return (
      <Card className="bg-card/50 border-border/60">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div className="h-4 w-24 bg-muted/60 rounded animate-pulse" />
            <div className="h-4 w-4 bg-muted/60 rounded animate-pulse" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-9 w-20 bg-muted/60 rounded animate-pulse mb-1" />
          {description && <div className="h-3 w-32 bg-muted/40 rounded animate-pulse" />}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-card/50 border-border/60 hover:border-dna-green/20 transition-colors">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardDescription>{label}</CardDescription>
          <Icon className={cn("h-4 w-4", colorClass)} />
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-bold tabular-nums">{value}</p>
        {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
      </CardContent>
    </Card>
  );
}
