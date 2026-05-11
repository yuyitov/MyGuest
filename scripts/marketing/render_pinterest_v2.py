"""Render MyGuest Pinterest v2 HTML templates to PNG files (32 pins)."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

CAMPAIGN_PATH = Path("data/marketing/pinterest_campaign_v2.json")
SCREENSHOTS_BASE = Path("public/marketing/pinterest-v2/assets/screenshots")
PLACEHOLDER_COLOR_MAP = {
    "Coastal": "#b8dce8",
    "Minimalist": "#d0d0d0",
    "Sunset": "#f5c4a8",
    "Classic": "#c8b880",
}
STYLE_CLASS_MAP = {
    "Coastal": "style-coastal",
    "Minimalist": "style-minimalist",
    "Sunset": "style-sunset",
    "Classic": "style-classic",
}
EXPECTED_PIN_COUNT = 32


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "pin"


def safe_output_name(output_name: str, fallback: str) -> str:
    cleaned = Path(output_name or fallback).name
    if not cleaned.lower().endswith(".png"):
        cleaned = f"{cleaned}.png"
    return cleaned


def find_screenshot(pin: dict) -> str | None:
    """Return HTTP-relative URL for screenshot (served by local server)."""
    slug = pin.get("slug", "")
    if not slug:
        return None
    screenshot_dir = SCREENSHOTS_BASE / slug
    for candidate in ("full-demo.png", "hero.png", "guide-section.png", "print-preview.png"):
        if (screenshot_dir / candidate).exists():
            return f"/assets/screenshots/{slug}/{candidate}"
    return None


def apply_pin_data(page, pin: dict, screenshot_path: str | None) -> None:
    style_class = STYLE_CLASS_MAP.get(pin.get("style", ""), "style-coastal")
    placeholder_color = PLACEHOLDER_COLOR_MAP.get(pin.get("style", ""), "#d0d0d0")

    page.evaluate(
        """
        ([pin, styleClass, screenshotPath, placeholderColor]) => {
            document.body.className = styleClass;

            const setText = (sel, val) => {
                const el = document.querySelector(sel);
                if (el && val !== undefined && val !== null) el.textContent = val;
            };

            setText('.v2-headline', pin.headline);
            setText('.v2-sub', pin.subheadline);
            setText('.v2-supporting-line', pin.supporting_line);

            const cta = document.querySelector('.v2-cta');
            if (cta) {
                cta.href = pin.destination_url || '#';
                cta.innerHTML = '';
                cta.appendChild(document.createTextNode(pin.cta || 'Get started'));
                const arrow = document.createElement('span');
                arrow.textContent = ' →';
                cta.appendChild(arrow);
            }

            const badgesWrap = document.querySelector('.v2-badges');
            if (badgesWrap && Array.isArray(pin.badges)) {
                badgesWrap.innerHTML = '';
                pin.badges.slice(0, 3).forEach(text => {
                    const badge = document.createElement('div');
                    badge.className = 'v2-badge';
                    badge.textContent = String(text);
                    badgesWrap.appendChild(badge);
                });
            }

            const img = document.querySelector('.v2-screenshot');
            if (img) {
                if (screenshotPath) {
                    img.src = screenshotPath;
                    img.style.display = 'block';
                } else {
                    img.style.display = 'none';
                    const wrap = img.closest('.v2-screenshot-wrap');
                    if (wrap) wrap.style.background = placeholderColor;
                }
            }

            const propName = document.querySelector('.v2-property-name');
            if (propName) propName.textContent = pin.property || '';

            const styleName = document.querySelector('.v2-style-name');
            if (styleName) styleName.textContent = pin.style || '';

            if (pin.output_name) {
                document.title = pin.output_name.replace(/\\.png$/i, '');
            }
        }
        """,
        [pin, style_class, screenshot_path, placeholder_color],
    )


def render_pin(page, url: str, output_path: Path, wait_ms: int, pin: dict) -> dict:
    screenshot_path = find_screenshot(pin)
    if not screenshot_path:
        print(f"  WARNING: no screenshot found for {pin['slug']} — using placeholder color")

    page.goto(url, wait_until="networkidle", timeout=120_000)
    page.wait_for_timeout(wait_ms)

    apply_pin_data(page, pin, screenshot_path)
    page.wait_for_timeout(400)

    pin_element = page.locator("main.pin").first
    pin_element.wait_for(state="visible", timeout=30_000)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(300)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pin_element.screenshot(path=str(output_path))

    return {
        "pin_id": pin.get("id"),
        "style": pin.get("style"),
        "property": pin.get("property"),
        "template": pin.get("template"),
        "headline": pin.get("headline"),
        "cta": pin.get("cta"),
        "destination_url": pin.get("destination_url"),
        "output_name": pin.get("output_name"),
        "output_path": str(output_path),
        "screenshot_used": screenshot_path or "PLACEHOLDER",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render MyGuest Pinterest v2 pins to PNG.")
    parser.add_argument("--base-url", required=True, help="Base URL for the templates directory.")
    parser.add_argument("--output-dir", default="output/pinterest-v2/pins", help="Output directory for PNGs.")
    parser.add_argument("--wait-ms", type=int, default=1200, help="Extra wait after page load (ms).")
    parser.add_argument("--campaign", default=str(CAMPAIGN_PATH), help="Path to pinterest_campaign_v2.json.")
    args = parser.parse_args()

    base_url = args.base_url
    if not base_url.endswith("/"):
        base_url += "/"

    campaign_path = Path(args.campaign)
    if not campaign_path.exists():
        print(f"ERROR: campaign file not found: {campaign_path}", file=sys.stderr)
        return 1

    data = json.loads(campaign_path.read_text(encoding="utf-8"))
    pins = data.get("pins", [])
    if not pins:
        print("ERROR: no pins found.", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir = output_dir.parent / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    warnings: list[str] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": 1000, "height": 1500},
                device_scale_factor=2,
            )

            for index, pin in enumerate(pins, start=1):
                template_file = pin.get("template", "") + ".html"
                output_name = safe_output_name(pin.get("output_name", ""), f"pin-{index:03d}.png")
                output_path = output_dir / output_name
                url = urljoin(base_url, template_file)

                print(f"[{index:02d}/{len(pins)}] {pin.get('id')} — {pin.get('style')} {pin.get('template')}")

                try:
                    result = render_pin(page, url, output_path, args.wait_ms, pin)
                    manifest.append(result)
                    print(f"  -> {output_path}")
                except PlaywrightTimeoutError as exc:
                    msg = f"Timeout rendering {pin.get('id')}: {exc}"
                    print(f"  ERROR: {msg}", file=sys.stderr)
                    warnings.append(msg)
                    continue

            browser.close()
    except Exception as exc:  # noqa: BLE001
        print(f"Fatal error: {exc}", file=sys.stderr)
        return 1

    manifest_path = metadata_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest -> {manifest_path}")

    upload_csv_path = metadata_dir / "pinterest_upload_sheet.csv"
    upload_fields = [
        "pin_id", "file_name", "board_name", "pin_title", "pin_description",
        "destination_url", "alt_text", "keywords", "style", "property", "template", "status",
    ]
    with open(upload_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=upload_fields)
        writer.writeheader()
        for pin in pins:
            keywords_str = " | ".join(pin.get("keywords", []))
            output_name = safe_output_name(pin.get("output_name", ""), "")
            png_path = output_dir / output_name
            status = "ready" if png_path.exists() else "MISSING"
            writer.writerow({
                "pin_id": pin["id"],
                "file_name": pin["output_name"],
                "board_name": pin["board_name"],
                "pin_title": pin["pin_title"],
                "pin_description": pin["pin_description"],
                "destination_url": pin["destination_url"],
                "alt_text": pin["alt_text"],
                "keywords": keywords_str,
                "style": pin["style"],
                "property": pin["property"],
                "template": pin["template"],
                "status": status,
            })
    print(f"Upload CSV -> {upload_csv_path}")

    tracking_csv_path = metadata_dir / "pinterest_tracking_sheet.csv"
    tracking_fields = [
        "pin_id", "file_name", "board_name", "destination_url", "pinterest_url",
        "publish_date", "status", "impressions", "saves", "outbound_clicks",
        "landing_visits", "cta_clicks", "leads", "purchases", "ctr",
        "lead_rate", "purchase_rate", "notes",
    ]
    with open(tracking_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tracking_fields)
        writer.writeheader()
        for pin in pins:
            writer.writerow({
                "pin_id": pin["id"],
                "file_name": pin["output_name"],
                "board_name": pin["board_name"],
                "destination_url": pin["destination_url"],
                "pinterest_url": "", "publish_date": "", "status": "pending",
                "impressions": "", "saves": "", "outbound_clicks": "",
                "landing_visits": "", "cta_clicks": "", "leads": "",
                "purchases": "", "ctr": "", "lead_rate": "", "purchase_rate": "", "notes": "",
            })
    print(f"Tracking CSV -> {tracking_csv_path}")

    actual_count = len(manifest)
    print(f"\n=== Render summary ===")
    print(f"Pins rendered:   {actual_count}")
    print(f"Pins expected:   {EXPECTED_PIN_COUNT}")
    if warnings:
        print(f"Warnings:        {len(warnings)}")
        for w in warnings:
            print(f"  WARNING: {w}")

    if actual_count < EXPECTED_PIN_COUNT:
        print(f"ERROR: rendered {actual_count} pins, expected {EXPECTED_PIN_COUNT}.", file=sys.stderr)
        return 1

    print(f"Output dir: {output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
