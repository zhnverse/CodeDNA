"use client";

import { useState } from "react";
import { RefreshCw, Check, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SyncButtonProps {
  onSuccess?: (result: { total: number; created: number; updated: number }) => void;
}

type Status = "idle" | "syncing" | "done" | "error";

export function SyncButton({ onSuccess }: SyncButtonProps) {
  const [status, setStatus] = useState<Status>("idle");
  const [summary, setSummary] = useState<string>("");

  async function handleSync() {
    setStatus("syncing");
    setSummary("");
    try {
      const res = await fetch("/api/repos/sync", { method: "POST" });
      if (!res.ok) throw new Error("Sync failed");
      const data = await res.json();
      setSummary(`${data.total} repos · ${data.created} new`);
      setStatus("done");
      onSuccess?.(data);
      setTimeout(() => setStatus("idle"), 3000);
    } catch {
      setStatus("error");
      setSummary("Sync failed");
      setTimeout(() => setStatus("idle"), 3000);
    }
  }

  const icons = {
    idle: <RefreshCw className="h-4 w-4" />,
    syncing: <RefreshCw className="h-4 w-4 animate-spin" />,
    done: <Check className="h-4 w-4" />,
    error: <AlertCircle className="h-4 w-4" />,
  };

  const labels = {
    idle: "Sync Repos",
    syncing: "Syncing…",
    done: summary || "Synced",
    error: summary || "Error",
  };

  return (
    <Button
      variant={status === "done" ? "outline" : status === "error" ? "destructive" : "glow"}
      size="sm"
      onClick={handleSync}
      disabled={status === "syncing"}
      className={cn("gap-2 min-w-[120px]", status === "done" && "border-dna-green/40 text-dna-green")}
    >
      {icons[status]}
      {labels[status]}
    </Button>
  );
}
