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

DEFAULT_VARIATIONS_PATH = "public/marketing/pinterest/pin_variations.json"

REQUIRED_PIN_FIELDS = [
    "template",
    "headline",
    "subheadline",
    "badges",
    "supporting_line",
    "cta",
    "link",
    "output_name",
]

PROHIBITED_COPY_PATTERNS = [
    r"upload your welcome book",
    r"ai reads",
    r"no manual input",
    r"send your pdf",
    r"extract everything",
    r"upload your canva",
    r"fully automated document extraction",
    r"no need to fill out a form",
    r"just upload your book",
    r"no form needed",
    r"document extraction",
    r"pdf extraction",
    r"canva extraction",
    r"photo extraction",
]


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "pin"


def safe_output_name(output_name: str, fallback: str) -> str:
    cleaned = Path(output_name or fallback).name
    if not cleaned.lower().endswith(".png"):
        cleaned = f"{cleaned}.png"
    return cleaned


def validate_safe_copy(pin: dict, index: int) -> None:
    copy_parts = [
        str(pin.get("headline", "")),
        str(pin.get("subheadline", "")),
        str(pin.get("supporting_line", "")),
        str(pin.get("cta", "")),
        " ".join(str(badge) for badge in pin.get("badges", [])),
    ]
    combined = " ".join(copy_parts).lower()

    for pattern in PROHIBITED_COPY_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            raise ValueError(
                f"Pin #{index} contains prohibited MVP copy: {pattern!r}. "
                "Do not promise AI document reading, upload automation, PDF/Canva/photo extraction, or no-form generation."
            )


def load_pin_variations(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    pins = data.get("pins")
    if not isinstance(pins, list) or not pins:
        raise ValueError(f"{path} must contain a non-empty 'pins' list.")

    cleaned_pins: list[dict] = []
    for index, pin in enumerate(pins, start=1):
        if not isinstance(pin, dict):
            raise ValueError(f"Pin #{index} must be an object.")

        missing = [field for field in REQUIRED_PIN_FIELDS if field not in pin]
        if missing:
            raise ValueError(f"Pin #{index} is missing required fields: {', '.join(missing)}")

        if not isinstance(pin["badges"], list) or not pin["badges"]:
            raise ValueError(f"Pin #{index} must include a non-empty badges list.")

        validate_safe_copy(pin, index)
        pin = dict(pin)
        pin["template"] = Path(str(pin["template"])).name
        pin["output_name"] = safe_output_name(str(pin["output_name"]), f"pin-{index:02d}.png")
        cleaned_pins.append(pin)

    return cleaned_pins


def apply_variation(page, pin: dict) -> None:
    page.evaluate(
        """
        (pin) => {
            const setText = (selector, value) => {
                const el = document.querySelector(selector);
                if (el && value !== undefined && value !== null) {
                    el.textContent = value;
                }
            };

            setText('.v3-headline', pin.headline);
            setText('.v3-sub', pin.subheadline);

            const main = document.querySelector('main.pin');
            const cta = document.querySelector('.v3-cta');

            if (main && pin.supporting_line) {
                let supportingLine = document.querySelector('.v3-supporting-line');
                if (!supportingLine) {
                    supportingLine = document.createElement('div');
                    supportingLine.className = 'v3-supporting-line';
                    supportingLine.style.position = 'absolute';
                    supportingLine.style.left = '72px';
                    supportingLine.style.right = '72px';
                    supportingLine.style.bottom = '118px';
                    supportingLine.style.fontFamily = 'Inter, Arial, sans-serif';
                    supportingLine.style.fontSize = '24px';
                    supportingLine.style.lineHeight = '1.25';
                    supportingLine.style.letterSpacing = '0.01em';
                    supportingLine.style.opacity = '0.78';
                    supportingLine.style.textAlign = 'center';
                    supportingLine.style.zIndex = '20';

                    if (cta && cta.parentNode) {
                        cta.parentNode.insertBefore(supportingLine, cta);
                    } else {
                        main.appendChild(supportingLine);
                    }
                }
                supportingLine.textContent = pin.supporting_line;
            }

            const badgesWrap = document.querySelector('.v3-badges');
            if (badgesWrap && Array.isArray(pin.badges)) {
                const icons = ['◎', '▣', '▤'];
                badgesWrap.innerHTML = '';
                pin.badges.slice(0, 3).forEach((text, index) => {
                    const badge = document.createElement('div');
                    badge.className = 'v3-badge';

                    const icon = document.createElement('i');
                    icon.textContent = icons[index] || '•';
                    badge.appendChild(icon);
                    badge.appendChild(document.createTextNode(String(text)));
                    badgesWrap.appendChild(badge);
                });
            }

            if (cta) {
                if (pin.link) {
                    cta.href = pin.link;
                }
                cta.innerHTML = '';
                cta.appendChild(document.createTextNode(pin.cta || 'Get your guide'));
                cta.appendChild(document.createTextNode(' '));

                const arrow = document.createElement('span');
                arrow.textContent = '→';
                cta.appendChild(arrow);
            }

            if (pin.output_name) {
                document.title = pin.output_name.replace(/\.png$/i, '');
            }
        }
        """,
        pin,
    )


def render_pin(page, url: str, output_path: Path, wait_ms: int, pin: dict | None = None) -> dict:
    page.goto(url, wait_until="networkidle", timeout=120_000)
    page.wait_for_timeout(wait_ms)

    if pin:
        apply_variation(page, pin)
        page.wait_for_timeout(300)

    pin_element = page.locator("main.pin").first
    pin_element.wait_for(state="visible", timeout=30_000)

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(300)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pin_element.screenshot(path=str(output_path))

    result = {
        "title": page.title(),
        "url": url,
        "output": str(output_path),
    }

    if pin:
        result.update(
            {
                "template": pin.get("template"),
                "headline": pin.get("headline"),
                "cta": pin.get("cta"),
                "link": pin.get("link"),
            }
        )

    return result


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
        help="List of template filenames to render when no variations file is found.",
    )
    parser.add_argument(
        "--variations",
        default=DEFAULT_VARIATIONS_PATH,
        help="Path to pin_variations.json. When present, this generates one PNG per variation.",
    )
    args = parser.parse_args()

    base_url = args.base_url
    if not base_url.endswith("/"):
        base_url += "/"

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = []

    variations_path = Path(args.variations) if args.variations else None
    variations: list[dict] = []
    if variations_path and variations_path.exists():
        variations = load_pin_variations(variations_path)
        print(f"Loaded {len(variations)} pin variations from {variations_path}")
    elif args.variations != DEFAULT_VARIATIONS_PATH:
        print(f"ERROR: variations file not found: {variations_path}", file=sys.stderr)
        return 1
    else:
        print("No pin variations file found. Rendering default templates only.")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": 1000, "height": 1500},
                device_scale_factor=2,
            )

            if variations:
                for index, pin in enumerate(variations, start=1):
                    template = pin["template"]
                    filename = safe_output_name(pin["output_name"], f"pin-{index:02d}-{slugify(Path(template).stem)}.png")
                    target_path = output_dir / filename
                    url = urljoin(base_url, template)

                    try:
                        result = render_pin(page, url, target_path, args.wait_ms, pin=pin)
                    except PlaywrightTimeoutError as exc:
                        print(f"ERROR rendering {url}: {exc}", file=sys.stderr)
                        continue

                    manifest.append(result)
                    print(f"Rendered variation {index:02d}: {template} -> {target_path}")
            else:
                for index, template in enumerate(args.templates, start=1):
                    filename = f"pin-{index:02d}-{slugify(Path(template).stem)}.png"
                    target_path = output_dir / filename
                    url = urljoin(base_url, Path(template).name)

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

    expected_count = len(variations) if variations else len(args.templates)
    if len(manifest) != expected_count:
        print(f"ERROR: rendered {len(manifest)} pins, expected {expected_count}.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
