"use client";

import { useTheme } from "next-themes";
import { Sun, Moon, Monitor } from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

const OPTIONS = [
  { value: "light", icon: Sun,     label: "Light" },
  { value: "dark",  icon: Moon,    label: "Dark"  },
  { value: "system",icon: Monitor, label: "System"},
] as const;

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  if (!mounted) return <div className="h-9 w-24 rounded-full bg-muted animate-pulse" />;

  return (
    <div className="flex items-center rounded-full border border-border/60 bg-background p-0.5 gap-0.5">
      {OPTIONS.map(({ value, icon: Icon, label }) => (
        <button
          key={value}
          onClick={() => setTheme(value)}
          title={label}
          className={cn(
            "flex items-center justify-center h-7 w-7 rounded-full transition-all",
            theme === value
              ? "bg-primary/15 text-primary shadow-sm"
              : "text-muted-foreground hover:text-foreground hover:bg-muted/60"
          )}
        >
          <Icon className="h-3.5 w-3.5" />
        </button>
      ))}
    </div>
  );
}
