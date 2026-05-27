import { HeroSection } from "@/components/landing/hero-section";
import { FeaturesSection } from "@/components/landing/features-section";
import { HowItWorksSection } from "@/components/landing/how-it-works";
import { GenomePreviewSection } from "@/components/landing/genome-preview";

export default function HomePage() {
  return (
    <div className="relative overflow-hidden">
      {/* Global grid background */}
      <div className="fixed inset-0 grid-bg pointer-events-none" />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <GenomePreviewSection />
    </div>
  );
}
