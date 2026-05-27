"use client";

import { signIn, useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Github, ArrowRight, Sparkles, Dna } from "lucide-react";
import { Button } from "@/components/ui/button";

export function HeroSection() {
  const { data: session } = useSession();
  const router = useRouter();

  const handleCTA = () => {
    if (session) {
      router.push("/dashboard");
    } else {
      signIn("github");
    }
  };

  return (
    <section className="relative min-h-[90vh] flex items-center justify-center px-4 py-24">
      {/* Radial gradient background */}
      <div className="absolute inset-0 bg-gradient-radial from-dna-green/5 via-transparent to-transparent pointer-events-none" />

      {/* Floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-dna-green/5 rounded-full blur-3xl animate-float pointer-events-none" />
      <div
        className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-dna-blue/5 rounded-full blur-3xl animate-float pointer-events-none"
        style={{ animationDelay: "1.5s" }}
      />

      <div className="relative z-10 text-center max-w-4xl mx-auto space-y-8">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-dna-green/30 bg-dna-green/5 text-dna-green text-sm font-medium">
          <Sparkles className="h-4 w-4" />
          AI-Powered Developer Genome Analysis
        </div>

        {/* Headline */}
        <div className="space-y-2">
          <h1 className="text-6xl sm:text-7xl md:text-8xl font-bold tracking-tight leading-none">
            Your Code Has
          </h1>
          <h1 className="text-6xl sm:text-7xl md:text-8xl font-bold tracking-tight leading-none text-gradient-dna">
            DNA
          </h1>
        </div>

        {/* Subtext */}
        <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          Connect your GitHub. Watch as we decode your commit history, language preferences, and
          architectural patterns into a living genome — your unique developer fingerprint.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button variant="glow" size="xl" onClick={handleCTA} className="w-full sm:w-auto gap-3">
            <Github className="h-5 w-5" />
            {session ? "Go to Dashboard" : "Connect GitHub"}
            <ArrowRight className="h-5 w-5" />
          </Button>
          <Button
            variant="outline"
            size="xl"
            className="w-full sm:w-auto border-border/60 hover:border-dna-green/40 gap-3"
            onClick={() => router.push("/genome/zhnverse")}
          >
            <Dna className="h-5 w-5" />
            See a Sample Genome
          </Button>
        </div>

        {/* Social proof */}
        <p className="text-sm text-muted-foreground">
          Free forever · No card required · Analyzes public & private repos
        </p>

        {/* DNA helix visual */}
        <div className="relative mt-16 flex justify-center">
          <div className="flex items-end gap-1 h-24">
            {Array.from({ length: 24 }).map((_, i) => (
              <div
                key={i}
                className="w-2 rounded-full bg-gradient-to-t from-dna-green/40 to-dna-blue/40"
                style={{
                  height: `${30 + Math.sin(i * 0.5) * 40}%`,
                  animationDelay: `${i * 0.05}s`,
                  opacity: 0.4 + Math.sin(i * 0.5) * 0.3,
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
