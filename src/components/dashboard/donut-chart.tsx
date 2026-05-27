"use client";

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { useTheme } from "next-themes";

export interface DonutSlice {
  language: string;
  count: number;
}

const LANG_COLORS: Record<string, string> = {
  TypeScript: "#3178c6",
  JavaScript: "#f7df1e",
  Python: "#3572a5",
  Go: "#00add8",
  Rust: "#dea584",
  Java: "#b07219",
  "C++": "#f34b7d",
  C: "#555555",
  Ruby: "#701516",
  PHP: "#4f5d95",
  Swift: "#f05138",
  Kotlin: "#a97bff",
  Dart: "#00b4ab",
  "C#": "#178600",
  Shell: "#89e051",
  HTML: "#e34c26",
  CSS: "#563d7c",
  Vue: "#41b883",
  Svelte: "#ff3e00",
  Scala: "#c22d40",
};

function langColor(name: string): string {
  return LANG_COLORS[name] ?? `hsl(${(name.charCodeAt(0) * 47) % 360}, 60%, 55%)`;
}

interface TooltipState {
  x: number;
  y: number;
  language: string;
  count: number;
  pct: string;
}

interface DonutChartProps {
  data: DonutSlice[];
  size?: number;
}

export function DonutChart({ data, size = 260 }: DonutChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);
  const { resolvedTheme } = useTheme();

  const total = data.reduce((s, d) => s + d.count, 0);
  const radius = size / 2 - 10;
  const inner = radius * 0.58;

  useEffect(() => {
    if (!svgRef.current || !data.length) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const g = svg
      .attr("width", size)
      .attr("height", size)
      .append("g")
      .attr("transform", `translate(${size / 2},${size / 2})`);

    const pie = d3.pie<DonutSlice>().value((d) => d.count).sort(null).padAngle(0.025);
    const arc = d3.arc<d3.PieArcDatum<DonutSlice>>().innerRadius(inner).outerRadius(radius).cornerRadius(4);
    const arcHover = d3.arc<d3.PieArcDatum<DonutSlice>>().innerRadius(inner).outerRadius(radius + 7).cornerRadius(4);

    // Glow filter
    const defs = svg.append("defs");
    const filt = defs.append("filter").attr("id", "donut-glow");
    filt.append("feGaussianBlur").attr("stdDeviation", "3").attr("result", "blur");
    const merge = filt.append("feMerge");
    merge.append("feMergeNode").attr("in", "blur");
    merge.append("feMergeNode").attr("in", "SourceGraphic");

    g.selectAll("path")
      .data(pie(data))
      .join("path")
      .attr("d", arc as never)
      .attr("fill", (d) => langColor(d.data.language))
      .attr("opacity", 0.85)
      .style("cursor", "pointer")
      .style("transition", "opacity 0.15s")
      .on("mouseenter", function (event: MouseEvent, d) {
        d3.select(this).transition().duration(120).attr("d", arcHover as never).attr("opacity", 1).attr("filter", "url(#donut-glow)");
        const rect = (event.target as SVGElement).closest("svg")!.getBoundingClientRect();
        setTooltip({
          x: event.clientX - rect.left + 12,
          y: event.clientY - rect.top - 28,
          language: d.data.language,
          count: d.data.count,
          pct: ((d.data.count / total) * 100).toFixed(1),
        });
      })
      .on("mousemove", function (event: MouseEvent) {
        const rect = (event.target as SVGElement).closest("svg")!.getBoundingClientRect();
        setTooltip((t) => t ? { ...t, x: event.clientX - rect.left + 12, y: event.clientY - rect.top - 28 } : t);
      })
      .on("mouseleave", function () {
        d3.select(this).transition().duration(120).attr("d", arc as never).attr("opacity", 0.85).attr("filter", null);
        setTooltip(null);
      });

    const textColor = resolvedTheme === "light" ? "rgba(0,0,0,0.85)" : "rgba(255,255,255,0.9)";
    // Center label
    g.append("text").attr("text-anchor", "middle").attr("y", -8)
      .attr("fill", textColor).attr("font-size", "22px").attr("font-weight", "700").text(total);
    g.append("text").attr("text-anchor", "middle").attr("y", 12)
      .attr("fill", "#6b7280").attr("font-size", "11px").text("repos");
  }, [data, size, total, inner, radius, resolvedTheme]);

  if (!data.length) {
    return (
      <div className="flex flex-col items-center justify-center gap-2 text-muted-foreground" style={{ width: size, height: size }}>
        <div className="w-16 h-16 rounded-full border-2 border-dashed border-border/60" />
        <p className="text-xs">No language data yet</p>
      </div>
    );
  }

  return (
    <div className="relative inline-block">
      <svg ref={svgRef} />
      {tooltip && (
        <div
          className="absolute z-50 pointer-events-none rounded-md border border-border bg-card/95 px-3 py-1.5 text-sm shadow-lg"
          style={{ left: tooltip.x, top: tooltip.y }}
        >
          <span className="font-semibold">{tooltip.language}</span>
          <span className="ml-2 text-muted-foreground">{tooltip.count} repos · {tooltip.pct}%</span>
        </div>
      )}
    </div>
  );
}

export function DonutLegend({ data }: { data: DonutSlice[] }) {
  const total = data.reduce((s, d) => s + d.count, 0);
  return (
    <div className="flex flex-col gap-2 min-w-0">
      {data.slice(0, 8).map((d) => (
        <div key={d.language} className="flex items-center gap-2 text-sm">
          <div className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ background: langColor(d.language) }} />
          <span className="truncate text-muted-foreground">{d.language}</span>
          <span className="ml-auto text-xs tabular-nums text-foreground/70">{((d.count / total) * 100).toFixed(0)}%</span>
        </div>
      ))}
    </div>
  );
}
