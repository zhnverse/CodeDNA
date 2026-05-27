"use client";

import { RadarChart } from "@/components/genome/radar-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dna } from "lucide-react";

interface RadarData {
  axis: string;
  value: number;
}

interface DashboardRadarProps {
  data: RadarData[];
  loading?: boolean;
}

export function DashboardRadar({ data, loading }: DashboardRadarProps) {
  return (
    <Card className="bg-card/50 border-border/60 h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-base flex items-center gap-2">
          <Dna className="h-4 w-4 text-dna-green" />
          Top Skills
        </CardTitle>
      </CardHeader>
      <CardContent className="flex items-center justify-center pb-4">
        {loading ? (
          <div className="w-48 h-48 rounded-full bg-muted/30 animate-pulse" />
        ) : data.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-8 text-center">
            <div className="w-16 h-16 rounded-full border-2 border-dashed border-border/60 flex items-center justify-center">
              <Dna className="h-6 w-6 text-muted-foreground/40" />
            </div>
            <p className="text-sm text-muted-foreground">No skills decoded yet.</p>
            <p className="text-xs text-muted-foreground/60">Analyze repos to populate your genome.</p>
          </div>
        ) : (
          <div className="w-full max-w-xs aspect-square">
            <RadarChart data={data} width={280} height={280} />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
