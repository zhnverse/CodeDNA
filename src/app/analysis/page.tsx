import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Cpu, GitBranch } from "lucide-react";

export default async function AnalysisPage() {
  const session = await getServerSession(authOptions);
  if (!session) redirect("/");

  return (
    <div className="container py-10 max-w-2xl space-y-8">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold">Analysis</h1>
        <p className="text-muted-foreground">Import and analyze your GitHub repositories.</p>
      </div>

      <Card className="bg-card/50 border-border/60">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="h-5 w-5 text-dna-green" />
            Import Repositories
          </CardTitle>
          <CardDescription>
            Connect your GitHub account to pull in repositories for analysis.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 rounded-lg border border-border/60 bg-muted/30 text-sm text-muted-foreground">
            Analysis engine coming in Phase 2. Stay tuned.
          </div>
          <Button variant="glow" className="gap-2" disabled>
            <Cpu className="h-4 w-4" />
            Start Analysis
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
