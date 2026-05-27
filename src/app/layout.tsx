import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/layout/providers";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { KeyboardShortcuts } from "@/components/layout/keyboard-shortcuts";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CodeDNA — Your Developer Genome",
  description: "Connect GitHub. See your true developer genome. Analyze your code, track your growth, showcase your skills.",
  keywords: ["developer", "github", "code analysis", "skills", "portfolio"],
  openGraph: {
    title: "CodeDNA",
    description: "Your developer genome, decoded.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} min-h-screen flex flex-col antialiased`}>
        <Providers>
          <KeyboardShortcuts />
          <Navbar />
          <main className="flex-1">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
