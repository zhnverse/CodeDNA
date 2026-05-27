"use client";

import { useEffect, useRef, useState, useMemo, useCallback } from "react";
import { useTheme } from "next-themes";

interface Skill {
  name: string;
  category: string;
  proficiencyScore: number;
  confidence: string;
  evidence: unknown;
}

interface DNAHelixProps {
  skills: Skill[];
  className?: string;
}

const CAT_COLORS: Record<string, string> = {
  LANGUAGE:  "#3B82F6",
  FRAMEWORK: "#10B981",
  PATTERN:   "#F59E0B",
  TOOL:      "#8B5CF6",
  CONCEPT:   "#06B6D4",
};

const RADIUS = 70;
const N_TURNS = 3;
const PTS_PER_TURN = 24;
const N = N_TURNS * PTS_PER_TURN;

function project(
  x3: number, y3: number, z3: number,
  w: number, h: number
): { sx: number; sy: number; depth: number; scale: number; alpha: number } {
  const d = (z3 / RADIUS + 1) / 2; // 0–1
  return {
    sx: w / 2 + x3,
    sy: h / 2 + y3 + z3 * 0.12,
    depth: z3,
    scale: 0.7 + 0.3 * d,
    alpha: 0.5 + 0.5 * d,
  };
}

type SelectedSkill = Skill | null;

export function DNAHelix({ skills, className }: DNAHelixProps) {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme !== "light";
  const strandColor = isDark ? "white" : "#94a3b8";
  const containerRef = useRef<HTMLDivElement>(null);
  const [dim, setDim] = useState({ w: 600, h: 500 });
  const [rot, setRot] = useState(0);
  const rotRef = useRef(0);
  const afRef = useRef<number>();
  const tRef = useRef(0);
  const hoveringRef = useRef(false);
  const [hovered, setHovered] = useState<{ skill: Skill; sx: number; sy: number } | null>(null);
  const [selected, setSelected] = useState<SelectedSkill>(null);

  useEffect(() => {
    const ro = new ResizeObserver((es) => {
      const e = es[0];
      if (e) setDim({ w: e.contentRect.width, h: e.contentRect.height });
    });
    if (containerRef.current) ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const tick = (now: number) => {
      if (!hoveringRef.current) {
        const dt = tRef.current ? now - tRef.current : 0;
        rotRef.current = (rotRef.current + dt * 0.00025) % (Math.PI * 2);
        setRot(rotRef.current);
      }
      tRef.current = now;
      afRef.current = requestAnimationFrame(tick);
    };
    afRef.current = requestAnimationFrame(tick);
    return () => { if (afRef.current) cancelAnimationFrame(afRef.current); };
  }, []);

  const scene = useMemo(() => {
    const { w, h } = dim;
    const ht = Math.min(h * 0.78, 380);

    // Strand paths
    const pathA: string[] = [], pathB: string[] = [];
    const rungs: { x1: number; y1: number; x2: number; y2: number; alpha: number }[] = [];

    for (let i = 0; i <= N; i++) {
      const t = i / N;
      const theta = t * N_TURNS * Math.PI * 2;
      const y3 = (t - 0.5) * ht;

      const xA = RADIUS * Math.cos(theta + rot), zA = RADIUS * Math.sin(theta + rot);
      const xB = RADIUS * Math.cos(theta + rot + Math.PI), zB = RADIUS * Math.sin(theta + rot + Math.PI);

      const pA = project(xA, y3, zA, w, h);
      const pB = project(xB, y3, zB, w, h);

      pathA.push(`${i === 0 ? "M" : "L"}${pA.sx.toFixed(1)},${pA.sy.toFixed(1)}`);
      pathB.push(`${i === 0 ? "M" : "L"}${pB.sx.toFixed(1)},${pB.sy.toFixed(1)}`);

      if (i % 6 === 0) {
        const d = ((zA + zB) / 2 / RADIUS + 1) / 2;
        rungs.push({ x1: pA.sx, y1: pA.sy, x2: pB.sx, y2: pB.sy, alpha: 0.15 + 0.3 * d });
      }
    }

    // Gene nodes
    const genes: Array<{
      skill: Skill; sx: number; sy: number; depth: number;
      r: number; color: string;
    }> = [];

    const used = skills.slice(0, Math.min(skills.length, 18));
    const step = N / (used.length || 1);

    used.forEach((sk, idx) => {
      const t = (idx * step + step / 2) / N;
      const theta = t * N_TURNS * Math.PI * 2;
      const y3 = (t - 0.5) * ht;
      const x3 = RADIUS * Math.cos(theta + rot);
      const z3 = RADIUS * Math.sin(theta + rot);
      const p = project(x3, y3, z3, w, h);
      genes.push({
        skill: sk,
        sx: p.sx, sy: p.sy,
        depth: p.depth,
        r: (4 + (sk.proficiencyScore / 100) * 8) * p.scale,
        color: CAT_COLORS[sk.category] ?? "#06B6D4",
      });
    });

    // Particles (fixed, derived from seed)
    const particles = Array.from({ length: 35 }, (_, i) => ({
      id: i,
      x: (((Math.sin(i * 2.39) + 1) / 2) * w).toFixed(1),
      y: (((Math.cos(i * 1.73) + 1) / 2) * h).toFixed(1),
      r: (0.5 + (i % 3) * 0.5).toFixed(1),
      o: (0.08 + (i % 5) * 0.02).toFixed(2),
    }));

    return { pathA: pathA.join(" "), pathB: pathB.join(" "), rungs, genes, particles };
  }, [rot, dim, skills]);

  const sortedRenderables = useMemo(
    () => [...scene.genes].sort((a, b) => a.depth - b.depth),
    [scene.genes]
  );

  const handleMouseEnter = useCallback((g: typeof scene.genes[0]) => {
    hoveringRef.current = true;
    setHovered({ skill: g.skill, sx: g.sx, sy: g.sy });
  }, []);
  const handleMouseLeave = useCallback(() => {
    hoveringRef.current = false;
    setHovered(null);
  }, []);

  return (
    <div ref={containerRef} className={`relative w-full h-full ${className ?? ""}`}>
      <svg
        viewBox={`0 0 ${dim.w} ${dim.h}`}
        width={dim.w}
        height={dim.h}
        className="w-full h-full"
        onMouseLeave={() => { hoveringRef.current = false; setHovered(null); }}
      >
        <defs>
          <filter id="hx-glow">
            <feGaussianBlur stdDeviation="2.5" result="b" />
            <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
          <filter id="hx-node-glow">
            <feGaussianBlur stdDeviation="4" result="b" />
            <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        {/* Particles */}
        {scene.particles.map((p) => (
          <circle key={p.id} cx={p.x} cy={p.y} r={p.r} fill={strandColor} opacity={p.o} />
        ))}

        {/* Strands */}
        <path d={scene.pathA} fill="none" stroke="#3B82F6" strokeWidth="2" strokeOpacity="0.65" filter="url(#hx-glow)" />
        <path d={scene.pathB} fill="none" stroke="#10B981" strokeWidth="2" strokeOpacity="0.65" filter="url(#hx-glow)" />

        {/* Rungs */}
        {scene.rungs.map((r, i) => (
          <line key={i} x1={r.x1} y1={r.y1} x2={r.x2} y2={r.y2}
            stroke={strandColor} strokeOpacity={r.alpha} strokeWidth="1" />
        ))}

        {/* Gene nodes (depth-sorted) */}
        {sortedRenderables.map((g) => (
          <g key={g.skill.name}
            onMouseEnter={() => handleMouseEnter(g)}
            onMouseLeave={handleMouseLeave}
            onClick={() => setSelected(s => s?.name === g.skill.name ? null : g.skill)}
            style={{ cursor: "pointer" }}
          >
            <circle cx={g.sx} cy={g.sy} r={g.r * 2.2} fill={g.color} opacity={0.08} />
            <circle cx={g.sx} cy={g.sy} r={g.r}
              fill={g.color} fillOpacity={0.85}
              stroke={g.color} strokeWidth={selected?.name === g.skill.name ? 2.5 : 0.5}
              strokeOpacity={0.9}
              filter="url(#hx-node-glow)"
            />
          </g>
        ))}
      </svg>

      {/* Hover tooltip */}
      {hovered && (
        <div className="absolute pointer-events-none z-30 rounded-lg border border-border/70 bg-card/95 px-3 py-2 text-sm shadow-xl backdrop-blur-sm"
          style={{ left: Math.min(hovered.sx + 14, dim.w - 190), top: Math.max(hovered.sy - 50, 8) }}>
          <p className="font-semibold">{hovered.skill.name}</p>
          <p className="text-xs text-muted-foreground capitalize mt-0.5">
            {hovered.skill.category.toLowerCase()} · {hovered.skill.confidence.toLowerCase()}
          </p>
          <div className="mt-1.5 h-1.5 w-full rounded-full bg-muted overflow-hidden">
            <div className="h-full rounded-full transition-all"
              style={{ width: `${hovered.skill.proficiencyScore}%`, background: CAT_COLORS[hovered.skill.category] ?? "#06B6D4" }} />
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">{hovered.skill.proficiencyScore}/100</p>
        </div>
      )}

      {/* Selected skill panel */}
      {selected && (
        <div className="absolute right-3 top-3 w-52 rounded-xl border border-border bg-card/95 p-3 shadow-xl backdrop-blur-sm z-30">
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: CAT_COLORS[selected.category] }} />
              <span className="font-semibold text-sm">{selected.name}</span>
            </div>
            <button onClick={() => setSelected(null)} className="text-muted-foreground hover:text-foreground text-xs ml-1 shrink-0">✕</button>
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between text-muted-foreground">
              <span>Category</span>
              <span className="capitalize text-foreground">{selected.category.toLowerCase()}</span>
            </div>
            <div className="flex justify-between text-muted-foreground">
              <span>Confidence</span>
              <span className="capitalize text-foreground">{selected.confidence.toLowerCase()}</span>
            </div>
            <div className="mt-2">
              <div className="flex justify-between text-muted-foreground mb-1">
                <span>Proficiency</span><span className="text-foreground">{selected.proficiencyScore}/100</span>
              </div>
              <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${selected.proficiencyScore}%`, background: CAT_COLORS[selected.category] }} />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-3 left-3 flex flex-col gap-1">
        {Object.entries(CAT_COLORS).map(([cat, color]) => (
          <div key={cat} className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <div className="w-2 h-2 rounded-full" style={{ background: color }} />
            <span className="capitalize">{cat.toLowerCase()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
