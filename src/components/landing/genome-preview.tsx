"use client";

import { RadarChart } from "@/components/genome/radar-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { signIn } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Github } from "lucide-react";

const dummyData = [
  { axis: "TypeScript", value: 87 },
  { axis: "Architecture", value: 74 },
  { axis: "Testing", value: 62 },
  { axis: "APIs", value: 91 },
  { axis: "DevOps", value: 55 },
  { axis: "React", value: 83 },
  { axis: "Databases", value: 70 },
  { axis: "Security", value: 48 },
];

const dummySkills = [
  { name: "TypeScript", score: 87, category: "LANGUAGE" },
  { name: "React", score: 83, category: "FRAMEWORK" },
  { name: "REST APIs", score: 91, category: "PATTERN" },
  { name: "Next.js", score: 79, category: "FRAMEWORK" },
  { name: "PostgreSQL", score: 70, category: "TOOL" },
  { name: "Jest", score: 62, category: "TOOL" },
];

const categoryColors: Record<string, string> = {
  LANGUAGE: "text-dna-green border-dna-green/30 bg-dna-green/10",
  FRAMEWORK: "text-dna-blue border-dna-blue/30 bg-dna-blue/10",
  PATTERN: "text-dna-purple border-dna-purple/30 bg-dna-purple/10",
  TOOL: "text-dna-cyan border-dna-cyan/30 bg-dna-cyan/10",
};

export function GenomePreviewSection() {
  return (
    <section className="relative py-24 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-4xl sm:text-5xl font-bold">
            Your genome, <span className="text-gradient-dna">visualized</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            A sample genome for a full-stack developer. Connect GitHub to generate yours.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          {/* Radar chart */}
          <div className="relative flex items-center justify-center">
            <div className="absolute inset-0 bg-gradient-radial from-dna-green/10 via-transparent to-transparent rounded-full" />
            <div className="w-full max-w-md aspect-square">
              <RadarChart data={dummyData} width={420} height={420} />
            </div>
          </div>

          {/* Skills breakdown */}
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-6">
              <div>
                <p className="text-sm text-muted-foreground">Developer Score</p>
                <p className="text-4xl font-bold text-gradient-dna">2,847</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Skills Decoded</p>
                <p className="text-4xl font-bold">24</p>
              </div>
            </div>

            <div className="space-y-3">
              {dummySkills.map((skill) => (
                <Card key={skill.name} className="bg-card/50 border-border/60">
                  <CardContent className="p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full border font-medium ${categoryColors[skill.category]}`}
                      >
                        {skill.category}
                      </span>
                      <span className="font-medium">{skill.name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-24 h-1.5 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-dna-green to-dna-blue rounded-full"
                          style={{ width: `${skill.score}%` }}
                        />
                      </div>
                      <span className="text-sm font-semibold w-8 text-right">{skill.score}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="pt-4">
              <Button
                variant="glow"
                size="lg"
                className="w-full gap-2"
                onClick={() => signIn("github")}
              >
                <Github className="h-5 w-5" />
                Generate My Genome
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
