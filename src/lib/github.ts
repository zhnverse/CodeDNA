const GITHUB_API = "https://api.github.com";

// ── Types ──────────────────────────────────────────────────────────────────

export interface GitHubRepo {
  id: number;
  name: string;
  full_name: string;
  html_url: string;
  description: string | null;
  language: string | null;
  stargazers_count: number;
  forks_count: number;
  size: number;
  private: boolean;
  updated_at: string;
  owner: { login: string };
  topics: string[];
}

export interface GitHubCommit {
  sha: string;
  commit: { message: string; author: { name: string; date: string } };
  stats?: { additions: number; deletions: number; total: number };
}

export interface GitHubPR {
  number: number;
  title: string;
  state: string;
  merged_at: string | null;
  created_at: string;
}

export interface GitHubTreeItem {
  path: string;
  type: "blob" | "tree";
  size?: number;
  sha: string;
}

// ── Core fetch ─────────────────────────────────────────────────────────────

async function ghFetch(
  token: string,
  path: string,
  opts: RequestInit = {},
  etag?: string
): Promise<{ data: unknown; status: number; newEtag?: string }> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
    ...(opts.headers as Record<string, string>),
  };
  if (etag) headers["If-None-Match"] = etag;

  const res = await fetch(`${GITHUB_API}${path}`, { ...opts, headers, next: { revalidate: 0 } });

  const remaining = parseInt(res.headers.get("X-RateLimit-Remaining") ?? "60");
  if (remaining < 5) {
    const reset = parseInt(res.headers.get("X-RateLimit-Reset") ?? "0") * 1000;
    const wait = Math.min(Math.max(0, reset - Date.now()), 60_000);
    if (wait > 0) await new Promise((r) => setTimeout(r, wait));
  }

  if (res.status === 304) return { data: null, status: 304 };
  if (!res.ok) throw new Error(`GitHub API ${res.status}: ${path}`);

  const data = await res.json();
  return { data, status: res.status, newEtag: res.headers.get("ETag") ?? undefined };
}

async function ghFetchAll<T>(token: string, path: string): Promise<T[]> {
  const results: T[] = [];
  let page = 1;
  while (true) {
    const sep = path.includes("?") ? "&" : "?";
    const { data } = await ghFetch(token, `${path}${sep}per_page=100&page=${page}`);
    const items = data as T[];
    if (!items?.length) break;
    results.push(...items);
    if (items.length < 100) break;
    page++;
  }
  return results;
}

// ── isCodeFile ─────────────────────────────────────────────────────────────

const SKIP_EXTS = new Set([
  ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp",
  ".pdf", ".zip", ".tar", ".gz", ".wasm", ".bin", ".exe", ".dll",
  ".ttf", ".woff", ".woff2", ".eot", ".mp4", ".mp3", ".wav",
]);
const SKIP_FILES = new Set([
  "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
  "composer.lock", "Gemfile.lock", "Cargo.lock", "poetry.lock",
  ".gitignore", ".gitattributes", ".editorconfig", ".prettierrc",
]);
const SKIP_DIRS = ["node_modules/", "vendor/", ".git/", "dist/", "build/", "__pycache__/"];

export function isCodeFile(filename: string): boolean {
  if (SKIP_FILES.has(filename.split("/").pop() ?? "")) return false;
  const lower = filename.toLowerCase();
  if (SKIP_DIRS.some((d) => lower.includes(d))) return false;
  const dot = lower.lastIndexOf(".");
  if (dot !== -1 && SKIP_EXTS.has(lower.slice(dot))) return false;
  return true;
}

// ── Public API ─────────────────────────────────────────────────────────────

export async function fetchUserRepos(accessToken: string): Promise<GitHubRepo[]> {
  return ghFetchAll<GitHubRepo>(accessToken, "/user/repos?type=all&sort=updated");
}

export async function fetchRepoDetails(
  accessToken: string,
  owner: string,
  repo: string
): Promise<{
  languages: Record<string, number>;
  contributorCount: number;
  commitCount: number;
}> {
  const [langRes, contribRes, commitRes] = await Promise.allSettled([
    ghFetch(accessToken, `/repos/${owner}/${repo}/languages`),
    ghFetch(accessToken, `/repos/${owner}/${repo}/contributors?per_page=1&anon=true`),
    ghFetch(accessToken, `/repos/${owner}/${repo}/commits?per_page=1`),
  ]);

  return {
    languages: langRes.status === "fulfilled" ? (langRes.value.data as Record<string, number>) : {},
    contributorCount:
      contribRes.status === "fulfilled"
        ? (contribRes.value.data as unknown[])?.length ?? 0
        : 0,
    commitCount:
      commitRes.status === "fulfilled"
        ? (commitRes.value.data as unknown[])?.length ?? 0
        : 0,
  };
}

export async function fetchRepoTree(
  accessToken: string,
  owner: string,
  repo: string,
  branch = "HEAD"
): Promise<GitHubTreeItem[]> {
  const { data } = await ghFetch(
    accessToken,
    `/repos/${owner}/${repo}/git/trees/${branch}?recursive=1`
  );
  const tree = (data as { tree: GitHubTreeItem[] })?.tree ?? [];
  return tree.filter((f) => f.type === "blob" && isCodeFile(f.path));
}

export async function fetchFileContent(
  accessToken: string,
  owner: string,
  repo: string,
  path: string
): Promise<string | null> {
  try {
    const { data } = await ghFetch(accessToken, `/repos/${owner}/${repo}/contents/${path}`);
    const file = data as { size: number; content?: string; encoding?: string };
    if (!file || file.size > 100_000) return null;
    if (file.encoding === "base64" && file.content) {
      return Buffer.from(file.content.replace(/\n/g, ""), "base64").toString("utf-8");
    }
    return null;
  } catch {
    return null;
  }
}

export async function fetchCommitHistory(
  accessToken: string,
  owner: string,
  repo: string,
  perPage = 30
): Promise<GitHubCommit[]> {
  const { data } = await ghFetch(
    accessToken,
    `/repos/${owner}/${repo}/commits?per_page=${perPage}`
  );
  return (data as GitHubCommit[]) ?? [];
}

export async function fetchPullRequests(
  accessToken: string,
  owner: string,
  repo: string
): Promise<GitHubPR[]> {
  return ghFetchAll<GitHubPR>(accessToken, `/repos/${owner}/${repo}/pulls?state=all&sort=updated`);
}
