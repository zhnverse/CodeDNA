import { Microscope, Dna, TrendingUp, Shield, Zap, GitBranch } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

const features = [
  {
    icon: Microscope,
    title: "Deep Analysis",
    description:
      "We scan every commit, file, and pattern across your repositories to build a comprehensive picture of how you truly code.",
    color: "text-dna-green",
    glow: "group-hover:shadow-[0_0_30px_rgba(0,255,136,0.15)]",
    border: "group-hover:border-dna-green/30",
  },
  {
    icon: Dna,
    title: "Living Genome",
    description:
      "Your genome updates as you push code. Watch your skills evolve in real-time across languages, frameworks, and patterns.",
    color: "text-dna-blue",
    glow: "group-hover:shadow-[0_0_30px_rgba(0,136,255,0.15)]",
    border: "group-hover:border-dna-blue/30",
  },
  {
    icon: TrendingUp,
    title: "Growth Tracking",
    description:
      "See exactly when you leveled up a skill, adopted a new pattern, or crossed the threshold from beginner to expert.",
    color: "text-dna-purple",
    glow: "group-hover:shadow-[0_0_30px_rgba(136,0,255,0.15)]",
    border: "group-hover:border-dna-purple/30",
  },
  {
    icon: Shield,
    title: "Verified Skills",
    description:
      "Claimed skills mean nothing. We measure what you actually demonstrate in code, with evidence from real projects.",
    color: "text-dna-cyan",
    glow: "group-hover:shadow-[0_0_30px_rgba(0,255,255,0.15)]",
    border: "group-hover:border-dna-cyan/30",
  },
  {
    icon: Zap,
    title: "Instant Insights",
    description:
      "Analysis completes in minutes, not hours. Get your genome snapshot and start sharing your profile immediately.",
    color: "text-yellow-600 dark:text-yellow-400",
    glow: "group-hover:shadow-[0_0_30px_rgba(250,204,21,0.15)]",
    border: "group-hover:border-yellow-400/30",
  },
  {
    icon: GitBranch,
    title: "Code Patterns",
    description:
      "Understand your architectural preferences, error handling styles, and naming conventions — the fingerprints only you leave.",
    color: "text-orange-600 dark:text-orange-400",
    glow: "group-hover:shadow-[0_0_30px_rgba(251,146,60,0.15)]",
    border: "group-hover:border-orange-400/30",
  },
];

export function FeaturesSection() {
  return (
    <section className="relative py-24 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-4xl sm:text-5xl font-bold">
            Everything about how{" "}
            <span className="text-gradient-dna">you write code</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Not just what languages you know — but how you think, architect, and evolve.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => (
            <Card
              key={feature.title}
              className={`group bg-card/50 border-border/60 transition-all duration-300 ${feature.border} ${feature.glow} hover:-translate-y-1`}
            >
              <CardHeader className="pb-3">
                <div className={`w-10 h-10 rounded-lg bg-background flex items-center justify-center mb-3 ${feature.color}`}>
                  <feature.icon className="h-5 w-5" />
                </div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-muted-foreground leading-relaxed">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
