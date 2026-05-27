"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { useTheme } from "next-themes";

interface RadarData {
  axis: string;
  value: number;
}

interface RadarChartProps {
  data: RadarData[];
  width?: number;
  height?: number;
}

export function RadarChart({ data, width = 400, height = 400 }: RadarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const { resolvedTheme } = useTheme();

  useEffect(() => {
    if (!svgRef.current || !data.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = 60;
    const radius = Math.min(width, height) / 2 - margin;
    const levels = 5;
    const total = data.length;
    const angleSlice = (Math.PI * 2) / total;

    const g = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2},${height / 2})`);

    const rScale = d3.scaleLinear().range([0, radius]).domain([0, 100]);

    // Grid circles
    for (let level = 1; level <= levels; level++) {
      const r = (radius / levels) * level;
      g.append("circle")
        .attr("r", r)
        .attr("fill", "none")
        .attr("stroke", "rgba(0,255,136,0.1)")
        .attr("stroke-width", 1);
    }

    // Axes
    const axis = g.selectAll(".axis").data(data).enter().append("g").attr("class", "axis");

    axis
      .append("line")
      .attr("x1", 0)
      .attr("y1", 0)
      .attr("x2", (d, i) => rScale(100) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr("y2", (d, i) => rScale(100) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr("stroke", "rgba(0,255,136,0.2)")
      .attr("stroke-width", 1);

    // Labels
    axis
      .append("text")
      .attr("x", (d, i) => (rScale(100) + 18) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr("y", (d, i) => (rScale(100) + 18) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("fill", resolvedTheme === "light" ? "rgba(0,0,0,0.65)" : "rgba(255,255,255,0.7)")
      .attr("font-size", "11px")
      .attr("font-family", "Inter, sans-serif")
      .text((d) => d.axis);

    // Radar area
    const radarLine = d3
      .lineRadial<RadarData>()
      .radius((d) => rScale(d.value))
      .angle((d, i) => i * angleSlice)
      .curve(d3.curveLinearClosed);

    // Glow filter
    const defs = svg.append("defs");
    const filter = defs.append("filter").attr("id", "glow");
    filter.append("feGaussianBlur").attr("stdDeviation", "3").attr("result", "coloredBlur");
    const feMerge = filter.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "coloredBlur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Fill
    g.append("path")
      .datum(data)
      .attr("d", radarLine as any)
      .attr("fill", "rgba(0,255,136,0.15)")
      .attr("stroke", "#00ff88")
      .attr("stroke-width", 2)
      .attr("filter", "url(#glow)");

    // Dots
    g.selectAll(".dot")
      .data(data)
      .enter()
      .append("circle")
      .attr("cx", (d, i) => rScale(d.value) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr("cy", (d, i) => rScale(d.value) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr("r", 4)
      .attr("fill", "#00ff88")
      .attr("filter", "url(#glow)");
  }, [data, width, height, resolvedTheme]);

  return <svg ref={svgRef} className="w-full h-full" />;
}
