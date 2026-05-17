# MyGuest

Digital guest guides for Airbnb properties — mobile-first, trilingual, with a printable PDF included.

Live at **[myguestguide.com](https://myguestguide.com)**

---

## What it does

Hosts fill out a form and receive a branded digital guide for their property with:
- Mobile-optimized web guide (EN / ES / FR)
- Printable PDF version
- 4 visual styles: Coastal, Minimalist, Sunset, Classic

---

## Repository structure

```
books/                          Guest book generation engine
  scripts/
    generate_villa.py           Generates the web guide (HTML) for a property
    build_print_pdf.py          Generates the printable PDF version
    _generate_demo_*.py         Demo property generators
  templates/
    master.html                 Web guide template
    print_letter.html           Print PDF template
  preview_print_redesign.html   Print redesign prototype

marketing/
  instagram/                   Instagram post system (1080×1080px)
    templates/                 9 HTML post templates
    scripts/
      export-posts.js          Renders posts to PNG via Puppeteer
      generate-mockups.js      Generates phone mockup PNGs (npm run mockups)
    assets/                    Logos, mascot, phone mockup PNGs
    posts.json                 Post definitions (copy + style)
    preview/                   Browser preview grid

  pinterest/                   Pinterest pin system (1000×1500px)
    templates/                 8 HTML pin templates
    styles/pinterest-v2.css    Shared CSS (4 themes)
    assets/screenshots/        Real demo screenshots (4 properties)
    data/                      Campaign JSON, keywords, demo inventory
    scripts/
      render_pinterest_v2.py   Renders 32 pins via Playwright
      render_qa_sample.py      Renders 8 QA samples for visual review
      validate_pinterest_copy.py  Checks for prohibited copy before render
      capture_pinterest_assets.py  Captures live demo screenshots
      build_pinterest_metadata.py  Generates upload/tracking CSVs
    output/                    Generated PNGs and metadata CSVs
    output-weekly/             Weekly pins generated via ChatGPT
    pins/                      Published pins + tracking spreadsheet
    docs/                      Operating guides
    v1/                        Legacy v1 templates (reference only)

  assets/                      General sales materials (PDF, DOCX)

public/                        GitHub Pages web root (myguestguide.com)
  index.html                   Landing page
  villas/                      4 live demo guides
    ocean-drive-retreat/
    the-soho-loft/
    casa-selva-tulum/
    le-marais-flat/
  assets/covers/               Cover images used in guides
  landing/                     Landing page assets (logos, mockups, mascot)

worker/
  worker.js                    Cloudflare Worker (Tally → KV → GitHub dispatch)
```

---

## Demo properties

| Property | Style |
|----------|-------|
| Ocean Drive Retreat | Coastal |
| The SoHo Loft | Minimalist |
| Casa Selva Tulum | Sunset |
| Le Marais Flat | Classic |

---

## Local development

**Preview Instagram posts:**
```bash
npm run preview        # serves on http://localhost:3100
npm run export         # renders all posts to PNG
npm run mockups        # regenerates phone mockup PNGs
```

**Render Pinterest QA samples:**
```bash
python -m http.server 8020 --directory marketing/pinterest
python marketing/pinterest/scripts/render_qa_sample.py --base-url http://localhost:8020/templates/
```

**Generate a guest book:**
```bash
python books/scripts/generate_villa.py <property-slug>
```

---

## GitHub Actions

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `generator.yml` | Manual | Generate a client guest book |
| `render-pdf.yml` | Manual | Build printable PDF |
| `render-pinterest-v2.yml` | Manual | Render 32 Pinterest pins |
| `render-pinterest-pins.yml` | Push to `marketing/pinterest/v1/` | Render v1 pins |
| `pages.yml` | Push to `main` | Deploy to GitHub Pages |
