#!/usr/bin/env python3
"""Take screenshots of all CodeDNA pages using Playwright."""
import os, time
from playwright.sync_api import sync_playwright

OUT = "/home/sloth/Skill/CodeDNA/report-screenshots"
os.makedirs(OUT, exist_ok=True)
BASE = "http://localhost:3000"

def shot(page, path, name, wait=2500, full=True):
    try:
        page.goto(f"{BASE}{path}", wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(wait)
        fpath = os.path.join(OUT, name)
        page.screenshot(path=fpath, full_page=full)
        print(f"  ✓ {name}")
        return fpath
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        return None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # ── Logged-out context (no cookies) ──────────────────────────────────────
    ctx_out = browser.new_context(viewport={"width": 1440, "height": 900})
    pg_out = ctx_out.new_page()
    print("=== Logged-out screenshots ===")
    shot(pg_out, "/",                    "01-landing-loggedout.png",  wait=3000)
    shot(pg_out, "/genome/zhnverse",     "10-public-profile.png",     wait=3000)
    shot(pg_out, "/api/widget/zhnverse", "11-widget-svg.png",         wait=2000, full=False)
    ctx_out.close()

    # ── Mobile viewport ───────────────────────────────────────────────────────
    ctx_mob = browser.new_context(viewport={"width": 375, "height": 812})
    pg_mob = ctx_mob.new_page()
    print("=== Mobile screenshots ===")
    shot(pg_mob, "/", "13-mobile-landing.png", wait=3000)
    ctx_mob.close()

    # ── Logged-in context (use GitHub OAuth session via storage state) ────────
    # We'll navigate to the app which requires login — capture whatever is visible
    ctx_in = browser.new_context(viewport={"width": 1440, "height": 900})
    pg_in = ctx_in.new_page()
    print("=== Logged-in screenshots (best-effort) ===")
    # Dashboard
    shot(pg_in, "/dashboard", "02-dashboard.png", wait=3000)
    # Genome page - helix view
    shot(pg_in, "/genome", "03-genome-helix.png", wait=3500)
    # Try to switch view - Radar
    try:
        pg_in.goto(f"{BASE}/genome", wait_until="networkidle", timeout=15000)
        pg_in.wait_for_timeout(2000)
        # Look for Radar button
        btns = pg_in.query_selector_all("button")
        for btn in btns:
            txt = (btn.inner_text() or "").strip().lower()
            if "radar" in txt:
                btn.click()
                pg_in.wait_for_timeout(2000)
                pg_in.screenshot(path=os.path.join(OUT, "04-genome-radar.png"), full_page=True)
                print("  ✓ 04-genome-radar.png")
                break
        # Skill tree
        for btn in pg_in.query_selector_all("button"):
            txt = (btn.inner_text() or "").strip().lower()
            if "tree" in txt or "skill" in txt:
                btn.click()
                pg_in.wait_for_timeout(2000)
                pg_in.screenshot(path=os.path.join(OUT, "05-genome-skilltree.png"), full_page=True)
                print("  ✓ 05-genome-skilltree.png")
                break
    except Exception as e:
        print(f"  ✗ view switch: {e}")

    shot(pg_in, "/projects",  "06-projects.png",  wait=3000)
    shot(pg_in, "/growth",    "07-growth.png",    wait=3500)
    shot(pg_in, "/analysis",  "08-analysis.png",  wait=3000)
    shot(pg_in, "/settings",  "09-settings.png",  wait=2500)
    ctx_in.close()

    # ── Landing page logged-in ────────────────────────────────────────────────
    ctx_li = browser.new_context(viewport={"width": 1440, "height": 900})
    pg_li = ctx_li.new_page()
    shot(pg_li, "/", "01b-landing-loggedin.png", wait=3000)
    # Try light mode
    try:
        pg_li.goto(f"{BASE}/", wait_until="networkidle", timeout=15000)
        pg_li.evaluate("document.documentElement.classList.remove('dark'); document.documentElement.classList.add('light');")
        pg_li.wait_for_timeout(1500)
        pg_li.screenshot(path=os.path.join(OUT, "12-landing-lightmode.png"), full_page=True)
        print("  ✓ 12-landing-lightmode.png")
    except Exception as e:
        print(f"  ✗ light mode: {e}")
    ctx_li.close()

    browser.close()

print(f"\nDone! Screenshots saved to: {OUT}")
print("Files:", sorted(os.listdir(OUT)))
