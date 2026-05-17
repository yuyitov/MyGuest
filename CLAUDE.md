# MyGuest — Contexto para Claude Code

## Qué es este proyecto
Plataforma de guías digitales para propiedades de Airbnb. URL: **myguestguide.com**
- Guías mobile-first para huéspedes (EN / ES / FR)
- PDF imprimible incluido
- 4 demos reales desplegados

---

## Estrategia de marketing Pinterest — DECISIÓN CLAVE (mayo 2026)

### Para PUBLICIDAD (Pinterest pins):
- **ChatGPT genera las imágenes directamente** — no se usa HTML/CSS
- El usuario tiene 8 imágenes referencia en: `C:\Users\veron\Downloads\ChatGPT Image 10 may 2026, 10_24_03 p.m..png`
- No se necesitan datos reales en las imágenes de publicidad
- **Pendiente**: crear 8 prompts reutilizables de ChatGPT (uno por diseño) para flujo semanal

### Para el PRODUCTO / DEMOS:
- Se sigue usando el sistema HTML/CSS + Playwright para renderizar guías reales
- Los 4 demos reales tienen screenshots capturados en `/assets/screenshots/`

---

## Estado actual del sistema HTML (pinterest-v2)

### Último commit con 8 QA samples: `2de61d3`
### Templates modificados DESPUÉS del commit (sin commitear aún):
- `template-01-before-after.html` — tiene cambios de layout importantes (ver abajo)

### Cambios en template-01 (pendientes de commit):
- Headline movido a **TOP-LEFT** (`top:90px; right:500px`) — ya no está en el bottom
- BEFORE/AFTER zone movida al **MEDIO** (`top:460px`)
- Fondo: gradiente CSS tipo playa (cielo → teal → arena), sin foto de fondo (las hero.png son screenshots de la app, no fotos reales)
- Blur + scale en `::before` removido (causaba artefactos)
- Phone baja a `top:230px`
- Strip labels en mixed case ("Mobile guide" no "MOBILE GUIDE")
- AFTER label flota junto al phone (`left:508px; top:232px`)

---

## Estructura de archivos clave

```
marketing/
  instagram/                        ← Sistema de posts para Instagram (1080×1080px)
    templates/                      ← 9 plantillas HTML
    scripts/
      export-posts.js               ← Renderiza posts con Puppeteer
      generate-mockups.js           ← Genera mockups de celular (npm run mockups)
    assets/mockups/phone/           ← PNGs pre-generados del celular

  pinterest/                        ← Sistema de pins para Pinterest
    templates/                      ← 8 plantillas HTML (1000×1500px)
      template-01-before-after.html ← MODIFICADO, pendiente commit
    styles/pinterest-v2.css         ← CSS compartido (Inter 800, 4 temas, phone, strip)
    assets/screenshots/             ← Screenshots de los 4 demos reales
      ocean-drive-retreat/          ← full-demo.png, hero.png, etc.
      the-soho-loft/
      casa-selva-tulum/
      le-marais-flat/
    data/
      pinterest_campaign_v2.json    ← 32 pins definidos
      pinterest_demo_inventory.json
      pinterest_keywords.json
    scripts/
      render_qa_sample.py           ← Renderiza 8 QA samples (aprobación visual)
      render_pinterest_v2.py        ← Renderiza 32 pins finales
      validate_pinterest_copy.py    ← Valida copy antes de renderizar
      capture_pinterest_assets.py   ← Captura screenshots de demos
      build_pinterest_metadata.py   ← Genera CSVs de metadata
    output/                         ← PNGs generados y metadata
      qa-sample/                    ← 8 PNGs de muestra (última versión: 2de61d3)
      pins/                         ← 32 PNGs finales
      metadata/
    output-weekly/                  ← Pins semanales generados con ChatGPT
    docs/                           ← Guías operativas
    v1/                             ← Templates v1 (obsoletos, referencia)
    pins/                           ← PNGs ya publicados en Pinterest
    requirements-render-pinterest.txt
    requirements-render-pinterest-v2.txt

  assets/                           ← Materiales de marketing general
    MyGuest_Mensajes_de_Venta.docx
    MyGuest_Sales_OnePager.pdf
```

---

## CSS — Estructura del sistema (pinterest-v2.css)

### 4 temas: `style-coastal` | `style-minimalist` | `style-sunset` | `style-classic`
Cada tema define variables CSS: `--bg-grad`, `--bg-img`, `--bg-overlay`, `--c-text`, `--c-mid`, `--c-rule`, `--c-strip`, `--c-strip-text`, `--c-before-bg`, `--c-before-border`, `--c-arrow-bg`

### Layout fijo (compartido):
- `main.pin`: 1000×1500px, `overflow:hidden`, fondo = `::before` (foto) + `::after` (overlay)
- `.v2-brand`: top-center, `+ MyGuest`
- `.v2-phone`: `right:28px; top:108px; width:420px; height:860px` (override por template si necesario)
- `.v2-copy`: `left:40px; right:40px; top:1008px` (bottom-left — **template-01 lo overridea a top:90px**)
- `.v2-strip`: `bottom:0; height:192px` dark strip con 3 iconos

### PROBLEMA CONOCIDO con fondos:
Las imágenes `hero.png` son screenshots de la app MyGuest (muestran UI con texto), NO fotos reales de propiedades. Cuando se usan como `background-image` CSS, el texto de la app se filtra a través del overlay aunque esté al 72% de opacidad. **Solución aplicada en template-01**: gradiente CSS puro sin foto de fondo.

---

## Demos reales (4 propiedades)

| Slug | Estilo | Nombre |
|------|--------|--------|
| `ocean-drive-retreat` | Coastal | Ocean Drive Retreat |
| `the-soho-loft` | Minimalist | The SoHo Loft |
| `casa-selva-tulum` | Sunset | Casa Selva Tulum |
| `le-marais-flat` | Classic | Le Marais Flat |

---

## Cómo renderizar QA samples localmente

```bash
# 1. Servidor (raíz en marketing/pinterest/)
python -m http.server 8020 --directory marketing/pinterest

# 2. Render (en otra terminal)
python marketing/pinterest/scripts/render_qa_sample.py --base-url http://localhost:8020/templates/

# Output: marketing/pinterest/output/qa-sample/qa-01-before-after.png ... qa-08-style-showcase.png
```

El script inyecta el screenshot real via JS (`img.src = '/assets/screenshots/{slug}/full-demo.png'`).

---

## Pendientes al retomar

1. **Commitear template-01** con los cambios de layout (headline top, BEFORE en medio, gradiente de playa)
2. **Crear 8 prompts de ChatGPT** para generación semanal de imágenes publicitarias
3. **Workflow semanal**: los prompts generan variaciones → descargar → subir a Pinterest
4. **NO renderizar los 32 pins finales** hasta aprobación visual de los 8 QA samples
5. Si se continúa con HTML templates: revisar templates 02-08 con el usuario uno por uno

---

## Reglas de copy (NUNCA escribir en ningún pin)
- No mencionar AI extrayendo documentos automáticamente
- No decir "en minutos", "sin trabajo extra", "importación instantánea"
- No usar yuyitov.github.io como URL
- Todos los links deben ir a **myguestguide.com**

---

## Repo GitHub
`https://github.com/yuyitov/MyGuest` — branch: `main`
