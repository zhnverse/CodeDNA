interface Entry { count: number; resetAt: number }

const store = new Map<string, Entry>();

// Clean up stale entries periodically to avoid memory leaks
setInterval(() => {
  const now = Date.now();
  store.forEach((v, k) => { if (v.resetAt < now) store.delete(k); });
}, 300_000);

export function rateLimit(
  ip: string,
  limit = 100,
  windowMs = 3_600_000
): { allowed: boolean; remaining: number; reset: number } {
  const now = Date.now();
  const entry = store.get(ip);

  if (!entry || entry.resetAt < now) {
    const resetAt = now + windowMs;
    store.set(ip, { count: 1, resetAt });
    return { allowed: true, remaining: limit - 1, reset: resetAt };
  }

  if (entry.count >= limit) {
    return { allowed: false, remaining: 0, reset: entry.resetAt };
  }

  entry.count++;
  return { allowed: true, remaining: limit - entry.count, reset: entry.resetAt };
}

export function rateLimitHeaders(result: ReturnType<typeof rateLimit>) {
  return {
    "X-RateLimit-Remaining": String(result.remaining),
    "X-RateLimit-Reset": String(Math.ceil(result.reset / 1000)),
  };
}
