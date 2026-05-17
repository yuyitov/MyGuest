"""Validate all copy and links in pinterest_campaign_v2.json for prohibited content."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CAMPAIGN_PATH = Path("data/marketing/pinterest_campaign_v2.json")

PROHIBITED_COPY_PATTERNS = [
    (r"\bai reads\b", "Prohibited claim: 'AI reads'"),
    (r"\bautomatic extraction\b", "Prohibited claim: 'automatic extraction'"),
    (r"\bautomatically generated\b", "Prohibited claim: 'automatically generated'"),
    (r"\bno manual input\b", "Prohibited claim: 'no manual input'"),
    (r"\bupload and ai\b", "Prohibited claim: 'upload and AI'"),
    (r"\bfully automated\b", "Prohibited claim: 'fully automated'"),
    (r"\bin minutes\b", "Prohibited claim: 'in minutes'"),
    (r"\bno extra work\b", "Prohibited claim: 'no extra work'"),
    (r"\bno form needed\b", "Prohibited claim: 'no form needed'"),
    (r"\binstant import\b", "Prohibited claim: 'instant import'"),
    (r"\bai does the rest\b", "Prohibited claim: 'AI does the rest'"),
    (r"\bai-powered\b", "Prohibited claim: 'AI-powered'"),
    (r"\bautomatic pdf\b", "Prohibited claim: 'automatic PDF'"),
    (r"\bautomatic import\b", "Prohibited claim: 'automatic import'"),
    (r"\bzero effort\b", "Prohibited claim: 'zero effort'"),
    (r"\bone-click\b", "Prohibited claim: 'one-click'"),
    (r"\bautomatic translation\b", "Prohibited claim: 'automatic translation'"),
    (r"\bai writes\b", "Prohibited claim: 'AI writes'"),
    (r"\bai import\b", "Prohibited claim: 'AI import'"),
]

PROHIBITED_LINK_PATTERNS = [
    (r"yuyitov\.github\.io", "Prohibited domain: yuyitov.github.io"),
    (r"ocean-drive-retreat-miami-beach-7xnzlba", "Prohibited old slug: ocean-drive-retreat-miami-beach-7xnzlba"),
    (r"[\?&]?(slug|page)=(test|qa|duplicate|paid-flow|final-test)", "Prohibited test/qa slug in URL"),
    (r"/test/|/qa/|/duplicate/|/paid-flow/|/final-test/", "Prohibited test/qa path in URL"),
]

REQUIRED_COPY_FIELDS = [
    "headline",
    "subheadline",
    "supporting_line",
    "cta",
    "pin_title",
    "pin_description",
    "alt_text",
]

REQUIRED_PIN_FIELDS = [
    "id",
    "style",
    "property",
    "slug",
    "template",
    "headline",
    "subheadline",
    "badges",
    "supporting_line",
    "cta",
    "destination_url",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "output_name",
    "board_name",
    "pin_title",
    "pin_description",
    "alt_text",
    "keywords",
    "demo_url",
    "pdf_url",
]

VALID_STYLES = {"Coastal", "Minimalist", "Sunset", "Classic"}
VALID_TEMPLATES = {
    "template-01-before-after",
    "template-02-demo-visual",
    "template-03-printable-pdf",
    "template-04-trilingual",
    "template-05-stop-repeating",
    "template-06-existing-materials",
    "template-07-private-details",
    "template-08-style-showcase",
}
VALID_UTM_SOURCE = "pinterest"
VALID_UTM_MEDIUM = "organic"
EXPECTED_DOMAIN = "myguestguide.com"


def collect_text(pin: dict) -> list[tuple[str, str]]:
    """Return (field_name, text) pairs for all copy fields."""
    parts = []
    for field in REQUIRED_COPY_FIELDS:
        val = pin.get(field, "")
        if val:
            parts.append((field, str(val)))
    badges = pin.get("badges", [])
    if isinstance(badges, list):
        parts.append(("badges", " ".join(str(b) for b in badges)))
    keywords = pin.get("keywords", [])
    if isinstance(keywords, list):
        parts.append(("keywords", " ".join(str(k) for k in keywords)))
    return parts


def collect_urls(pin: dict) -> list[tuple[str, str]]:
    """Return (field_name, url) pairs for all URL fields."""
    urls = []
    for field in ("destination_url", "demo_url", "pdf_url"):
        val = pin.get(field, "")
        if val:
            urls.append((field, str(val)))
    return urls


def validate_pin(pin: dict, index: int) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    pin_id = pin.get("id", f"pin-{index:03d}")

    missing = [f for f in REQUIRED_PIN_FIELDS if f not in pin]
    if missing:
        errors.append(f"[{pin_id}] Missing required fields: {', '.join(missing)}")

    style = pin.get("style", "")
    if style not in VALID_STYLES:
        errors.append(f"[{pin_id}] Invalid style '{style}'. Must be one of: {', '.join(sorted(VALID_STYLES))}")

    template = pin.get("template", "")
    if template not in VALID_TEMPLATES:
        errors.append(f"[{pin_id}] Invalid template '{template}'. Must be one of: {', '.join(sorted(VALID_TEMPLATES))}")

    if pin.get("utm_source") != VALID_UTM_SOURCE:
        errors.append(f"[{pin_id}] utm_source must be '{VALID_UTM_SOURCE}', got '{pin.get('utm_source')}'")

    if pin.get("utm_medium") != VALID_UTM_MEDIUM:
        errors.append(f"[{pin_id}] utm_medium must be '{VALID_UTM_MEDIUM}', got '{pin.get('utm_medium')}'")

    badges = pin.get("badges", [])
    if not isinstance(badges, list) or len(badges) == 0:
        errors.append(f"[{pin_id}] badges must be a non-empty list")

    for field, text in collect_text(pin):
        text_lower = text.lower()
        for pattern, label in PROHIBITED_COPY_PATTERNS:
            if re.search(pattern, text_lower, flags=re.IGNORECASE):
                errors.append(f"[{pin_id}] Prohibited copy in '{field}': {label}")

    for field, url in collect_urls(pin):
        for pattern, label in PROHIBITED_LINK_PATTERNS:
            if re.search(pattern, url, flags=re.IGNORECASE):
                errors.append(f"[{pin_id}] Prohibited URL in '{field}': {label} — URL: {url}")
        if EXPECTED_DOMAIN not in url:
            warnings.append(f"[{pin_id}] URL in '{field}' does not contain expected domain '{EXPECTED_DOMAIN}': {url}")

    utm_content = pin.get("utm_content", "")
    if not utm_content:
        warnings.append(f"[{pin_id}] utm_content is empty — tracking will be imprecise")

    output_name = pin.get("output_name", "")
    if not output_name.endswith(".png"):
        errors.append(f"[{pin_id}] output_name must end in .png, got '{output_name}'")

    return errors, warnings


def main() -> int:
    if not CAMPAIGN_PATH.exists():
        print(f"ERROR: campaign file not found: {CAMPAIGN_PATH}", file=sys.stderr)
        return 1

    data = json.loads(CAMPAIGN_PATH.read_text(encoding="utf-8"))
    pins = data.get("pins", [])

    if not isinstance(pins, list) or not pins:
        print("ERROR: 'pins' must be a non-empty list.", file=sys.stderr)
        return 1

    print(f"Validating {len(pins)} pins from {CAMPAIGN_PATH}\n")

    all_errors: list[str] = []
    all_warnings: list[str] = []
    destination_urls: list[str] = []

    for index, pin in enumerate(pins, start=1):
        errors, warnings = validate_pin(pin, index)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
        url = pin.get("destination_url", "")
        if url:
            destination_urls.append(url)

    styles_found = {p.get("style") for p in pins}
    templates_found = {p.get("template") for p in pins}

    missing_styles = VALID_STYLES - styles_found
    missing_templates = VALID_TEMPLATES - templates_found

    if missing_styles:
        all_warnings.append(f"Styles not represented in campaign: {', '.join(sorted(missing_styles))}")
    if missing_templates:
        all_warnings.append(f"Templates not represented in campaign: {', '.join(sorted(missing_templates))}")

    if len(pins) != 32:
        all_errors.append(f"Expected exactly 32 pins, found {len(pins)}")

    print("=== VALIDATION REPORT ===")
    print(f"Total pins reviewed:  {len(pins)}")
    print(f"Errors:               {len(all_errors)}")
    print(f"Warnings:             {len(all_warnings)}")
    print(f"Styles covered:       {', '.join(sorted(styles_found))}")
    print(f"Templates covered:    {len(templates_found)}/8")

    if all_errors:
        print(f"\n=== ERRORS ({len(all_errors)}) ===")
        for e in all_errors:
            print(f"  ERROR: {e}")

    if all_warnings:
        print(f"\n=== WARNINGS ({len(all_warnings)}) ===")
        for w in all_warnings:
            print(f"  WARNING: {w}")

    print(f"\n=== DESTINATION URLs ({len(destination_urls)}) ===")
    seen = set()
    for url in destination_urls:
        base = url.split("?")[0]
        if base not in seen:
            seen.add(base)
            print(f"  {base}")

    if all_errors:
        print(f"\nVALIDATION FAILED — {len(all_errors)} error(s) found. Fix before publishing.")
        return 1

    print(f"\nVALIDATION PASSED — {len(pins)} pins, {len(all_warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
