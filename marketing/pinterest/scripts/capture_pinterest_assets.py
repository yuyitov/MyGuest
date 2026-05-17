"""Capture screenshots of real MyGuest demo pages for Pinterest v2 assets."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

INVENTORY_PATH = Path("data/marketing/pinterest_demo_inventory.json")
BASE_SCREENSHOTS_DIR = Path("public/marketing/pinterest-v2/assets/screenshots")

CAPTURES = [
    {
        "name": "hero",
        "wait_selector": None,
        "scroll_to": 0,
        "clip": None,
        "full_page": False,
        "viewport": {"width": 390, "height": 844},
        "description": "Mobile hero / cover view",
    },
    {
        "name": "guide-section",
        "wait_selector": None,
        "scroll_to": 600,
        "clip": None,
        "full_page": False,
        "viewport": {"width": 390, "height": 844},
        "description": "Guide section — scrolled to content",
    },
    {
        "name": "full-demo",
        "wait_selector": None,
        "scroll_to": 0,
        "clip": None,
        "full_page": True,
        "viewport": {"width": 390, "height": 844},
        "description": "Full-page vertical screenshot",
    },
    {
        "name": "print-preview",
        "wait_selector": None,
        "scroll_to": 0,
        "clip": None,
        "full_page": False,
        "viewport": {"width": 794, "height": 1123},
        "description": "Print preview (PDF page dimensions)",
        "url_suffix": "print.html",
    },
]


def load_inventory() -> list[dict]:
    if not INVENTORY_PATH.exists():
        print(f"ERROR: inventory file not found: {INVENTORY_PATH}", file=sys.stderr)
        sys.exit(1)
    return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))


def capture_demo(page, demo: dict, capture: dict) -> tuple[bool, str]:
    slug = demo["slug"]
    name = capture["name"]
    output_dir = BASE_SCREENSHOTS_DIR / slug
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{name}.png"

    url_suffix = capture.get("url_suffix")
    if url_suffix:
        base = demo["demo_url"].rstrip("/")
        url = f"{base}/{url_suffix}"
    else:
        url = demo["demo_url"]

    try:
        page.set_viewport_size(capture["viewport"])
        print(f"  [{slug}] Navigating to {url} ...")
        page.goto(url, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(2000)

        scroll_to = capture.get("scroll_to", 0)
        if scroll_to:
            page.evaluate(f"window.scrollTo(0, {scroll_to})")
            page.wait_for_timeout(800)

        if capture.get("full_page"):
            page.screenshot(path=str(output_path), full_page=True)
        else:
            clip = capture.get("clip")
            if clip:
                page.screenshot(path=str(output_path), clip=clip)
            else:
                page.screenshot(path=str(output_path))

        print(f"  [{slug}] Saved {name}.png -> {output_path}")
        return True, str(output_path)

    except PlaywrightTimeoutError as exc:
        print(f"  WARNING [{slug}] Timeout capturing {name}: {exc}", file=sys.stderr)
        return False, ""
    except Exception as exc:  # noqa: BLE001
        print(f"  WARNING [{slug}] Error capturing {name}: {exc}", file=sys.stderr)
        return False, ""


def main() -> int:
    inventory = load_inventory()
    print(f"Loaded {len(inventory)} demos from {INVENTORY_PATH}")

    results: list[dict] = []
    errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for demo in inventory:
            slug = demo["slug"]
            style = demo["style"]
            print(f"\n[{style}] {demo['property']} ({slug})")

            for capture in CAPTURES:
                page = browser.new_page(viewport=capture["viewport"])
                ok, path = capture_demo(page, demo, capture)
                page.close()

                result = {
                    "slug": slug,
                    "style": style,
                    "capture": capture["name"],
                    "path": path,
                    "ok": ok,
                }
                results.append(result)
                if not ok:
                    errors.append(f"{slug}/{capture['name']}")

        browser.close()

    total = len(results)
    ok_count = sum(1 for r in results if r["ok"])
    print(f"\n=== Capture summary ===")
    print(f"Total attempted: {total}")
    print(f"Successful:      {ok_count}")
    print(f"Failed:          {len(errors)}")

    if errors:
        print(f"\nFailed captures (placeholders will be used during render):")
        for e in errors:
            print(f"  WARNING: {e}")

    manifest_path = BASE_SCREENSHOTS_DIR / "capture_manifest.json"
    manifest_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nManifest written -> {manifest_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
