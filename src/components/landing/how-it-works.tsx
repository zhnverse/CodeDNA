import { Github, Cpu, Share2 } from "lucide-react";

const steps = [
  {
    number: "01",
    icon: Github,
    title: "Connect GitHub",
    description:
      "One click OAuth. We request read access to your repositories — public and optionally private.",
    color: "from-dna-green/20 to-dna-green/5",
    iconColor: "text-dna-green",
    border: "border-dna-green/20",
  },
  {
    number: "02",
    icon: Cpu,
    title: "Analyze",
    description:
      "Our engine scans your commit history, file structures, language distribution, and code patterns across all repos.",
    color: "from-dna-blue/20 to-dna-blue/5",
    iconColor: "text-dna-blue",
    border: "border-dna-blue/20",
  },
  {
    number: "03",
    icon: Share2,
    title: "Showcase",
    description:
      "Get your living genome profile. Share it with recruiters, teams, or just track your own evolution over time.",
    color: "from-dna-purple/20 to-dna-purple/5",
    iconColor: "text-dna-purple",
    border: "border-dna-purple/20",
  },
];

export function HowItWorksSection() {
  return (
    <section className="relative py-24 px-4">
      {/* Section gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-dna-green/[0.02] to-transparent pointer-events-none" />

      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-4xl sm:text-5xl font-bold">How it works</h2>
          <p className="text-muted-foreground text-lg">Three steps from repo to genome.</p>
        </div>

        <div className="relative">
          {/* Connector line */}
          <div className="hidden md:block absolute top-1/2 left-0 right-0 h-px bg-gradient-to-r from-dna-green/20 via-dna-blue/20 to-dna-purple/20 -translate-y-1/2" />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
            {steps.map((step, idx) => (
              <div key={step.number} className="relative flex flex-col items-center text-center">
                {/* Step number + icon */}
                <div
                  className={`relative z-10 w-20 h-20 rounded-2xl bg-gradient-to-br ${step.color} border ${step.border} flex items-center justify-center mb-6 group`}
                >
                  <step.icon className={`h-8 w-8 ${step.iconColor}`} />
                  <span className={`absolute -top-3 -right-3 text-xs font-bold ${step.iconColor} bg-background px-1.5 py-0.5 rounded border ${step.border}`}>
                    {step.number}
                  </span>
                </div>

                <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
