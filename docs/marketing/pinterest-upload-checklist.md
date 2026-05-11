# Pinterest v2 — Upload Checklist

Step-by-step guide for downloading, reviewing, and publishing the 32 Pinterest pins.

---

## Step 1 — Download the artifact

1. Go to the GitHub repository → **Actions** tab.
2. Find the run **"Render Pinterest v2 Pins"** (triggered manually via **Run workflow**).
3. When the run completes successfully (green checkmark), scroll to **Artifacts**.
4. Download **`pinterest-v2-package`** (ZIP file).
5. Unzip it locally. You'll have:
   ```
   pins/          ← 32 PNG files (1000×1500px)
   metadata/
     manifest.json
     pinterest_upload_sheet.csv
     pinterest_tracking_sheet.csv
     README.md
   ```

---

## Step 2 — Review the 32 PNGs

Before uploading, verify:

- [ ] Total PNG count is exactly 32.
- [ ] Each PNG is named correctly: `pin-001-coastal-before-after.png`, etc.
- [ ] No PNG is blank or appears corrupted (open a few to check).
- [ ] Spot-check at least one pin per style (Coastal, Minimalist, Sunset, Classic).
- [ ] Spot-check at least one pin per template (before-after, demo-visual, printable-pdf, trilingual, stop-repeating, existing-materials, private-details, style-showcase).
- [ ] Text is legible at Pinterest preview size.
- [ ] No prohibited copy visible on any pin ("in minutes", "AI", "automatic", etc.).
- [ ] No private/sensitive property data visible on any pin.

---

## Step 3 — Import CSVs to Google Sheets

1. Open [Google Sheets](https://sheets.google.com) and create a new spreadsheet called **"MyGuest Pinterest v2"**.
2. Click **File → Import → Upload** → select `pinterest_upload_sheet.csv`.
3. Choose **Insert new sheet** and name it **"Upload"**.
4. Repeat for `pinterest_tracking_sheet.csv` — name that sheet **"Tracking"**.
5. Freeze the header row (Row 1) on each sheet.

---

## Step 4 — Upload the first 8 pins (first batch)

Upload pins 001–008 (one per template, Coastal style first):

For each pin:
1. Go to [Pinterest](https://www.pinterest.com) → **Create → Create Pin**.
2. Upload the PNG file (`pin-001-coastal-before-after.png`, etc.).
3. Copy-paste from the **Upload sheet** CSV:
   - **Title** → `pin_title` column
   - **Description** → `pin_description` column
   - **Destination link** → `destination_url` column
   - **Alt text** → click "Accessibility" → paste `alt_text` column
4. Select the board from `board_name` column.
5. Schedule or publish immediately.
6. After publishing, copy the live Pinterest pin URL.

---

## Step 5 — Record Pinterest URLs in tracking sheet

After each pin is live:
1. Open the **Tracking** sheet in Google Sheets.
2. Find the pin's row by `pin_id`.
3. Fill in:
   - `pinterest_url` — full URL of the published pin
   - `publish_date` — today's date (YYYY-MM-DD)
   - `status` → change from `pending` to `live`

---

## Step 6 — Publish remaining pins in batches

Recommended schedule:
- **Day 1:** Pins 001–008 (8 pins, one per template, Coastal)
- **Day 3:** Pins 009–016 (8 pins, Minimalist style)
- **Day 5:** Pins 017–024 (8 pins, Sunset style)
- **Day 7:** Pins 025–032 (8 pins, Classic style)

Or: publish 4 per day spread over 8 days for more distribution.

---

## Step 7 — Monitor for 7–10 days

Wait at least 7 days before evaluating results. Pinterest takes time to distribute.

Check these metrics per pin (from Pinterest Analytics):

| Metric | Where to find |
|---|---|
| Impressions | Pinterest Analytics → Pins |
| Saves | Pinterest Analytics → Pins |
| Outbound clicks | Pinterest Analytics → Pins |
| Landing visits | Google Analytics 4 → Acquisition → UTM source=pinterest |
| CTA clicks | GA4 → Events → filter by UTM content |
| Leads (Tally starts) | Tally dashboard or GA4 event |
| Purchases | Stripe dashboard → filter by date |

Record all metrics in the **Tracking** sheet.

---

## Step 8 — Declare a winner

After 7–10 days, declare a pin a **winner** if it shows:

| Signal | Threshold (rough guide) |
|---|---|
| Outbound click rate | > 1% (outbound clicks / impressions) |
| Saves | High relative to other pins |
| Lead or purchase confirmed | Any purchase = winner |
| Visual clarity | Clear readability at thumbnail size |

Winner criteria is intentionally flexible for the first launch. Adjust thresholds after the first 32 pins are published and you have baseline data.

---

## Automation — Future options

The following automations are possible **after** you have:
- A Pinterest Business account
- Pinterest API access token

**Do not block MVP publishing on these.** Manual upload is the right move now.

| Automation | Requirement |
|---|---|
| Auto-upload pins via Pinterest API | Pinterest Developer App + API token |
| Scheduled publishing (e.g., 2 pins/day) | Pinterest API with scheduling endpoint |
| Auto-pull analytics into tracking sheet | Pinterest API analytics + Google Sheets script |

When ready, add Pinterest API credentials to GitHub Secrets and update `render-pinterest-v2.yml`.

---

*MyGuest Pinterest v2 — Checklist | myguestguide.com*
