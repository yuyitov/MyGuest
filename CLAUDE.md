# MyGuest — Contexto para Claude Code

## Qué es este proyecto

MyGuest es un sistema para crear welcome books digitales para anfitriones de Airbnb y rentas vacacionales.

El cliente (dueño del Airbnb) recibe 2 entregables, ambos accesibles por link seguro con token:

1. **Guía digital móvil** → `/guest/<slug>?token=` — versión mobile completa con datos privados inyectados por el Worker.
2. **Guía imprimible** → `/print/<slug>?token=` — versión para imprimir con datos privados inyectados por el Worker. El host abre este link y usa `Print / Save as PDF` desde el navegador para obtener el PDF completo.

La guía y el PDF deben contener toda la información necesaria para la estancia:
bienvenida, dirección, Google Maps, check-in/check-out, instrucciones de acceso, códigos de entrada, lockbox/keypad, WiFi, reglas, amenidades, recomendaciones locales, contacto, emergencias, instrucciones de salida.

MyGuest no debe entregar libros incompletos, a menos que el cliente no proporcione la información.

---

## Principio principal del producto

MyGuest debe entregar una sola experiencia completa para el huésped.

El huésped NO debe tener que:
- abrir dos guías diferentes
- pedir otra contraseña
- iniciar sesión
- desbloquear secciones manualmente
- recibir WiFi o códigos por otro canal
- esperar información adicional después

La experiencia correcta:
- el host manda un solo link
- el huésped abre un solo link
- la guía muestra toda la información necesaria
- no hay login
- no hay contraseña adicional

La seguridad se resuelve internamente por arquitectura, no haciendo más difícil la experiencia del huésped.

---

## Arquitectura aprobada

```
Tally → Cloudflare Worker → GitHub Actions → GitHub Pages
```

Con datos sensibles fuera del sitio público y reconciliación con Tally API.

**No cambiar esta arquitectura sin validarlo.**

Repo correcto: `yuyitov/MyGuest` (no usar `yuyitov/myguest-app`, está desactualizado).

---

## Interpretación correcta de seguridad

Hay una sola guía digital completa. La guía SÍ muestra WiFi, códigos, acceso y datos completos. Pero esos datos NO deben quedar escritos dentro del HTML público, GitHub Pages, archivos públicos, JSON público, PDF público sin protección, logs o código fuente visible.

La guía visual carga la información completa de forma segura desde Cloudflare Worker/KV usando un token privado incluido en el link. El huésped no nota esta separación técnica.

**Resumen**: La guía debe MOSTRAR toda la información, pero no debe PUBLICARLA dentro del código público.

### Qué puede ir en GitHub Pages (shell público)
- estructura HTML base, CSS, layout, navegación, componentes visuales
- placeholders seguros, scripts de carga, diseño, assets públicos
- datos demo claramente ficticios

### Qué NO puede ir en GitHub Pages
- WiFi password real, códigos reales, door code, keypad code, lockbox code, PIN real
- teléfono privado real, instrucciones sensibles reales
- tokens privados reales en archivos estáticos
- PDF completo sensible como archivo público

### Lo que debe vivir en Cloudflare Worker + KV
- WiFi SSID, WiFi password, códigos, lockbox, keypad
- instrucciones completas de acceso, teléfono del host
- información completa que el huésped sí necesita ver

---

## Modelo técnico

### GitHub Pages
Shell visual / app estática. Contiene estructura, CSS, layout, placeholders, lógica de carga.

### Cloudflare Worker + KV
Capa segura. Recibe payload de Tally, valida firma, separa datos, guarda datos completos en KV, genera token de acceso, hace dispatch a GitHub Actions, responde a la guía solo con token válido. Usa `cache-control: no-store`. No imprime secretos en logs.

### GitHub Actions
Genera la guía móvil, actualiza HTML estático seguro, publica en GitHub Pages, corre validaciones de seguridad, bloquea builds si aparecen datos sensibles.

Workflows:
- `generator.yml` — genera el guest book (trigger: `repository_dispatch` tipo `new-villa`)
- `render-pdf.yml` — genera PDF como artefacto (NO como archivo público en `public/`)
- `pages.yml` — despliega a GitHub Pages

### Tally
Entrada de datos del host. Recolecta información general, acceso, WiFi, reglas, amenidades, recomendaciones, contacto, emergencias, imágenes/archivos.

---

## Fórmula del slug oficial

```
slug = slugify(property_name) + "-" + últimos 10 caracteres de submission_id
```

Ejemplo: `Casa Serena` + `01JSG4J8P2K9X7` → `casa-serena-4j8p2k9x7`

Reglas: minúsculas, sin acentos, espacios → guiones, sin símbolos, sin dobles guiones, máx 50-60 caracteres antes del sufijo.

**Nota de implementación**: El código usa `.slice(-10)` (10 caracteres), no 4. Esto es intencional para reducir la probabilidad de colisiones. Se recomienda mantener 10 caracteres.

---

## Link seguro sin contraseña

Ejemplo: `https://myguestguide.com/villas/casa-serena-k9x7/?token=xxx`

- Token: 32 bytes aleatorios, base64 URL-safe
- Validar token en Worker
- No guardar token real dentro de archivos estáticos
- No exponer token en logs
- Sin token o token inválido → no devolver datos sensibles
- `<meta name="referrer" content="no-referrer">`

Sin login ni contraseña. Si el huésped comparte el link, otra persona podría ver la guía. Esto es aceptable para MVP porque el objetivo es una experiencia simple. Lo importante es que la información no quede publicada en GitHub Pages.

---

## Flujo de adjuntos y extracción manual (MVP)

### Regla crítica

Si el cliente sube archivos (PDF, Word, Canva, fotos, capturas), el flujo **NO debe generar ni entregar automáticamente** los books hasta que Vero revise esos archivos y extraiga manualmente la información.

El sistema debe pausar con estado: `needs_manual_extraction`

### Cómo detectar adjuntos

El Worker detecta si el payload contiene:
- respuesta "Sí" en la pregunta de adjuntos del formulario
- campos `existing_book_file` o `existing_book_photos` no vacíos
- URLs de archivo en el payload

### Comportamiento correcto cuando hay adjuntos

1. Guardar la submission en KV
2. Guardar o referenciar los archivos de forma segura
3. Marcar estado como `needs_manual_extraction`
4. **NO disparar la generación final**
5. Guardar registro de intake con datos del cliente para revisión de Vero

### Comportamiento correcto cuando NO hay adjuntos

Proceder directamente con el dispatch a GitHub Actions.

### Formulario interno de revisión (futuro)

Nombre sugerido: `MyGuest — Manual Extraction Review`

Permite a Vero ingresar `submission_id`, completar información extraída, aprobar. Tally dispara otro webhook al Worker que combina datos originales + datos extraídos y lanza la generación.

---

## Estados internos del flujo

```
paid
form_sent
form_submitted
needs_manual_extraction
manual_extraction_in_progress
manual_extraction_complete
ready_to_generate
generating
generated
qa_pending
approved
delivered
```

---

## PDF / book imprimible

### Regla MVP aprobada

El PDF completo para clientes reales se obtiene con **Print / Save as PDF** desde la guía imprimible segura cargada con token en el navegador.

Flujo correcto:
1. El host abre el link de la guía imprimible: `/print/<slug>?token=<token>`.
2. El Worker valida el token, inyecta WiFi, códigos y acceso en el HTML de `print.html`.
3. El host usa `Print / Save as PDF` desde el navegador.
4. El PDF resultante incluye WiFi, códigos, acceso y toda la información completa.

El email de entrega incluye este link como "Open printable guide →".

Ventajas:
- No se guarda PDF sensible en GitHub.
- No se publica PDF sensible en `public/`.
- El PDF queda completo porque incluye los datos ya cargados.
- El host sigue compartiendo un solo link.

El diseño del PDF/imprimible debe verse correctamente en tamaño Carta (Letter) y A4, sin cortes, desbordamientos ni problemas de maquetación.

### Reglas de seguridad del PDF (no negociables)

- **No generar PDF completo sensible en GitHub Actions.** GitHub Actions solo tiene el payload público (sin WiFi, códigos, acceso real).
- **No guardar PDF completo sensible como artifact** en ningún workflow.
- **No commitear PDF completo sensible** al repo.
- **No publicar PDF completo sensible en `public/`** ni en GitHub Pages.
- Si un PDF con datos reales de cliente se genera localmente, debe tratarse con la misma seguridad que cualquier dato privado del cliente.

### `render-pdf.yml` — SOLO para demos y QA visual

`render-pdf.yml` genera un PDF de `print.html` para revisar el diseño visual. **No es el flujo del PDF completo de clientes.**

Razón: el `print.html` que genera GitHub Actions solo contiene datos públicos (sin WiFi, códigos, acceso). Los datos privados viven en Cloudflare KV y no están disponibles para GitHub Actions.

El workflow tiene tres protecciones:
1. Solo acepta los 4 slugs de demo oficiales (`ocean-drive-retreat`, `the-soho-loft`, `casa-selva-tulum`, `le-marais-flat`).
2. Requiere campo `confirm_demo_only: true` explícito.
3. Escanea el `print.html` en busca de patrones sensibles antes de generar.
4. El PDF resultante se sube como artefacto (14 días), **nunca como commit a `public/`**.

### Demos con `print.pdf` existente

Los 4 demos en `public/villas/*/print.pdf` fueron generados con datos ficticios. Son aceptables como demos visibles. No agregar más `print.pdf` a `public/` salvo para demos con datos claramente ficticios.

### Opción futura — PDF generado por Worker

Endpoint: `/print/<slug>/pdf` — valida token, genera el PDF completo en el servidor. Usar `cache-control: no-store`.

Actualmente el endpoint `/print/<slug>?token=` sirve el HTML con datos privados inyectados. El host hace `Print / Save as PDF` manualmente. En el futuro, el Worker podría generar el PDF directamente (requiere headless browser o servicio externo).

---

## Validación de `house_access_public`

Este campo solo puede contener orientación general no sensible. Ejemplos correctos:
- "La entrada principal está frente a la calle principal."
- "La información de acceso se cargará automáticamente en la guía al abrir el link correcto."

Prohibido: códigos de puerta, lockbox codes, keypad codes, PINs, passwords, combinaciones alfanuméricas tipo código.

El generador debe advertir o bloquear si `house_access_public` contiene: números de 4+ dígitos, `code`, `código`, `keypad`, `lockbox`, `password`, `passcode`, `PIN`, `door code`, combinaciones tipo `A1847B`.

---

## Secciones con placeholders prohibidos

Las secciones Access & Parking y WiFi NO deben contener textos como:
- "Detailed arrival instructions will be shared privately before check-in."
- "WiFi details are protected and appear..."
- "Ask your host for WiFi."
- "Access details will be sent later."

La guía se entrega después de reservar. Debe mostrar información completa cuando se abre con link válido. Los datos sensibles se cargan desde Worker/KV.

---

## Mensaje de producto correcto

No decir: public guide, private guide, separate private section, ask your host for details, WiFi appears later.

Sí decir:
- "One beautiful digital guide for your guests."
- "Everything your guests need, right on their phone."
- "A secure guest link with all stay details."
- "Sensitive details are loaded securely, not published in the website code."

En español:
- "Una sola guía digital con todo lo que tus huéspedes necesitan."
- "Un link seguro para compartir la información de la estancia."
- "Los datos sensibles se cargan de forma segura; no quedan publicados en el código del sitio."

---

## Menú principal de la guía

Categorías: Getting There · Check-in/out · Access & Parking · WiFi · The House · House Rules · Things to Know · Restaurants · Bars & Drinks · Things to Do · Contact · Emergency

Estética: premium, hospitality-editorial, claro, mobile-first. NO: SaaS corporativo, infantil, genérico.

---

## Identidad visual MyGuest

Sensación: calmado, moderno, premium, cálido, editorial, minimal, mobile-first.

Paleta (website, landing, marketing; no necesariamente los books de clientes):
- Warm Ivory `#F7F3EE`
- Soft Sand `#EFE7DD`
- Soft Charcoal `#2B2B2B`
- Warm Gray `#7A746E`
- Light Taupe `#D8CEC2`
- Lagoon Teal `#59C3C3`
- Deep Teal `#2D6A73`
- Sunset Coral `#F29B7F`

Reglas: mucho whitespace, bordes redondeados suaves, sombras muy suaves, CTAs claros, fotografía cálida y premium.

---

## Validaciones de seguridad (antes de commit o entrega)

Buscar en todo el repo:
`wifi_password`, `house_access_private`, `host_phone`, `lockbox`, `keypad`, `code`, `password`, `pin`, `door code`, `access code`, `building code`, `Detailed arrival instructions`, `WiFi details are protected`, `SunsetBeach2024`, `7842`, `4521`

Verificar: dónde aparece, si está en `public/`, si es riesgo real o solo referencia de código.

---

## Reglas no negociables

- No meter WiFi/password/códigos reales en GitHub Pages.
- No publicar PDF completo sensible en `public/` ni como archivo público.
- Mantener separación técnica estricta entre shell público y datos completos seguros.
- La experiencia debe ser una sola guía completa.
- No pedir contraseña al huésped.
- No crear dos libros separados para el huésped.
- No dejar placeholders incorrectos de tipo "los datos se enviarán después".
- No cambiar arquitectura sin validarlo contra el plan aprobado.
- Si hay adjuntos, NO generar ni entregar hasta revisión manual de Vero.
- No hacer commit si hay riesgos abiertos de seguridad o textos viejos incorrectos.

---

## Criterio de aprobación MVP

El MVP está listo para vender cuando se cumpla:

- Cliente paga
- Cliente llena Tally
- Se puede generar una guía real
- La guía tiene toda la información
- WiFi y acceso aparecen con link válido
- WiFi y acceso no aparecen en código público
- El huésped no necesita contraseña
- El host comparte un solo link
- El PDF/imprimible también queda completo (via Print/Save as PDF)
- El PDF completo no queda publicado como archivo público sensible
- Diseño móvil aprobado
- Menú aprobado
- Google Maps claro y clickable
- No hay placeholders incorrectos
- Demos en `demo_mode` usan credenciales ficticias realistas (WiFi/códigos inventados) — nunca datos reales de clientes
- QA manual documentado
- Entrega final clara al cliente

---

## Seguridad del negocio

- 2FA activo en todas las cuentas críticas: GitHub, Cloudflare, Tally, dominio, email, plataforma de pago.
- No compartir contraseñas por WhatsApp, email o chat.
- No poner tokens dentro del repo.
- No commitear archivos `.env` ni passwords ni datos reales de clientes.
- Usar GitHub Secrets para tokens y Cloudflare Secrets para secretos del Worker.
- Todo input de Tally es no confiable: escapar HTML, usar `textContent` en lugar de `innerHTML`.
- Validar URLs: solo `https://` o `http://`, bloquear `javascript:`, `data:`.
- Agregar `rel="noopener noreferrer"` en links externos.
- Adjuntos: aceptar solo PDF, DOCX, JPG, PNG, HEIC. Bloquear .exe, .bat, .cmd, .js, .html, .php, .zip.
- Antes de cada entrega: verificar que el link correcto es para el cliente correcto, que sin token no se ven datos sensibles, que no hay secretos en View Source.

---

## Estrategia de marketing Pinterest (decisión mayo 2026)

### Para PUBLICIDAD (Pinterest pins):
- **ChatGPT genera las imágenes directamente** — no se usa HTML/CSS
- No se necesitan datos reales en imágenes de publicidad
- **Pendiente**: crear 8 prompts reutilizables de ChatGPT para flujo semanal

### Para el PRODUCTO / DEMOS:
- Se sigue usando el sistema HTML/CSS + Playwright para renderizar guías reales
- Los 4 demos reales tienen screenshots capturados en `marketing/pinterest/assets/screenshots/`

---

## Estructura de archivos clave

```
books/                              ← Motor de generación de guest books
  scripts/
    generate_villa.py               ← Genera la guía web (HTML) de una propiedad
    build_print_pdf.py              ← Genera el PDF imprimible
    postprocess_public_book.py      ← QA visual post-generación
    _generate_demo_*.py             ← Generadores de demos
  templates/
    master.html                     ← Template web
    print_letter.html               ← Template PDF imprimible
  preview_print_redesign.html       ← Prototipo rediseño PDF (borrador)

marketing/
  instagram/                        ← Sistema de posts para Instagram (1080×1080px)
    templates/                      ← 9 plantillas HTML
    scripts/
      export-posts.js               ← Renderiza posts con Puppeteer
      generate-mockups.js           ← Genera mockups de celular (npm run mockups)
    assets/mockups/phone/           ← PNGs pre-generados del celular (frame + screen combinados)
    assets/mockups/*-hi.png         ← Imágenes de pantalla compuestas manualmente
                                       NO son screenshots de los demos. Se crean con Gemini/diseño.
                                       NUNCA reemplazar con capturas automáticas de public/villas/.
    posts.json                      ← Definición de posts (copy + estilo)
    preview/                        ← Preview grid en browser

  pinterest/                        ← Sistema de pins para Pinterest (1000×1500px)
    templates/                      ← 8 plantillas HTML
    styles/pinterest-v2.css         ← CSS compartido (4 temas, phone, strip)
    assets/screenshots/             ← Screenshots de los 4 demos reales
    data/
      pinterest_campaign_v2.json    ← 32 pins definidos
    scripts/
      render_qa_sample.py           ← Renderiza 8 QA samples (aprobación visual)
      render_pinterest_v2.py        ← Renderiza 32 pins finales
      validate_pinterest_copy.py    ← Valida copy antes de renderizar
    output/                         ← PNGs generados y metadata
    output-weekly/                  ← Pins semanales generados con ChatGPT
    pins/                           ← PNGs ya publicados + Excel de seguimiento
    docs/                           ← Guías operativas
    v1/                             ← Templates v1 (obsoletos, referencia)

  assets/                           ← Materiales de ventas generales

public/                             ← Web root de GitHub Pages (myguestguide.com)
  index.html                        ← Landing page
  villas/                           ← 4 demos reales desplegados
  assets/covers/                    ← Imágenes de portada usadas en guías
  landing/                          ← Assets de landing (logos, mockups, mascota)

worker/
  worker.js                         ← Cloudflare Worker (Tally → KV → GitHub dispatch)

.github/workflows/
  generator.yml                     ← repository_dispatch tipo new-villa → genera guest book
  render-pdf.yml                    ← Genera PDF como artefacto (NO commit a public/)
  pages.yml                         ← Despliega a GitHub Pages
  instagram-publish.yml             ← Auto-publica posts de Instagram (cron diario)
  render-pinterest-v2.yml           ← Renderiza 32 pins Pinterest (manual)
```

---

## Demos reales (4 propiedades)

| Slug | Estilo | Nombre |
|------|--------|--------|
| `ocean-drive-retreat` | Coastal | Ocean Drive Retreat |
| `the-soho-loft` | Minimalist | The SoHo Loft |
| `casa-selva-tulum` | Sunset | Casa Selva Tulum |
| `le-marais-flat` | Classic | Le Marais Flat |

**Demo mode**: solo para demos comerciales. El código debe mostrar warning claro si `demo_mode: True`.

**Política de credenciales en demos oficiales**: Los 4 demos oficiales (`ocean-drive-retreat`, `the-soho-loft`, `casa-selva-tulum`, `le-marais-flat`) pueden contener credenciales ficticias realistas (WiFi network, contraseñas, códigos de acceso, teléfonos inventados) para mostrar la experiencia real del huésped. Esto es aceptable **solo en `demo_mode: True`** y **solo con datos completamente inventados**. Usar datos reales de un cliente en `demo_mode` es un bug crítico de seguridad. Las guías reales de clientes nunca exponen WiFi, códigos ni acceso en HTML público — esos datos solo se sirven vía Worker/KV con token válido.

---

## CSS — Estructura del sistema (pinterest-v2.css)

### 4 temas: `style-coastal` | `style-minimalist` | `style-sunset` | `style-classic`

### Layout fijo (compartido):
- `main.pin`: 1000×1500px, `overflow:hidden`
- `.v2-brand`: top-center, `+ MyGuest`
- `.v2-phone`: `right:28px; top:108px; width:420px; height:860px`
- `.v2-copy`: `left:40px; right:40px; top:1008px`
- `.v2-strip`: `bottom:0; height:192px`

### PROBLEMA CONOCIDO con fondos:
Las imágenes `hero.png` son screenshots de la app MyGuest (muestran UI con texto), NO fotos reales. El texto se filtra a través del overlay. **Solución en template-01**: gradiente CSS puro sin foto de fondo.

---

## Comandos frecuentes

```bash
# Instagram
npm run preview        # preview en http://localhost:3100
npm run export         # renderiza posts a PNG
npm run mockups        # regenera mockups de celular

# Pinterest
python -m http.server 8020 --directory marketing/pinterest
python marketing/pinterest/scripts/render_qa_sample.py --base-url http://localhost:8020/templates/

# Guest books
python books/scripts/generate_villa.py <property-slug>
```

---

## Reglas de copy (NUNCA escribir en ningún pin ni material)

- No mencionar AI extrayendo documentos automáticamente
- No decir "en minutos", "sin trabajo extra", "importación instantánea"
- No usar yuyitov.github.io como URL
- Todos los links deben ir a **myguestguide.com**

---

## Arquitectura multilingüe (implementada en commit `06ea48d`, 2026-06-09)

### Mobile guide (`worker/worker.js`)
- `PRIVATE_BOOK_LABELS` — dict con etiquetas privadas en EN/ES/FR: WiFi Network, WiFi Password, Private Access Details, Host Phone, Door Code, Building Code, Access.
- `buildPrivateBookBlocks(secrets, lang)` — usa el dict según el idioma de la URL (`?lang=es`).
- `injectPrivateDetailsIntoBookHtml({ html, slug, token, secrets, lang })` — pasa `lang` desde `handleGuestPrivateAccess` (que ya tenía `const lang = normalizePrivateBookLang(...)`).
- `injectPrivateDetailsIntoPrintHtml` — itera `['en', 'es', 'fr']`, inyecta con labels traducidos en cada placeholder `private-house-print-block-{lang}`. Usa `split().join()` (no `replace`) para reemplazar todos los idiomas.

### Printable (`books/scripts/build_print_pdf.py`)
- Importa `translate_public_content` y `flatten_content` de `generate_villa.py` con lazy import (si falla, usa stubs que devuelven el contenido sin cambios).
- `_rewrap_translated(base_content, translated_flat)` — pone valores flat traducidos de regreso en la estructura nested que usan los `build_*()` functions.
- `build_house(content, ui)` — genera `<div id="private-house-print-block-{ui['html_lang']}"></div>` (IDs únicos por idioma: `-en`, `-es`, `-fr`).
- Loop de idiomas: para Español y Français llama `translate_public_content` → `_rewrap_translated` → pasa contenido traducido a `_pages_for_lang(lang, translated_content)`.

### Workflow (`generator.yml`)
- Step "Build Print PDF" ahora incluye `OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}`.

### Comportamiento verificado (prueba `maison-mar-serena-gbaea4l`, 2026-06-09)
- Generate Villa Page: traduce 10 campos en 4 batches para ES y FR.
- Build Print PDF: mismo proceso de traducción para ES y FR del printable.
- QA: "QA OK: no private/sensitive terms found in public text outputs."
- Nota: `wifi_password` y `house_access_private` aparecen como identificadores JS en el template (`d.wifi_password`) — no son valores reales. El QA del workflow los distingue correctamente.

---

## Notas técnicas críticas (aprendidas en sesión)

- **`wrangler kv key list/get` requiere `--remote`** — sin ese flag lee almacenamiento local vacío.
- **`gh run rerun` usa el `headSha` del run original**, no HEAD actual de main. Para `repository_dispatch`, `actions/checkout@v4` sin `ref:` hace checkout del `headSha` guardado en el evento — no del código más reciente. Si se necesita re-generar una villa con código nuevo, la única opción segura es un nuevo `repository_dispatch` o que el cliente vuelva a enviar el formulario.
- **`handleNotify` tiene idempotencia** — si `delivery.status === 'delivered'` devuelve `{ ok: true, idempotent: true }` sin re-enviar email. Safe para re-runs del pages.yml.

---

## Estado actual (actualizado 2026-07-16)

**MyGuest está LIVE con GO para venta pública.**

- **G-06 (compra controlada LIVE)**: cerrado con PASS completo, refund hecho y limpieza G06 completada.
- **MyGuest 07**: landing multi-moneda cerrada (commit `483b8b2` — from $29 USD / MXN 499 / CAD 41.99).
- **MyGuest 08 (limpieza KV)**: cerrado el 2026-07-02 — 127 KV keys de pruebas confirmadas borradas en bulk (SMOKETEST*, FLOWATEST, hmac, mar-serena, g02c/g02d, FULLTEST/villa-maralto, adjuntos, paid-flow QA, pruebas manuales abril-mayo).
- **`public/villas/` limpio**: solo contiene los 4 demos oficiales (`ocean-drive-retreat`, `the-soho-loft`, `casa-selva-tulum`, `le-marais-flat`), verificados en 200.
- **MyGuest 08b (Grupo C)**: cerrado el 2026-07-16 — las 19 keys se identificaron una por una y resultaron ser todas pruebas propias: 9 `subm-*` de villas de test ya despublicadas (`casa-mar-serena-*`, `test-sin-adjuntos`, `casa-stripe-test-c`, etc. — ninguna existe en `public/villas/`, verificado), 7 `subm-*` de formularios abandonados en abril (`slug: null`, `status: received`), 2 `order:pi_*` de compras de prueba de Vero a su propio correo (`duplicate-order-qa-should-not-generate` y `g02d-upload-test-villa`, ambas `delivered`), y `priv-ocean-drive-retreat-miami-beach-7xnzlba` + `subm-7XNzLBA` (un test, **no** el demo `ocean-drive-retreat`). Borradas en bulk con aprobación de Vero; backup previo en `charly/backups/kv/2026-07-16/MYGUEST_KV.json`.
- **KV restante (3 keys, 2026-07-16)**:
  - **Grupo B (TTL)**: 3 `invalid_order:courtesy_*` — eran 8; los `processed:pi_*` y `rl:*` ya expiraron solos. Dejar expirar, no tocar.
  - No queda ninguna key sin identificar.

---

## Pendientes al retomar

### Limpieza de pruebas — ✅ CERRADA (MyGuest 08, 2026-07-02 · 08b, 2026-07-16)
- **KV**: las keys de prueba documentadas aquí (mar-serena, SMOKETEST, hmac, villa-maralto, etc.) fueron borradas — 127 keys en total. El grupo C (19 keys) se identificó y borró el 2026-07-16 (MyGuest 08b). Solo quedan 3 keys del grupo B, con TTL, que expiran solas. Ver "Estado actual".
- **GitHub Pages**: `public/villas/` quedó limpio — solo los 4 demos oficiales.

### Seguridad / Infraestructura
1. ~~**Rotar `NOTIFY_SECRET`**~~ — ✅ **Resuelto 2026-07-17** (P5). Rotado a un valor aleatorio de 48 chars con el MISMO valor en Cloudflare Worker (`wrangler secret put`) y GitHub Actions (`gh secret set`). Verificado por HTTP: bearer incorrecto → 401, bearer nuevo + slug inexistente → 404 `delivery record not found` (auth OK, sin efectos secundarios). Valor nunca impreso ni commiteado.
2. ~~**Llenar KV namespace ID** en `worker/wrangler.toml`~~ — ✅ hecho: ya trae el ID real (`4353e51b...`). Ojo: ese archivo está en `.gitignore`, así que solo existe en la máquina de Vero; quien clone el repo tiene que crearlo.
3. **Verificar Resend API key** — confirmar que pertenece a la cuenta correcta y que `hello@myguestguide.com` está verificado.
4. **Configurar webhook en Tally**: Tally → Integrations → Webhooks → `https://myguest-worker.veronica-perezarroyo.workers.dev/tally-webhook`.
5. **Limpiar KV de prueba** — ✅ Resuelto (MyGuest 08, 2026-07-02): SMOKETEST01-05, SMOKETEST10, FLOWATEST01 y registros hmac borrados.
5b. **Limpiar carpeta de prueba** `public/villas/hmac-test-no-entregar-zezdgrg/` — ✅ Resuelto: ya no existe en `public/villas/`.
6. **Limpiar páginas de prueba** (`smoke-test-flujo-a-...`, villa-maralto-0260606a01/b01/c01) — ✅ Resuelto: carpetas eliminadas y KV borrado en MyGuest 08; URLs verificadas en 404.
7. **Node.js 20 deprecation** en GitHub Actions — forzado Node 24 desde el 16 junio 2026, eliminado el 16 septiembre 2026. Actualizar `actions/checkout@v4`, `actions/setup-python@v5`, `actions/configure-pages@v5`, `actions/deploy-pages@v4`, `actions/upload-artifact@v4` a versiones que soporten Node 24.
8. **Desplegar worker.js via Wrangler** — autenticación configurada y funcional (`npx wrangler deploy` desde `worker/`). ✅ Resuelto.
9. **Pinear SHAs en GitHub Actions** — las actions de terceros (checkout, setup-python, etc.) deben anclarse a SHA completo en lugar de tag. Pendiente para post-MVP.

### Corrections flow — ✅ VERIFICADO E2E (2026-07-17, P11)
- El link `/correct/<slug>?token=` redirige a Tally `Ek6EM2` con pre-fill de `slug`, `correction_token`, `customer_email`, `form_type=corrections`. El form Ek6EM2 tiene los 4 hidden fields configurados (confirmado en su esquema).
- Prueba controlada (key `correction:p11-corrections-test` creada y borrada con aprobación de Vero): token inválido → 404; envío real firmado por Tally → worker marcó `used:true` (`used_at` registrado) → **confirma también la pata Tally→worker de A4** (TALLY_SIGNING_SECRET sincronizado); segundo acceso → página "already used" (sin redirigir a Tally). Alert email a `ALERT_EMAIL` es non-fatal (`.catch`).
- Nota operativa: el submit de Tally (React) NO se dispara por automatización de navegador (ni click sintético ni `requestSubmit`); requiere un clic humano real. Para futuras pruebas E2E del form, que Vero haga el clic de envío.

### Diseño — ✅ DECISIÓN TOMADA (2026-07-17, P5)
Vero revisó una guía real (Ocean Drive Retreat, móvil ES/EN + PDF) y decidió: **el producto es suficiente para vender**. El diseño móvil y el imprimible YA cumplen sus dos requisitos:
- Imprimible SIN links de Google Maps en Restaurants/Bars/Things to Do → renderiza dirección + teléfono (`build_print_pdf.py` `build_recommendations`, `_is_maps_url()` filtra los maps URLs). ✅
- PDF trilingüe EN+ES+FR en un solo archivo con páginas divisorias (`SUPPORTED_LANGUAGES`, loop en `render_print_html`). ✅
- `master.html` (móvil) aprobado como está.

**Único remanente = marketing, no producto:** los 4 PDF demo en `public/villas/*/print.pdf` son de 2026-05-10 (anteriores a esas features) → muestran inglés-only con links de Maps. Regenerarlos es una **tarea de marketing** (refrescar muestra de venta), registrada en el Centro; NO bloquea el 100% del producto.

### Pinterest / Marketing
- **Crear 8 prompts de ChatGPT** para generación semanal de imágenes publicitarias de Pinterest
- **Workflow semanal**: prompts → AI images → descargar → subir a Pinterest
- **NO renderizar los 32 pins finales** hasta aprobación visual de los 8 QA samples
- Si se continúa con HTML templates: revisar templates 02-08 con el usuario uno por uno

Ver detalle completo en `docs/mvp-delivery-flow.md`.

---

## Repo GitHub

`https://github.com/yuyitov/MyGuest` — branch: `main`

---

## Sincroniza pendientes con el tablero central

Los pendientes de My Guest están centralizados en el business-dashboard: `C:\Users\veron\Negocios Digitales\Dashboard\business-dashboard\config\pendientes.json`, bajo el área `"myGuest"`.

**Al cerrar una tarea que esté listada ahí como pendiente, márcala hecha** antes de terminar la sesión: en ese archivo ubica el área `"myGuest"`, encuentra el ítem por su `"n"` y agrégale `"hecho": true`. No borres ni renumeres los demás ítems, y no inventes pendientes nuevos (si lo que hiciste no está en la lista, déjalo). Con eso desaparece de los dos tableros: el business-dashboard al recargar y el de Charly al reabrirlo. Si el business-dashboard corre en `127.0.0.1:4545`, equivale a `POST /api/pendientes/done` con `{ "areaId": "myGuest", "n": <n>, "hecho": true }`.
