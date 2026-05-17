"""Capture inner page screenshots from the 4 MyGuest demos.

Usage:
  # 1. Start a local server (from repo root):
  #    python -m http.server 8030 --directory public
  #
  # 2. Run this script:
  #    python scripts/marketing/capture_demo_screens.py --base-url http://localhost:8030
  #
  # Output: marketing/social-post-system/assets/screenshots/{slug}/{screen}.png
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL_DEFAULT = "http://localhost:8030"
OUTPUT_BASE = Path("marketing/social-post-system/assets/screenshots")

DEMOS = [
    {"slug": "ocean-drive-retreat",  "file": "villas/ocean-drive-retreat/en.html",  "label": "Ocean Drive Retreat"},
    {"slug": "the-soho-loft",        "file": "villas/the-soho-loft/en.html",        "label": "The SoHo Loft"},
    {"slug": "casa-selva-tulum",     "file": "villas/casa-selva-tulum/en.html",      "label": "Casa Selva Tulum"},
    {"slug": "le-marais-flat",       "file": "villas/le-marais-flat/en.html",        "label": "Le Marais Flat"},
]

# screen id -> output filename
SCREENS = [
    ("menu-sheet",          "menu"),
    ("places-to-eat-screen","local-guide"),
    ("house-rules-screen",  "house-rules"),
    ("wifi-screen",         "wifi"),
    ("checkin-screen",      "checkin"),
    ("things-to-do-screen", "things-to-do"),
    ("welcome-screen",      "welcome"),
]


def capture_screen(page, base_url: str, demo: dict, screen_id: str, out_path: Path) -> bool:
    url = f"{base_url}/{demo['file']}#{screen_id}"
    page.goto(url, wait_until="networkidle", timeout=60_000)
    page.wait_for_timeout(1500)

    # Try to activate the target section (hash navigation)
    page.evaluate(f"""
        const el = document.getElementById('{screen_id}');
        if (el) {{
            el.scrollIntoView({{behavior: 'instant', block: 'start'}});
            // Trigger hash-based navigation if any
            el.classList.add('active');
        }}
    """)
    page.wait_for_timeout(800)

    # Check if the section exists and has content
    section = page.query_selector(f"#{screen_id}")
    if not section:
        print(f"    SKIP: #{screen_id} not found in {demo['slug']}")
        return False

    # Check if section is visible (some may be hidden with data-hide-if-empty when content is empty)
    is_visible = page.evaluate(f"""
        const el = document.getElementById('{screen_id}');
        if (!el) return false;
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && rect.height > 50;
    """)
    if not is_visible:
        # Try making it visible by targeting it
        page.evaluate(f"""
            const el = document.getElementById('{screen_id}');
            if (el) {{
                el.style.display = 'block';
                el.style.visibility = 'visible';
            }}
        """)
        page.wait_for_timeout(500)

    # Get the app-shell bounds (the phone container)
    shell = page.query_selector(".app-shell")
    if not shell:
        shell = section

    # Screenshot just the section, clipped to phone width
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shell_box = shell.bounding_box()
    if not shell_box:
        print(f"    SKIP: no bounding box for #{screen_id}")
        return False

    # Clip to section within the shell
    section_box = section.bounding_box()
    if section_box:
        clip = {
            "x": shell_box["x"],
            "y": section_box["y"],
            "width": shell_box["width"],
            "height": min(section_box["height"], 900),  # max 900px tall
        }
    else:
        clip = {
            "x": shell_box["x"],
            "y": shell_box["y"],
            "width": shell_box["width"],
            "height": min(shell_box["height"], 900),
        }

    page.screenshot(path=str(out_path), clip=clip)
    print(f"    -> {out_path}")
    return True


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL_DEFAULT)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    total = 0
    errors = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Mobile-width viewport
        page = browser.new_page(
            viewport={"width": 430, "height": 932},
            device_scale_factor=2,
        )

        for demo in DEMOS:
            print(f"\n[{demo['label']}]")
            out_dir = OUTPUT_BASE / demo["slug"]
            out_dir.mkdir(parents=True, exist_ok=True)

            for screen_id, fname in SCREENS:
                out_path = out_dir / f"{fname}.png"
                print(f"  Capturing #{screen_id}...")
                try:
                    ok = capture_screen(page, base_url, demo, screen_id, out_path)
                    if ok:
                        total += 1
                except Exception as exc:
                    print(f"  ERROR: {exc}", file=sys.stderr)
                    errors += 1

        browser.close()

    print(f"\n=== Done: {total} screenshots, {errors} errors ===")
    print(f"Output: {OUTPUT_BASE.resolve()}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
