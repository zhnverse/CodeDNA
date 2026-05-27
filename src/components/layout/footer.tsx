import Link from "next/link";
import { Dna } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border/40 py-8 mt-auto">
      <div className="container flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <Dna className="h-4 w-4 text-dna-green" />
          <span>Code<span className="text-dna-green">DNA</span></span>
          <span className="text-border">·</span>
          <span>Your developer genome, decoded.</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/privacy" className="hover:text-foreground transition-colors">Privacy</Link>
          <Link href="/terms" className="hover:text-foreground transition-colors">Terms</Link>
        </div>
      </div>
    </footer>
  );
}
