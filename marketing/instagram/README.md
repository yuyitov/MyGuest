# MyGuest — Instagram Post System

A design-driven system for creating, previewing, and exporting Instagram posts (1080×1080px) for MyGuest.

---

## How it works

Each post is defined in `posts.json`. Nine HTML templates render the visual. You preview in the browser, then export to PNG with Puppeteer.

---

## 1. Where to edit post text

Open `posts.json` in any text editor.

Each post has:
- `title` — the main headline shown on the image
- `subtitle` — supporting text (not all templates use this)
- `body` — a longer description paragraph (some templates)
- `cta` — call-to-action button text
- `caption` — the Instagram caption you'll paste into Meta Business Suite
- `hashtags` — hashtags to add at the end of the caption
- `status` — `"ready"` to export, `"draft"` to skip (unless using `--draft`), `"skip"` to always skip
- `publish_date` — planned publish date (for your own reference)

**To change what a post says:** edit the fields in posts.json. The templates read these automatically.

---

## 2. Where the assets live

Images are already placed in the project — you don't need to move anything:

| Asset | Path |
|-------|------|
| Logo | `public/landing/logo_principal-Photoroom.png` |
| Coastal mockup | `public/landing/Mockups/Coastal_Style_Beach_Cel_Mockup.png` |
| Minimalist mockup | `public/landing/Mockups/Minnimalist_Beach_Cel_Mockup.png` |
| Sunset mockup | `public/landing/Mockups/Sunset_Style_Beach_Cel_Mockup.png` |
| Classic mockup | `public/landing/Mockups/Classic_mock.png` |

Templates reference these with relative paths — do not move them.

---

## 3. How to install

From the project root (`MyGuest/`):

```bash
npm install
```

This installs Puppeteer (used for PNG export). Only needed once.

---

## 4. How to preview

```bash
npm run preview
```

Then open your browser at: **http://localhost:3100/preview/**

You'll see a grid of all posts. Click any card to open the full 1080×1080 template in a new tab.

**Filters in the sidebar:**
- Filter by status (ready / draft)
- Filter by template type

> The preview must be served — it won't work if you just open the HTML file directly, because it fetches posts.json via HTTP.

---

## 5. How to export PNGs

Export all **ready** posts:
```bash
npm run export
```

Export **ready + draft** posts:
```bash
npm run export:draft
```

Puppeteer opens each template in a headless browser, renders it at 2x resolution, and captures a 1080×1080px screenshot.

---

## 6. Where the PNGs land

```
marketing/social-post-system/exports/
  01-post-001.png
  02-post-002.png
  ...
```

Files are named with a sequential number + the post ID. The `exports/` folder is gitignored (only `.gitkeep` is tracked).

---

## 7. How to schedule on Meta Business Suite

1. Go to [business.facebook.com](https://business.facebook.com) → **Content** → **Posts & Reels**
2. Click **Create post** → select your Instagram account
3. Upload the exported PNG from `exports/`
4. Paste the `caption` from posts.json
5. Add the `hashtags` at the end of the caption
6. Click **Schedule** → set the `publish_date` from posts.json
7. Confirm

Repeat for each post. Aim for 1–2 posts per day for best reach.

---

## Template reference

| # | Template | Best for |
|---|----------|----------|
| 01 | Brand Intro | First impressions, pinned post |
| 02 | Core Promise | Brand statement, big quote |
| 03 | How It Works | Process explanation, 4-step grid |
| 04 | Host Problem | Relatable pain points, high engagement |
| 05 | MyGuest Solution | Solution statement on deep teal |
| 06 | Before / After | Comparison, high saves |
| 07 | What's Included | Feature list, informational |
| 08 | Template Showcase | Visual style demos |
| 09 | CTA / Price | Sales posts, launch price |

---

## Adding new posts

1. Add a new object to `posts.json` with a unique `id`
2. Set `status: "draft"` to start
3. Preview with `npm run preview`
4. When happy, change to `status: "ready"` and export
