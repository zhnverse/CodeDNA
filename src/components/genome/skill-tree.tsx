"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";

interface Skill {
  name: string;
  category: string;
  proficiencyScore: number;
}

const CAT_COLORS: Record<string, string> = {
  LANGUAGE: "#3B82F6", FRAMEWORK: "#10B981",
  PATTERN: "#F59E0B", TOOL: "#8B5CF6", CONCEPT: "#06B6D4",
};
const CAT_LABELS: Record<string, string> = {
  LANGUAGE: "Languages", FRAMEWORK: "Frameworks",
  PATTERN: "Patterns", TOOL: "Tools", CONCEPT: "Concepts",
};

interface NodeDatum extends d3.SimulationNodeDatum {
  id: string;
  type: "root" | "category" | "skill";
  label: string;
  color: string;
  r: number;
  category?: string;
}
interface LinkDatum extends d3.SimulationLinkDatum<NodeDatum> {
  strength: number;
}

export function SkillTree({ skills }: { skills: Skill[] }) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const W = rect.width || 560;
    const H = rect.height || 480;
    const cx = W / 2, cy = H / 2;

    const nodes: NodeDatum[] = [
      { id: "root", type: "root", label: "You", color: "#00ff88", r: 22 },
    ];
    const links: LinkDatum[] = [];

    const categories = Array.from(new Set(skills.map((s) => s.category)));
    categories.forEach((cat) => {
      nodes.push({ id: `cat-${cat}`, type: "category", label: CAT_LABELS[cat] ?? cat, color: CAT_COLORS[cat] ?? "#888", r: 16, category: cat });
      links.push({ source: "root", target: `cat-${cat}`, strength: 0.4 });

      skills.filter((s) => s.category === cat).slice(0, 12).forEach((s) => {
        const nid = `skill-${s.name}`;
        nodes.push({ id: nid, type: "skill", label: s.name, color: CAT_COLORS[cat] ?? "#888", r: 4 + (s.proficiencyScore / 100) * 9, category: cat });
        links.push({ source: `cat-${cat}`, target: nid, strength: 0.6 });
      });
    });

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("width", W).attr("height", H);

    const defs = svg.append("defs");
    const f = defs.append("filter").attr("id", "tree-glow");
    f.append("feGaussianBlur").attr("stdDeviation", "3").attr("result", "b");
    const fm = f.append("feMerge");
    fm.append("feMergeNode").attr("in", "b");
    fm.append("feMergeNode").attr("in", "SourceGraphic");

    const container = svg.append("g");

    const linkEl = container.append("g").selectAll("line")
      .data(links).join("line")
      .attr("stroke", (d) => {
        const tgtId = (d.target as NodeDatum).id;
        const tgt = nodes.find((n) => n.id === tgtId);
        return tgt?.color ?? "#666";
      })
      .attr("stroke-opacity", 0.25)
      .attr("stroke-width", 1.5)
      .attr("class", "link-line");

    const nodeEl = container.append("g").selectAll("g")
      .data(nodes).join("g")
      .attr("class", "node-g");

    nodeEl.append("circle")
      .attr("r", (d) => d.r)
      .attr("fill", (d) => d.color)
      .attr("fill-opacity", (d) => d.type === "skill" ? 0.75 : 0.9)
      .attr("filter", (d) => d.type !== "skill" ? "url(#tree-glow)" : null);

    nodeEl.filter((d) => d.type !== "skill").append("text")
      .text((d) => d.label)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("fill", (d) => d.type === "root" ? "#000" : "#fff")
      .attr("font-size", (d) => d.type === "root" ? "10px" : "9px")
      .attr("font-weight", "700")
      .attr("font-family", "Inter, sans-serif");

    nodeEl.filter((d) => d.type === "skill").append("title").text((d) => d.label);

    const sim = d3.forceSimulation(nodes)
      .force("link", d3.forceLink<NodeDatum, LinkDatum>(links).id((d) => d.id).distance(90).strength((d) => d.strength))
      .force("charge", d3.forceManyBody().strength(-220))
      .force("center", d3.forceCenter(cx, cy))
      .force("collide", d3.forceCollide<NodeDatum>((d) => d.r + 6));

    sim.on("tick", () => {
      linkEl
        .attr("x1", (d) => (d.source as NodeDatum).x ?? 0)
        .attr("y1", (d) => (d.source as NodeDatum).y ?? 0)
        .attr("x2", (d) => (d.target as NodeDatum).x ?? 0)
        .attr("y2", (d) => (d.target as NodeDatum).y ?? 0);
      nodeEl.attr("transform", (d) => `translate(${d.x ?? cx},${d.y ?? cy})`);
    });

    return () => { sim.stop(); };
  }, [skills]);

  return (
    <div ref={containerRef} className="relative w-full h-full">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
}
