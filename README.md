# MyGuest

Digital guest guides for Airbnb properties — mobile-first, trilingual, with a printable PDF included.

Live at **[myguestguide.com](https://myguestguide.com)**

---

## What it does

Hosts fill out a Tally form and receive a branded digital guide for their property:
- Mobile-optimized web guide (EN / ES / FR)
- Printable PDF via browser Print / Save as PDF
- 4 visual styles: Coastal, Minimalist, Sunset, Classic

The host shares **one secure link** with guests. The guide loads all stay details (WiFi, access codes, instructions) securely from Cloudflare Worker/KV using a private token in the link. Sensitive data is never stored in GitHub Pages or public files.

---

## Architecture

```
Tally → Cloudflare Worker → GitHub Actions → GitHub Pages
```

- **Tally**: Host fills property form, uploads existing welcome books if any.
- **Cloudflare Worker**: Validates submission, stores private data (WiFi, codes) in KV, dispatches to GitHub Actions.
- **GitHub Actions**: Generates the visual guide shell (no sensitive data), publishes to GitHub Pages.
- **GitHub Pages**: Hosts the static guide shell at myguestguide.com.
- **Guest access**: Guide fetches complete data from Worker/KV using secure token in the link.

---

## Repository structure

```
books/                          Guest book generation engine
  scripts/
    generate_villa.py           Generates the web guide (HTML) for a property
    build_print_pdf.py          Generates the printable PDF template
    postprocess_public_book.py  Post-generation visual QA
    _generate_demo_*.py         Demo property generators
  templates/
    master.html                 Web guide template
    print_letter.html           Print PDF template

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
| `generator.yml` | `repository_dispatch` (type: `new-villa`) | Generate a client guest book |
| `render-pdf.yml` | Manual (`workflow_dispatch`) | **Demo QA only** — renders print.html to PDF artifact for visual design review. Blocked on non-demo slugs. Not used for real client PDFs (see security model below). |
| `render-pinterest-v2.yml` | Manual (`workflow_dispatch`) | Render 32 Pinterest pins |
| `render-pinterest-pins.yml` | Push to `marketing/pinterest/v1/` | Render v1 pins (legacy) |
| `pages.yml` | Push to `main` | Deploy to GitHub Pages |
| `instagram-publish.yml` | Daily cron + manual | Auto-publish scheduled Instagram posts |

---

## Security model

- Sensitive data (WiFi, access codes, host phone) is stored only in Cloudflare KV, never in GitHub Pages.
- The guest guide shell on GitHub Pages contains no real credentials.
- A secure token in the guest link grants access to private data via the Worker.
- Without a valid token, the Worker returns no sensitive data.
- **Client PDFs**: The complete PDF (with WiFi, codes, full access details) is obtained by the host using `Print / Save as PDF` from the guide already loaded with a valid token. GitHub Actions only generates public-data-only print shells. Complete PDFs with real client data are never generated, committed, or stored in GitHub.
- `render-pdf.yml` is blocked on non-demo slugs and requires explicit demo confirmation. PDF output is uploaded as a workflow artifact, not committed to `public/`.
- All Tally input is treated as untrusted: HTML is escaped before rendering.
