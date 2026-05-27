export interface MockAnalysisResult {
  architecturePattern: string;
  architectureConfidence: number;
  codePatterns: Array<{ type: string; description: string; quality: number }>;
  qualityIndicators: {
    namingConsistency: number;
    separationOfConcerns: number;
    dryAdherence: number;
    overallQuality: number;
  };
  skillsDemonstrated: Array<{
    skill: string;
    category: "LANGUAGE" | "FRAMEWORK" | "PATTERN" | "TOOL" | "CONCEPT";
    proficiency: "beginner" | "intermediate" | "advanced" | "expert";
    evidence: string;
  }>;
  complexityScore: number;
  projectSummary: string;
  projectHighlights: string[];
  isTutorialClone: boolean;
  tutorialConfidence: number;
}

function seeded(seed: string, salt: string, min: number, max: number): number {
  let h = 0x811c9dc5;
  const s = seed + salt;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = (h * 0x01000193) >>> 0;
  }
  return min + (h % (max - min + 1));
}

type SkillDef = { skill: string; category: "LANGUAGE" | "FRAMEWORK" | "PATTERN" | "TOOL" | "CONCEPT" };

const LANG_SKILLS: Record<string, SkillDef[]> = {
  TypeScript:  [{ skill:"TypeScript", category:"LANGUAGE" }, { skill:"JavaScript", category:"LANGUAGE" }, { skill:"Type Safety", category:"CONCEPT" }, { skill:"Node.js", category:"FRAMEWORK" }],
  JavaScript:  [{ skill:"JavaScript", category:"LANGUAGE" }, { skill:"Node.js", category:"FRAMEWORK" }, { skill:"Async Programming", category:"PATTERN" }],
  Python:      [{ skill:"Python", category:"LANGUAGE" }, { skill:"Data Structures", category:"CONCEPT" }, { skill:"OOP Design", category:"PATTERN" }],
  Go:          [{ skill:"Go", category:"LANGUAGE" }, { skill:"Concurrency", category:"CONCEPT" }, { skill:"REST API", category:"PATTERN" }],
  Rust:        [{ skill:"Rust", category:"LANGUAGE" }, { skill:"Memory Safety", category:"CONCEPT" }, { skill:"Systems Programming", category:"PATTERN" }],
  Java:        [{ skill:"Java", category:"LANGUAGE" }, { skill:"OOP Design", category:"PATTERN" }, { skill:"Spring Boot", category:"FRAMEWORK" }, { skill:"Maven", category:"TOOL" }],
  Ruby:        [{ skill:"Ruby", category:"LANGUAGE" }, { skill:"Rails", category:"FRAMEWORK" }, { skill:"MVC Pattern", category:"PATTERN" }],
  PHP:         [{ skill:"PHP", category:"LANGUAGE" }, { skill:"Laravel", category:"FRAMEWORK" }, { skill:"Composer", category:"TOOL" }],
  "C#":        [{ skill:"C#", category:"LANGUAGE" }, { skill:".NET", category:"FRAMEWORK" }, { skill:"LINQ", category:"CONCEPT" }],
  Dart:        [{ skill:"Dart", category:"LANGUAGE" }, { skill:"Flutter", category:"FRAMEWORK" }, { skill:"Mobile Development", category:"CONCEPT" }],
  Swift:       [{ skill:"Swift", category:"LANGUAGE" }, { skill:"iOS Development", category:"CONCEPT" }, { skill:"Xcode", category:"TOOL" }],
  Kotlin:      [{ skill:"Kotlin", category:"LANGUAGE" }, { skill:"Android", category:"FRAMEWORK" }, { skill:"Coroutines", category:"CONCEPT" }],
  "C++":       [{ skill:"C++", category:"LANGUAGE" }, { skill:"Systems Programming", category:"PATTERN" }, { skill:"Memory Management", category:"CONCEPT" }],
  C:           [{ skill:"C", category:"LANGUAGE" }, { skill:"Systems Programming", category:"PATTERN" }, { skill:"Pointers", category:"CONCEPT" }],
  Shell:       [{ skill:"Shell Scripting", category:"LANGUAGE" }, { skill:"Linux", category:"TOOL" }, { skill:"DevOps", category:"CONCEPT" }],
  HTML:        [{ skill:"HTML", category:"LANGUAGE" }, { skill:"CSS", category:"LANGUAGE" }, { skill:"Web Development", category:"CONCEPT" }],
};

const HINTS: Array<[RegExp, SkillDef]> = [
  [/next|nextjs/i,           { skill:"Next.js",        category:"FRAMEWORK" }],
  [/react/i,                 { skill:"React",           category:"FRAMEWORK" }],
  [/vue|nuxt/i,              { skill:"Vue.js",          category:"FRAMEWORK" }],
  [/angular/i,               { skill:"Angular",         category:"FRAMEWORK" }],
  [/svelte/i,                { skill:"Svelte",          category:"FRAMEWORK" }],
  [/express|fastify|koa/i,   { skill:"Express.js",      category:"FRAMEWORK" }],
  [/django/i,                { skill:"Django",          category:"FRAMEWORK" }],
  [/flask/i,                 { skill:"Flask",           category:"FRAMEWORK" }],
  [/fastapi/i,               { skill:"FastAPI",         category:"FRAMEWORK" }],
  [/graphql/i,               { skill:"GraphQL",         category:"TOOL"      }],
  [/docker|container/i,      { skill:"Docker",          category:"TOOL"      }],
  [/k8s|kubernetes/i,        { skill:"Kubernetes",      category:"TOOL"      }],
  [/prisma/i,                { skill:"Prisma ORM",      category:"TOOL"      }],
  [/postgres|pg$/i,          { skill:"PostgreSQL",      category:"TOOL"      }],
  [/mongo/i,                 { skill:"MongoDB",         category:"TOOL"      }],
  [/redis/i,                 { skill:"Redis",           category:"TOOL"      }],
  [/api|rest/i,              { skill:"REST API",        category:"PATTERN"   }],
  [/auth|oauth/i,            { skill:"Authentication",  category:"CONCEPT"   }],
  [/test|jest|pytest|spec/i, { skill:"Testing",         category:"CONCEPT"   }],
  [/cli/i,                   { skill:"CLI Tools",       category:"TOOL"      }],
  [/ml|machine.?learning/i,  { skill:"Machine Learning",category:"CONCEPT"   }],
  [/tailwind/i,              { skill:"Tailwind CSS",    category:"FRAMEWORK" }],
  [/web3|blockchain|crypto/i,{ skill:"Web3",            category:"CONCEPT"   }],
];

function detectArch(name: string, desc: string | null): { pattern: string; confidence: number } {
  const t = `${name} ${desc ?? ""}`.toLowerCase();
  if (/microservice|micro.service/.test(t)) return { pattern: "microservice", confidence: 85 };
  if (/serverless|lambda/.test(t))           return { pattern: "serverless",  confidence: 80 };
  if (/event|queue|pubsub/.test(t))          return { pattern: "event-driven",confidence: 82 };
  if (/website|landing|portfolio|blog/.test(t)) return { pattern: "jamstack", confidence: 78 };
  if (/mvc|model.view/.test(t))              return { pattern: "MVC",         confidence: 80 };
  if (/api|rest|graphql/.test(t))            return { pattern: "layered",     confidence: 75 };
  return { pattern: "layered", confidence: 60 };
}

const PATTERN_DESCS: Record<string, (lang: string, name: string) => string> = {
  error_handling:     (l, n) => `${l} error handling with structured exception management in ${n}`,
  testing:            (_l, _n) => `Test coverage patterns indicating quality-focused development`,
  api_design:         (_l, n) => `RESTful API design with consistent endpoint conventions in ${n}`,
  state_management:   (l, _n) => `State management using ${l}-idiomatic patterns`,
  naming_convention:  (l, _n) => `Naming conventions following ${l} community standards`,
  architecture:       (l, _n) => `${l} architectural patterns with clear separation of concerns`,
};

export function mockAnalyzeRepo(repo: {
  name: string;
  description: string | null;
  primaryLanguage: string | null;
  stars: number;
  forks: number;
  size: number;
}): MockAnalysisResult {
  const seed = repo.name;
  const lang = repo.primaryLanguage ?? "JavaScript";
  const text = `${repo.name} ${repo.description ?? ""}`;

  const seen = new Set<string>();
  const skills: SkillDef[] = [];
  for (const s of (LANG_SKILLS[lang] ?? LANG_SKILLS["JavaScript"])) {
    if (!seen.has(s.skill)) { seen.add(s.skill); skills.push(s); }
  }
  for (const [pat, def] of HINTS) {
    if (pat.test(text) && !seen.has(def.skill)) { seen.add(def.skill); skills.push(def); }
  }
  if (!seen.has("Git")) skills.push({ skill:"Git", category:"TOOL" });
  if (repo.stars > 5 && !seen.has("Open Source")) skills.push({ skill:"Open Source", category:"CONCEPT" });

  const allSkills = skills.slice(0, 8);
  const profLevels: Array<"beginner"|"intermediate"|"advanced"|"expert"> = ["beginner","intermediate","advanced","expert"];
  const repoScore = Math.min(40 + repo.stars * 2 + repo.forks, 85);

  const skillsDemonstrated = allSkills.map((def, i) => {
    const s = seeded(seed, `sk${i}`, Math.max(40, repoScore - 20), Math.min(95, repoScore + 10));
    const idx = s < 50 ? 0 : s < 65 ? 1 : s < 82 ? 2 : 3;
    return {
      skill: def.skill,
      category: def.category,
      proficiency: profLevels[idx],
      evidence: `Detected in ${repo.name} — ${def.category.toLowerCase()} usage from codebase structure`,
    };
  });

  const { pattern, confidence } = detectArch(repo.name, repo.description);
  const complexity = seeded(seed, "cmx", Math.max(25, repoScore - 15), Math.min(95, repoScore + 10));

  const q = (k: string) => seeded(seed, k, Math.max(45, repoScore - 10), Math.min(92, repoScore + 8));
  const qualityIndicators = {
    namingConsistency:    q("q0"),
    separationOfConcerns: q("q1"),
    dryAdherence:         q("q2"),
    overallQuality:       q("q3"),
  };

  const patTypes = ["error_handling","testing","api_design","naming_convention","architecture"] as const;
  const patCount = seeded(seed, "pc", 2, 4);
  const codePatterns = Array.from({ length: patCount }, (_, i) => ({
    type: patTypes[i % patTypes.length],
    description: (PATTERN_DESCS[patTypes[i % patTypes.length]] ?? (() => "Pattern observed"))(lang, repo.name),
    quality: seeded(seed, `pt${i}`, 50, 88),
  }));

  const desc = repo.description ?? `a ${lang} project`;
  const article = /^[aeiou]/i.test(desc) ? "" : "a ";
  const summary = `${repo.name} is ${article}${desc}. The codebase demonstrates ${lang} development with a ${pattern} architectural approach.`;

  const highlights = [`Primary language: ${lang}`, `Architecture: ${pattern}`, `${allSkills.length} skills identified`];
  if (repo.stars > 0) highlights.push(`${repo.stars} GitHub stars`);
  if (skillsDemonstrated.some(s => s.proficiency === "expert")) highlights.push("Expert-level patterns detected");

  return {
    architecturePattern: pattern,
    architectureConfidence: confidence,
    codePatterns,
    qualityIndicators,
    skillsDemonstrated,
    complexityScore: complexity,
    projectSummary: summary,
    projectHighlights: highlights,
    isTutorialClone: false,
    tutorialConfidence: seeded(seed, "tut", 0, 20),
  };
}
