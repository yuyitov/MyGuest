from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

DEFAULT_TEMPLATES = [
    "template-01-stop-questions.html",
    "template-02-pdf.html",
    "template-03-trilingual.html",
    "template-04-minutes.html",
    "template-05-one-link.html",
]


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "pin"


def render_pin(page, url: str, output_path: Path, wait_ms: int) -> dict:
    page.goto(url, wait_until="networkidle", timeout=120_000)
    page.wait_for_timeout(wait_ms)

    pin = page.locator("main.pin").first
    pin.wait_for(state="visible", timeout=30_000)

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(300)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pin.screenshot(path=str(output_path))

    return {
        "title": page.title(),
        "url": url,
        "output": str(output_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render MyGuest Pinterest HTML templates to PNG files.")
    parser.add_argument(
        "--base-url",
        required=True,
        help="Base URL that serves the /marketing/pinterest/ folder.",
    )
    parser.add_argument(
        "--output-dir",
        default="output/pinterest",
        help="Directory for generated PNG files.",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=1200,
        help="Extra wait time after load, in milliseconds.",
    )
    parser.add_argument(
        "--templates",
        nargs="*",
        default=DEFAULT_TEMPLATES,
        help="List of template filenames to render.",
    )
    args = parser.parse_args()

    base_url = args.base_url
    if not base_url.endswith("/"):
        base_url += "/"

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": 1000, "height": 1500},
                device_scale_factor=2,
            )

            for idx, template in enumerate(args.templates, start=1):
                filename = f"pin-{idx:02d}-{slugify(Path(template).stem)}.png"
                target_path = output_dir / filename
                url = urljoin(base_url, template)

                try:
                    result = render_pin(page, url, target_path, args.wait_ms)
                except PlaywrightTimeoutError as exc:
                    print(f"ERROR rendering {url}: {exc}", file=sys.stderr)
                    continue

                manifest.append(result)
                print(f"Rendered {template} -> {target_path}")

            browser.close()
    except Exception as exc:  # noqa: BLE001
        print(f"Fatal error: {exc}", file=sys.stderr)
        return 1

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote manifest -> {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
