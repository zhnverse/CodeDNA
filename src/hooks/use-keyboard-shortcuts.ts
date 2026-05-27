"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

export function useKeyboardShortcuts() {
  const router = useRouter();
  const pending = useRef<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      // Ignore when typing in inputs
      const tag = (e.target as HTMLElement).tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
      if ((e.target as HTMLElement).isContentEditable) return;

      const key = e.key.toLowerCase();

      if (pending.current === "g") {
        if (timer.current) clearTimeout(timer.current);
        pending.current = null;

        const routes: Record<string, string> = {
          d: "/dashboard",
          g: "/genome",
          p: "/projects",
          r: "/growth",
          s: "/settings",
        };
        if (routes[key]) router.push(routes[key]);
        return;
      }

      if (key === "g") {
        pending.current = "g";
        timer.current = setTimeout(() => { pending.current = null; }, 1500);
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      if (timer.current) clearTimeout(timer.current);
    };
  }, [router]);
}
