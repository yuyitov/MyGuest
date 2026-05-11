# Pinterest v2 — Operating Guide

Complete reference for running, maintaining, and expanding the MyGuest Pinterest v2 system.

---

## 1. System summary

The Pinterest v2 system generates 32 Pinterest pin images (PNG, 1000×1500px) from 8 templates × 4 styles/demos.

**Architecture:**
```
data/marketing/pinterest_campaign_v2.json   ← Source of truth for all 32 pins
    ↓
scripts/marketing/validate_pinterest_copy.py  ← Safety check (runs first)
    ↓
scripts/marketing/capture_pinterest_assets.py ← Screenshots from real demos
    ↓
public/marketing/pinterest-v2/templates/*.html ← 8 HTML templates (rendered by Playwright)
    ↓
scripts/marketing/render_pinterest_v2.py       ← Renders 32 PNGs
    ↓
scripts/marketing/build_pinterest_metadata.py  ← Generates upload/tracking CSVs
    ↓
output/pinterest-v2/pins/*.png                 ← 32 final PNGs
output/pinterest-v2/metadata/*.csv             ← Upload and tracking sheets
```

Triggered by: `.github/workflows/render-pinterest-v2.yml` (manual, `workflow_dispatch` only).

---

## 2. Where the templates are

```
public/marketing/pinterest-v2/templates/
  template-01-before-after.html      ← Scattered materials → clean guide
  template-02-demo-visual.html       ← Full screenshot of real demo
  template-03-printable-pdf.html     ← Phone + PDF side by side
  template-04-trilingual.html        ← EN / ES / FR language panels
  template-05-stop-repeating.html    ← Chat bubbles → one link solution
  template-06-existing-materials.html← PDF, Word, photos, or simple form
  template-07-private-details.html   ← Public guide + private guest link
  template-08-style-showcase.html    ← Large property demo showcase
```

CSS: `public/marketing/pinterest-v2/styles/pinterest-v2.css`

---

## 3. Where the screenshots are

Captured screenshots are stored in:
```
public/marketing/pinterest-v2/assets/screenshots/
  ocean-drive-retreat/
    hero.png
    guide-section.png
    full-demo.png
    print-preview.png
  the-soho-loft/
    hero.png
    guide-section.png
    full-demo.png
    print-preview.png
  casa-selva-tulum/
    ...
  le-marais-flat/
    ...
```

Screenshots are captured from the live URLs in `data/marketing/pinterest_demo_inventory.json`.

If a screenshot is missing, the render script uses a solid color placeholder and logs a warning. The PIN still renders.

---

## 4. How to add a new demo

1. **Add entry to inventory:**
   Edit `data/marketing/pinterest_demo_inventory.json` — add a new object following the existing structure. Include `style`, `property`, `slug`, `demo_url`, `pdf_url`, and color values.

2. **Check that the demo URL is live** at `myguestguide.com/villas/{slug}/`.

3. **Run screenshot capture:**
   ```
   python scripts/marketing/capture_pinterest_assets.py
   ```

4. **Add pins to campaign:**
   Edit `data/marketing/pinterest_campaign_v2.json` — add 8 new pin objects (one per template) for the new demo. Keep naming consistent: `pin-033-{style}-{template}`, etc.

5. **Run validation:**
   ```
   python scripts/marketing/validate_pinterest_copy.py
   ```

6. **Render and review:**
   Via GitHub Actions or locally with a static server.

---

## 5. How to add a new style

1. Add a CSS class to `pinterest-v2.css`:
   ```css
   body.style-newstyle { --c-bg: #...; --c-primary: #...; --c-accent: #...; --c-text: #...; --c-mid: #...; --c-surface: #...; --c-border: #...; }
   ```

2. Add the style to `STYLE_CLASS_MAP` in `render_pinterest_v2.py`:
   ```python
   STYLE_CLASS_MAP = { ..., "NewStyle": "style-newstyle" }
   ```

3. Add placeholder color to `PLACEHOLDER_COLOR_MAP` in `render_pinterest_v2.py`.

4. Add `VALID_STYLES` in `validate_pinterest_copy.py`:
   ```python
   VALID_STYLES = {"Coastal", "Minimalist", "Sunset", "Classic", "NewStyle"}
   ```

5. Add color values to the demo inventory for demos using this style.

6. Add 8 new pins (one per template) to `pinterest_campaign_v2.json` for the new style.

---

## 6. How to create a new batch of pins

1. **Add pins to** `data/marketing/pinterest_campaign_v2.json`.
   - Increment IDs: `pin-033`, `pin-034`, etc.
   - Follow the existing schema exactly.
   - Each pin needs all required fields (see `validate_pinterest_copy.py`).

2. **Run validation:**
   ```
   python scripts/marketing/validate_pinterest_copy.py
   ```
   Fix any errors before continuing.

3. **Update expected count** in `render_pinterest_v2.py`:
   ```python
   EXPECTED_PIN_COUNT = 40  # updated from 32
   ```

4. **Trigger the GitHub Actions workflow** (`render-pinterest-v2.yml` → Run workflow).

5. **Download artifact** `pinterest-v2-package`.

6. **Follow the upload checklist** in `pinterest-upload-checklist.md`.

---

## 7. How to validate copy

```bash
python scripts/marketing/validate_pinterest_copy.py
```

The script reads `data/marketing/pinterest_campaign_v2.json` and checks every text field for:
- Prohibited copy phrases (AI claims, "in minutes", "automatic extraction", etc.)
- Prohibited links (yuyitov.github.io, test/qa slugs, old slug)
- Missing required fields
- Invalid styles or templates
- Incorrect UTM parameters

Exit code 0 = clean. Exit code 1 = errors found. The GitHub Actions workflow fails if this script fails.

---

## 8. How to generate assets

### Screenshots only
```bash
python scripts/marketing/capture_pinterest_assets.py
```
Requires: `pip install playwright` + `playwright install chromium`

### PNGs only (with local server)
```bash
# Terminal 1
python -m http.server 8000 --directory public

# Terminal 2
python scripts/marketing/render_pinterest_v2.py \
  --base-url http://127.0.0.1:8000/marketing/pinterest-v2/templates/ \
  --output-dir output/pinterest-v2/pins
```

### Metadata CSVs only
```bash
python scripts/marketing/build_pinterest_metadata.py
```

### Full pipeline (via GitHub Actions — recommended)
Go to repo → Actions → "Render Pinterest v2 Pins" → Run workflow.

---

## 9. How to review artifacts

After a GitHub Actions run:
1. Go to Actions → the completed run → Artifacts.
2. Download `pinterest-v2-package`.
3. Verify: 32 PNGs + manifest.json + 2 CSVs + README.md.
4. Open 5–10 random PNGs to verify visual quality.
5. Open `pinterest_upload_sheet.csv` and spot-check:
   - No `yuyitov.github.io` in any URL
   - No prohibited copy in any title or description
   - All `destination_url` values contain `myguestguide.com`

---

## 10. How to avoid prohibited promises

**Never write in any pin, template, or CSV:**

| Prohibited | Why |
|---|---|
| "AI reads your document" | False — no AI extraction |
| "automatically generated from PDF/photos/Canva" | False — manual setup |
| "no manual input required" | False — we do manual review |
| "upload and AI does the rest" | False |
| "fully automated AI import" | False |
| "in minutes" | Misleading — setup takes time |
| "no extra work" | Misleading |
| "instant import" | False |
| "no form needed" | False — form is the default |
| "AI does the rest" | False |

**Safe copy patterns:**
- "Turn your Airbnb welcome book into a mobile guest guide."
- "You don't have to start from scratch."
- "Send your existing welcome book, PDF, Word file, Canva export, photos or screenshots — or fill out our simple form."
- "Early access includes manual setup."
- "Mobile guest guide + printable PDF."
- "English, Spanish and French versions."
- "Private guest link for sensitive stay details."
- "Early Access Launch Price: $29."

---

## 11. How to maintain UTMs

All destination URLs in `pinterest_campaign_v2.json` follow this pattern:
```
https://myguestguide.com/villas/{slug}/?utm_source=pinterest&utm_medium=organic&utm_campaign=pinterest_v2_launch&utm_content={unique_id}
```

Or for general landing:
```
https://myguestguide.com/?utm_source=pinterest&utm_medium=organic&utm_campaign=pinterest_v2_launch&utm_content={unique_id}
```

**Rules:**
- `utm_source` must always be `pinterest`
- `utm_medium` must always be `organic`
- `utm_campaign` must always be `pinterest_v2_launch` for this batch
- `utm_content` must be unique per pin — use the pattern `{template_short}-{style_short}`

When adding a new batch (e.g., retargeting), create a new campaign value:
```
utm_campaign=pinterest_v2_retargeting
```

---

## 12. What to do if a demo changes

If a demo URL changes (e.g., slug changes or design is updated):

1. Update `data/marketing/pinterest_demo_inventory.json` with the new URL.
2. Update all affected pins in `data/marketing/pinterest_campaign_v2.json` — search for the old URL.
3. Re-run screenshot capture for that demo.
4. Re-run validation.
5. Re-render the affected pins.
6. If pins are already live on Pinterest: edit the destination URL on each live pin.

---

## 13. What to do if a PDF doesn't open

If a PDF URL returns 404 or won't load:

1. Check `myguestguide.com/villas/{slug}/print.pdf` in a browser.
2. If 404: the PDF render may need to be re-run via the `render-pdf.yml` GitHub Actions workflow.
3. In the meantime, update `pdf_url` in the affected pins to point to the demo URL (`demo_url`) as a fallback.
4. PDF pins should always link to the demo page, not directly to the PDF — Pinterest doesn't open PDFs well.

---

## 14. What to do if a pin leads to 404

1. Check the `destination_url` in `pinterest_campaign_v2.json` for the affected pin.
2. Verify the URL works in a browser.
3. If the property page moved: update `destination_url` in the JSON and re-run the pipeline.
4. If a pin is already live on Pinterest: edit the pin's destination URL directly on Pinterest.
5. Update the URL in the **Tracking sheet** too.

---

## Quick reference commands

```bash
# Validate copy
python scripts/marketing/validate_pinterest_copy.py

# Capture screenshots
python scripts/marketing/capture_pinterest_assets.py

# Render (requires local server on port 8000)
python -m http.server 8000 --directory public &
python scripts/marketing/render_pinterest_v2.py --base-url http://127.0.0.1:8000/marketing/pinterest-v2/templates/

# Build CSVs only
python scripts/marketing/build_pinterest_metadata.py

# Check output
ls output/pinterest-v2/pins/*.png | wc -l   # Should be 32
```

---

*MyGuest Pinterest v2 — Operating Guide | myguestguide.com*
