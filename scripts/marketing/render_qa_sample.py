"""Render 8 QA sample pins — one per template — for visual review before full 32-pin run."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

CAMPAIGN_PATH = Path("data/marketing/pinterest_campaign_v2.json")
SCREENSHOTS_BASE = Path("public/marketing/pinterest-v2/assets/screenshots")
OUTPUT_DIR = Path("output/pinterest-v2/qa-sample")

TEMPLATES_ORDER = [
    "template-01-before-after",
    "template-02-demo-visual",
    "template-03-printable-pdf",
    "template-04-trilingual",
    "template-05-stop-repeating",
    "template-06-existing-materials",
    "template-07-private-details",
    "template-08-style-showcase",
]

STYLE_CLASS_MAP = {
    "Coastal": "style-coastal",
    "Minimalist": "style-minimalist",
    "Sunset": "style-sunset",
    "Classic": "style-classic",
}

PLACEHOLDER_COLOR_MAP = {
    "Coastal": "#b8dce8",
    "Minimalist": "#d0d0d0",
    "Sunset": "#f5c4a8",
    "Classic": "#c8b880",
}


def find_screenshot(slug: str) -> str | None:
    """Return HTTP-relative URL for screenshot (served by local server)."""
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
        }
        """,
        [pin, style_class, screenshot_path, placeholder_color],
    )


def render_pin(page, url: str, output_path: Path, pin: dict) -> None:
    screenshot_path = find_screenshot(pin.get("slug", ""))
    if not screenshot_path:
        print(f"  WARNING: no screenshot for {pin['slug']} — using placeholder")

    page.goto(url, wait_until="networkidle", timeout=120_000)
    page.wait_for_timeout(1200)

    apply_pin_data(page, pin, screenshot_path)
    if screenshot_path:
        # Wait for the injected screenshot image to finish loading
        page.wait_for_function(
            "document.querySelector('.v2-screenshot') && document.querySelector('.v2-screenshot').complete",
            timeout=15_000,
        )
    page.wait_for_timeout(400)

    pin_element = page.locator("main.pin").first
    pin_element.wait_for(state="visible", timeout=30_000)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(300)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pin_element.screenshot(path=str(output_path))
    print(f"  -> {output_path}")


PREFERRED_STYLE: dict[str, str] = {
    "template-01-before-after": "Coastal",
    "template-02-demo-visual": "Minimalist",
    "template-03-printable-pdf": "Sunset",
    "template-04-trilingual": "Classic",
    "template-05-stop-repeating": "Coastal",
    "template-06-existing-materials": "Minimalist",
    "template-07-private-details": "Sunset",
    "template-08-style-showcase": "Classic",
}


def select_qa_pins(pins: list[dict]) -> list[dict]:
    """Select one pin per template (preferred style), in template order."""
    by_template: dict[str, list[dict]] = {}
    for pin in pins:
        t = pin.get("template", "")
        by_template.setdefault(t, []).append(pin)

    result = []
    for t in TEMPLATES_ORDER:
        candidates = by_template.get(t, [])
        if not candidates:
            continue
        preferred_style = PREFERRED_STYLE.get(t, "Coastal")
        match = next((p for p in candidates if p.get("style") == preferred_style), candidates[0])
        result.append(match)
    return result


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Render 8 QA sample pins.")
    parser.add_argument("--base-url", required=True, help="Base URL for templates directory.")
    parser.add_argument("--campaign", default=str(CAMPAIGN_PATH))
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
    qa_pins = select_qa_pins(pins)

    if not qa_pins:
        print("ERROR: no pins selected.", file=sys.stderr)
        return 1

    print(f"Selected {len(qa_pins)} QA pins:")
    for p in qa_pins:
        print(f"  {p['id']:10s} {p['template']:40s} [{p['style']:10s}] {p['property']}")
    print()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1000, "height": 1500},
            device_scale_factor=2,
        )

        for i, pin in enumerate(qa_pins, start=1):
            import re as _re
            template_file = pin.get("template", "") + ".html"
            template_slug = _re.sub(r"^template-\d+-", "", pin["template"])
            output_name = f"qa-{i:02d}-{template_slug}.png"
            output_path = OUTPUT_DIR / output_name
            url = urljoin(base_url, template_file)

            print(f"[{i}/8] {pin['id']} — {pin['style']} — {pin['template']}")

            try:
                render_pin(page, url, output_path, pin)
            except PlaywrightTimeoutError as exc:
                msg = f"Timeout: {pin['id']}: {exc}"
                print(f"  ERROR: {msg}", file=sys.stderr)
                errors.append(msg)

        browser.close()

    generated = list(OUTPUT_DIR.glob("qa-*.png"))
    print(f"\n=== QA Sample Summary ===")
    print(f"Rendered: {len(generated)}/8")
    print(f"Output:   {OUTPUT_DIR.resolve()}")

    if errors:
        print(f"Errors:   {len(errors)}")
        for e in errors:
            print(f"  ERROR: {e}")
        return 1

    if len(generated) < 8:
        print(f"ERROR: only {len(generated)} PNGs found, expected 8.", file=sys.stderr)
        return 1

    print("\nSample pins ready for visual review.")
    print("Open the output folder and check each pin before approving full 32-pin render.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
