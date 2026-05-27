"use client";

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { useTheme } from "next-themes";

interface Skill {
  name: string;
  category: string;
  proficiencyScore: number;
}

interface GenomeRadarProps {
  skills: Skill[];
}

const CATEGORIES = ["LANGUAGE", "FRAMEWORK", "PATTERN", "TOOL", "CONCEPT"] as const;
const CAT_LABELS: Record<string, string> = {
  LANGUAGE: "Languages", FRAMEWORK: "Frameworks",
  PATTERN: "Patterns", TOOL: "Tools", CONCEPT: "Concepts",
};
const CAT_COLORS: Record<string, string> = {
  LANGUAGE: "#3B82F6", FRAMEWORK: "#10B981",
  PATTERN: "#F59E0B", TOOL: "#8B5CF6", CONCEPT: "#06B6D4",
};

export function GenomeRadar({ skills }: GenomeRadarProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; cat: string; catSkills: Skill[] } | null>(null);
  const { resolvedTheme } = useTheme();

  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return;

    const isDark = resolvedTheme !== "light";
    const gridStroke = isDark ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.07)";
    const axisStroke = isDark ? "rgba(255,255,255,0.12)" : "rgba(0,0,0,0.10)";

    const rect = containerRef.current.getBoundingClientRect();
    const W = rect.width || 340;
    const H = rect.height || 340;
    const margin = 60;
    const R = Math.min(W, H) / 2 - margin;
    const levels = 5;
    const N = CATEGORIES.length;
    const angleSlice = (Math.PI * 2) / N;

    // Aggregate: avg proficiency per category
    const data = CATEGORIES.map((cat) => {
      const catSkills = skills.filter((s) => s.category === cat);
      const avg = catSkills.length ? catSkills.reduce((a, s) => a + s.proficiencyScore, 0) / catSkills.length : 0;
      return { cat, value: avg, catSkills };
    });

    const rScale = d3.scaleLinear().range([0, R]).domain([0, 100]);

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("width", W).attr("height", H);

    const g = svg.append("g").attr("transform", `translate(${W / 2},${H / 2})`);

    // Grid
    for (let lv = 1; lv <= levels; lv++) {
      const r = (R / levels) * lv;
      g.append("circle").attr("r", r).attr("fill", "none")
        .attr("stroke", gridStroke).attr("stroke-width", 1);
    }

    // Axes
    CATEGORIES.forEach((cat, i) => {
      const angle = angleSlice * i - Math.PI / 2;
      const x2 = rScale(100) * Math.cos(angle);
      const y2 = rScale(100) * Math.sin(angle);
      g.append("line").attr("x1", 0).attr("y1", 0).attr("x2", x2).attr("y2", y2)
        .attr("stroke", axisStroke).attr("stroke-width", 1);

      // Label
      const lx = (rScale(100) + 22) * Math.cos(angle);
      const ly = (rScale(100) + 22) * Math.sin(angle);
      g.append("text").attr("x", lx).attr("y", ly)
        .attr("text-anchor", "middle").attr("dominant-baseline", "middle")
        .attr("fill", CAT_COLORS[cat]).attr("font-size", "12px")
        .attr("font-family", "Inter, sans-serif").attr("font-weight", "600")
        .text(CAT_LABELS[cat])
        .style("cursor", "pointer")
        .on("mouseenter", function (event: MouseEvent) {
          const d = data.find((x) => x.cat === cat)!;
          const svgRect = svgRef.current!.getBoundingClientRect();
          setTooltip({ x: event.clientX - svgRect.left, y: event.clientY - svgRect.top, cat, catSkills: d.catSkills });
        })
        .on("mouseleave", () => setTooltip(null));
    });

    // Radar polygon
    const radarLine = d3.lineRadial<typeof data[0]>()
      .radius((d) => rScale(d.value))
      .angle((_d, i) => i * angleSlice)
      .curve(d3.curveLinearClosed);

    const defs = svg.append("defs");
    const filter = defs.append("filter").attr("id", "radar-glow");
    filter.append("feGaussianBlur").attr("stdDeviation", "3").attr("result", "b");
    const fm = filter.append("feMerge");
    fm.append("feMergeNode").attr("in", "b");
    fm.append("feMergeNode").attr("in", "SourceGraphic");

    g.append("path").datum(data)
      .attr("d", radarLine as never)
      .attr("fill", "rgba(0,255,136,0.12)")
      .attr("stroke", "#00ff88")
      .attr("stroke-width", 2)
      .attr("filter", "url(#radar-glow)");

    // Dots on vertices
    data.forEach((d, i) => {
      const angle = angleSlice * i - Math.PI / 2;
      const r = rScale(d.value);
      g.append("circle")
        .attr("cx", r * Math.cos(angle)).attr("cy", r * Math.sin(angle))
        .attr("r", 4).attr("fill", CAT_COLORS[d.cat]).attr("filter", "url(#radar-glow)");
    });

  }, [skills, resolvedTheme]);

  return (
    <div ref={containerRef} className="relative w-full h-full flex items-center justify-center">
      <svg ref={svgRef} className="w-full h-full" />
      {tooltip && (
        <div className="absolute pointer-events-none z-20 rounded-lg border border-border bg-card/95 px-3 py-2 text-sm shadow-xl backdrop-blur-sm"
          style={{ left: Math.min(tooltip.x + 8, 260), top: tooltip.y - 20 }}>
          <p className="font-semibold text-sm mb-1" style={{ color: CAT_COLORS[tooltip.cat] }}>{CAT_LABELS[tooltip.cat]}</p>
          {tooltip.catSkills.length === 0
            ? <p className="text-xs text-muted-foreground">No skills yet</p>
            : tooltip.catSkills.slice(0, 6).map((s) => (
              <div key={s.name} className="flex items-center justify-between gap-3 text-xs">
                <span className="text-muted-foreground">{s.name}</span>
                <span className="text-foreground font-medium">{s.proficiencyScore}</span>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
