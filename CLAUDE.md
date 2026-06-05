# MyGuest — Contexto para Claude Code

## Qué es este proyecto

MyGuest es un sistema para crear welcome books digitales para anfitriones de Airbnb y rentas vacacionales.

El cliente (dueño del Airbnb) recibe 2 entregables completos:

1. Una guía digital móvil completa (link seguro).
2. Una versión PDF / imprimible completa (Print / Save as PDF desde la guía).

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
slug = slugify(property_name) + "-" + últimos 4 caracteres de submission_id
```

Ejemplo: `Casa Serena` + `01JSG4J8P2K9X7` → `casa-serena-k9x7`

Reglas: minúsculas, sin acentos, espacios → guiones, sin símbolos, sin dobles guiones, máx 50-60 caracteres antes del sufijo.

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

El PDF completo para clientes reales se obtiene con **Print / Save as PDF** desde la guía ya cargada con el link/token seguro en el navegador.

Flujo correcto:
1. El host abre la guía con su link seguro (token válido).
2. Los datos completos se cargan desde Cloudflare Worker/KV.
3. El host usa `Print / Save as PDF` desde el navegador.
4. El PDF resultante incluye WiFi, códigos, acceso y toda la información completa.

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

### Opción futura — PDF servido por Worker

Endpoint: `/guest/<slug>/pdf` — valida token, genera o entrega el PDF completo. Usar `cache-control: no-store`.

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
- Demos no usan credenciales que parezcan reales
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

**Demo mode**: solo para demos comerciales. Nunca usar datos reales. El código debe mostrar warning claro si `demo_mode: True`.

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

## Pendientes al retomar

1. **Crear 8 prompts de ChatGPT** para generación semanal de imágenes publicitarias de Pinterest
2. **Workflow semanal**: prompts → AI images → descargar → subir a Pinterest
3. **NO renderizar los 32 pins finales** hasta aprobación visual de los 8 QA samples
4. Si se continúa con HTML templates: revisar templates 02-08 con el usuario uno por uno

---

## Repo GitHub

`https://github.com/yuyitov/MyGuest` — branch: `main`
