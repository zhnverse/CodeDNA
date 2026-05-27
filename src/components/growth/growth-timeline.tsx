"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { useTheme } from "next-themes";

interface GrowthEvent {
  id: string;
  eventType: string;
  createdAt: string;
  skillNode?: { name: string; category: string } | null;
}

interface GrowthTimelineProps {
  events: GrowthEvent[];
}

const CAT_COLORS: Record<string, string> = {
  LANGUAGE: "#3B82F6", FRAMEWORK: "#10B981",
  PATTERN: "#F59E0B", TOOL: "#8B5CF6", CONCEPT: "#06B6D4",
};
const CATEGORIES = ["LANGUAGE", "FRAMEWORK", "PATTERN", "TOOL", "CONCEPT"];

export function GrowthTimeline({ events }: GrowthTimelineProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { resolvedTheme } = useTheme();

  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return;

    const isDark = resolvedTheme !== "light";
    const tickStroke = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.08)";
    const domainStroke = isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)";
    const hoverStroke = isDark ? "rgba(255,255,255,0.4)" : "rgba(0,0,0,0.3)";

    const rect = containerRef.current.getBoundingClientRect();
    const W = rect.width || 600;
    const H = 240;
    const margin = { top: 20, right: 20, bottom: 40, left: 40 };
    const iW = W - margin.left - margin.right;
    const iH = H - margin.top - margin.bottom;

    // Group events by week
    const skillEvents = events.filter((e) => e.eventType === "NEW_SKILL" && e.skillNode);
    if (skillEvents.length === 0) return;

    const dates = skillEvents.map((e) => new Date(e.createdAt));
    const minDate = d3.min(dates)!;
    const maxDate = new Date(Math.max(Date.now(), d3.max(dates)!.getTime() + 86400000 * 7));

    // Generate weekly buckets
    const weeks = d3.timeWeeks(d3.timeWeek.floor(minDate), maxDate);
    if (weeks.length < 2) {
      // Add a week before
      weeks.unshift(d3.timeWeek.offset(weeks[0] ?? new Date(), -1));
    }

    type WeekRow = Record<string, number> & { date: Date };
    const buckets: WeekRow[] = weeks.map((w) => {
      const row: WeekRow = { date: w } as WeekRow;
      CATEGORIES.forEach((c) => { row[c] = 0; });
      return row;
    });

    skillEvents.forEach((ev) => {
      const evDate = new Date(ev.createdAt);
      const bucket = buckets.find((b, i) => {
        const next = buckets[i + 1];
        return evDate >= b.date && (!next || evDate < next.date);
      });
      if (bucket && ev.skillNode) {
        bucket[ev.skillNode.category] = (bucket[ev.skillNode.category] ?? 0) + 1;
      }
    });

    // Cumulative sum
    const cumulative = buckets.map((row, i) => {
      const prev = i > 0 ? buckets[i - 1] : null;
      const out: WeekRow = { date: row.date } as WeekRow;
      CATEGORIES.forEach((c) => {
        out[c] = (row[c] ?? 0) + ((prev as WeekRow | null)?.[c] ?? 0);
      });
      return out;
    });

    const stack = d3.stack<WeekRow>().keys(CATEGORIES).order(d3.stackOrderNone).offset(d3.stackOffsetNone);
    const stacked = stack(cumulative);

    const x = d3.scaleTime().domain([weeks[0], maxDate]).range([0, iW]);
    const maxVal = d3.max(stacked, (s) => d3.max(s, (d) => d[1])) ?? 10;
    const y = d3.scaleLinear().domain([0, maxVal]).range([iH, 0]);

    const area = d3.area<d3.SeriesPoint<WeekRow>>()
      .x((d) => x(d.data.date))
      .y0((d) => y(d[0]))
      .y1((d) => y(d[1]))
      .curve(d3.curveCatmullRom);

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("width", W).attr("height", H);

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    // Areas
    g.selectAll(".area").data(stacked).join("path")
      .attr("class", "area")
      .attr("d", area)
      .attr("fill", (d) => CAT_COLORS[d.key] ?? "#888")
      .attr("fill-opacity", 0.6)
      .attr("stroke", (d) => CAT_COLORS[d.key] ?? "#888")
      .attr("stroke-width", 1)
      .attr("stroke-opacity", 0.8);

    // X axis
    g.append("g").attr("transform", `translate(0,${iH})`)
      .call(d3.axisBottom(x).ticks(Math.min(weeks.length, 6)).tickFormat(d3.timeFormat("%b %d") as never))
      .call((ax) => { ax.select(".domain").attr("stroke", domainStroke); ax.selectAll("text").attr("fill", "#6b7280").attr("font-size", "10px"); ax.selectAll("line").attr("stroke", tickStroke); });

    // Y axis
    g.append("g")
      .call(d3.axisLeft(y).ticks(4).tickFormat((d) => String(d)))
      .call((ax) => { ax.select(".domain").remove(); ax.selectAll("text").attr("fill", "#6b7280").attr("font-size", "10px"); ax.selectAll("line").attr("stroke", tickStroke); });

    // Hover line
    const hoverLine = g.append("line").attr("y1", 0).attr("y2", iH)
      .attr("stroke", hoverStroke).attr("stroke-width", 1).attr("opacity", 0);

    svg.on("mousemove", function (event: MouseEvent) {
      const [mx] = d3.pointer(event, g.node());
      if (mx < 0 || mx > iW) { hoverLine.attr("opacity", 0); return; }
      hoverLine.attr("x1", mx).attr("x2", mx).attr("opacity", 1);
    }).on("mouseleave", () => hoverLine.attr("opacity", 0));

  }, [events, resolvedTheme]);

  return (
    <div ref={containerRef} className="w-full">
      <svg ref={svgRef} className="w-full" />
      <div className="flex gap-3 mt-2 flex-wrap">
        {CATEGORIES.map((c) => (
          <div key={c} className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <div className="w-2.5 h-2.5 rounded-sm" style={{ background: CAT_COLORS[c] }} />
            <span className="capitalize">{c.charAt(0) + c.slice(1).toLowerCase()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
