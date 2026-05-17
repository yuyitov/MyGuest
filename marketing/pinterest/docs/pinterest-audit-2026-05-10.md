# Pinterest System Audit — 2026-05-10

Audit of the existing Pinterest marketing system before migration to v2.

---

## 1. Archivos existentes

### public/marketing/pinterest/
| Archivo | Estado |
|---|---|
| `index.html` | Legacy — galería de templates v1 |
| `pin_variations.json` | **OBSOLETO** — todos los links apuntan a `yuyitov.github.io` |
| `premium-v3.css` | Reutilizable — estilos base del sistema de pins v3 |
| `style.css` | Reutilizable — complemento de estilos |
| `template-01-stop-questions.html` | Legacy — copy tiene "Ready in minutes" (prohibido), links internos rotos |
| `template-02-pdf.html` | Legacy — reutilizable visualmente, copy OK |
| `template-03-trilingual.html` | Legacy — reutilizable visualmente |
| `template-04-minutes.html` | **OBSOLETO** — nombre y contenido implican "in minutes" (prohibido) |
| `template-05-one-link.html` | Legacy — reutilizable visualmente, copy OK |

### scripts/marketing/
| Archivo | Estado |
|---|---|
| `render_pinterest_pins.py` | Reutilizable — arquitectura sólida. Renombrar a v2 con nuevo JSON |

### .github/workflows/
| Archivo | Estado |
|---|---|
| `render-pinterest-pins.yml` | Legacy — trigger en push a main path viejo. No tocar (mantener para v1) |

### Raíz del proyecto
| Archivo | Estado |
|---|---|
| `requirements-render-pinterest.txt` | Reutilizable — `playwright==1.53.0` |

---

## 2. Qué sirve todavía

- `premium-v3.css` y `style.css`: sistema de diseño base, tipografía, badges, CTA, layout de pin 1000×1500. Reutilizar como inspiración en `pinterest-v2.css`.
- `render_pinterest_pins.py`: arquitectura de renderizado con Playwright. El script v2 sigue el mismo patrón.
- `template-02-pdf.html`, `template-03-trilingual.html`, `template-05-one-link.html`: copy base reutilizable con modificaciones.

---

## 3. Qué queda obsoleto

| Elemento | Razón |
|---|---|
| `pin_variations.json` | Todos los links apuntan a `yuyitov.github.io/MyGuest/` — destino prohibido |
| `template-04-minutes.html` | Nombre y copia implican "in minutes" — frase prohibida |
| `template-01-stop-questions.html` | Copy contiene "Ready in minutes" — frase prohibida |
| `render-pinterest-pins.yml` trigger `push: paths` | Dispara en push a main, acoplado a paths v1 |
| Todos los `link:` en `pin_variations.json` | Apuntan a `yuyitov.github.io` |

---

## 4. Links viejos que deben reemplazarse

| Link viejo | Reemplazar por |
|---|---|
| `https://yuyitov.github.io/MyGuest/?utm_*` | `https://myguestguide.com/?utm_source=pinterest&utm_medium=organic&utm_campaign=pinterest_v2_launch&utm_content=...` |
| `../../index.html` (relativo interno) | `https://myguestguide.com/villas/{slug}/?utm_*` |
| Slug `ocean-drive-retreat-miami-beach-7xnzlba` | `ocean-drive-retreat` |
| Cualquier link de `yuyitov.github.io` | `myguestguide.com` |

---

## 5. Copy viejo que debe eliminarse

| Frase | Ubicación | Razón |
|---|---|---|
| "Ready in minutes." | template-01-stop-questions.html (subheadline) | Prohibido — promete velocidad irreal |
| `template-04-minutes.html` | Nombre de archivo | El nombre implica el claim "in minutes" |
| Cualquier pin con `link: yuyitov.github.io` | pin_variations.json | Destino prohibido |
| "Airbnb hosts" badge | Varios pins v1 | No es error de copy pero puede mejorarse |

---

## 6. Estructura nueva recomendada

```
public/marketing/pinterest-v2/        ← Sistema v2 nuevo
  index.html                          ← Índice de templates
  styles/pinterest-v2.css             ← CSS unificado con variables por estilo
  templates/                          ← 8 templates verticales 1000×1500
    template-01-before-after.html
    template-02-demo-visual.html
    template-03-printable-pdf.html
    template-04-trilingual.html
    template-05-stop-repeating.html
    template-06-existing-materials.html
    template-07-private-details.html
    template-08-style-showcase.html
  assets/
    screenshots/{slug}/               ← Capturas reales de las demos
    generated/                        ← Assets generados por scripts
    exports/                          ← Exportaciones finales

data/marketing/                       ← Datos estructurados
  pinterest_demo_inventory.json       ← 4 demos reales
  pinterest_campaign_v2.json          ← 32 pins
  pinterest_keywords.json             ← SEO keywords

scripts/marketing/                    ← Scripts de automatización
  capture_pinterest_assets.py         ← Captura screenshots de demos
  render_pinterest_v2.py              ← Renderiza 32 PNGs
  validate_pinterest_copy.py          ← Valida copy prohibido
  build_pinterest_metadata.py         ← Genera CSVs de publicación

output/pinterest-v2/                  ← Outputs generados (no en repo)
  pins/                               ← 32 PNGs
  metadata/                           ← manifest.json, CSVs

docs/marketing/                       ← Documentación operativa
  pinterest-audit-2026-05-10.md       ← Este archivo
  pinterest-v2-operating-guide.md     ← Guía operativa
  pinterest-upload-checklist.md       ← Checklist de publicación

.github/workflows/
  render-pinterest-v2.yml             ← Workflow v2 (solo workflow_dispatch)
```

Los archivos legacy en `public/marketing/pinterest/` se mantienen intactos y se marcan como legacy. No se borran.

---

## 7. Riesgos detectados

| Riesgo | Severidad | Mitigación |
|---|---|---|
| Links `yuyitov.github.io` en pins publicados | CRÍTICO | `validate_pinterest_copy.py` falla si detecta este dominio |
| Copy "in minutes" o promesas de IA | CRÍTICO | `validate_pinterest_copy.py` falla si detecta frases prohibidas |
| `render-pinterest-pins.yml` dispara en push a main | MEDIO | No tocar — el nuevo workflow usa solo `workflow_dispatch` |
| Screenshots no capturadas antes de render | MEDIO | Script usa placeholder controlado + warning en log |
| PDF URLs como destino directo de Pinterest | BAJO | v2 envía siempre a demo, PDF se usa solo como asset visual |
| Datos privados en screenshots | BAJO | Las demos públicas no contienen datos privados reales |
| Template `template-04-minutes.html` publicado | BAJO | Archivo no accesible públicamente desde la landing comercial |

---

## 8. Acciones inmediatas tomadas (v2)

- Creado nuevo sistema completo en `public/marketing/pinterest-v2/`
- Creados 8 templates HTML con copy revisado
- Creado `pinterest_campaign_v2.json` con 32 pins (cero links prohibidos)
- Creado `validate_pinterest_copy.py` que falla en copy o links prohibidos
- Creado `render-pinterest-v2.yml` con solo `workflow_dispatch`
- Archivos legacy en `public/marketing/pinterest/` marcados como legacy, no eliminados

---

*Generado: 2026-05-10 | Sistema: MyGuest Pinterest v2*
