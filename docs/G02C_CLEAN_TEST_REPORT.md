# G-02C — Prueba end-to-end TEST limpia

**Fecha:** 2026-06-27
**Estado:** ✅ Cerrada y limpia.

---

## Objetivo de la prueba

Validar el flujo completo sin archivos adjuntos en un entorno TEST limpio:
Stripe TEST → KV → email post-pago → Tally → Worker → GitHub Actions → GitHub Pages → email final → links privados → auditoría de seguridad → limpieza.

Se usó un alias de email (`+myguesttest`) para evitar el bypass `isVeroTest` y obtener un resultado realista del flujo de producción.

---

## Datos de prueba

| Campo | Valor |
|---|---|
| PaymentIntent TEST | `pi_3TmlcXG4Nw60erBP16CoGC3H` |
| Email | `veronica.perezarroyo+myguesttest@gmail.com` |
| Slug generado | `property-name-g02-clean-test-no-live-o9dg16x` |
| Formulario Tally | `MedpvA` |
| Primary language | English |
| Pet friendly | Yes (con pet rules ficticias) |
| Archivos adjuntos | Ninguno |
| Datos privados | Completamente ficticios (sentinel values) |

---

## Flujo validado — paso a paso

### A. Pago Stripe TEST

- Pago procesado correctamente con tarjeta de prueba.
- Evento `checkout.session.completed` recibido por Worker.
- `order:pi_3TmlcXG4Nw60erBP16CoGC3H` creado en KV con:
  - `status: paid`
  - `customer_email` correcto
  - `amount: 10000`, `currency: mxn`
- Email post-pago recibido con link de Tally incluyendo:
  - `order_id`
  - `customer_email`

### B. Tally MedpvA

- Formulario abierto con hidden fields pre-rellenados.
- Enviado con datos ficticios realistas.
- Ningún archivo subido → flujo directo sin `needs_manual_extraction`.

### C. Worker procesó submission

- Guards pasados sin errores:
  - `order_id` presente
  - email match correcto
  - `status: paid` válido
- Payload público y privado separados correctamente.
- `priv-{slug}` creado en KV con datos ficticios.
- `repository_dispatch` disparado a GitHub Actions.

### D. GitHub Actions generator

- Run ID: `28276098824`
- Status: ✅ success (2m17s)
- Steps completados: Validate payload → Generate Villa Page → Postprocess QA → Build Print PDF → QA public outputs → Commit and Push

### E. GitHub Pages deploy

- Run ID: `28276151599`
- Status: ✅ success (24s)
- Step `Notify Worker (send delivery email)` completado.

### F. Archivos generados — HTTP 200

| Archivo | HTTP |
|---|---|
| `en.html` | 200 |
| `es.html` | 200 |
| `fr.html` | 200 |
| `index.html` | 200 |
| `print.html` | 200 |
| `print.pdf` | 200 |

### G. KV post-generación

| Key | Estado |
|---|---|
| `order:{pi}` | status `generation_dispatched` |
| `delivery:{slug}` | status `delivered`, `notified_at` presente |
| `priv-{slug}` | `status: stored_private`, datos ficticios en `secrets` |
| `correction:{slug}` | existía con `used: false` |

### H. Email final

Recibido con los tres links:
- Digital guide (`/guest/{slug}?token=...`)
- Printable guide (`/print/{slug}?token=...`)
- Correction link (`/correct/{slug}?token=...`)

### I. Links privados (verificación manual)

- Guest link con token → mostró WiFi, acceso privado y teléfono ficticios ✅
- Print link con token → mostró privados inyectados ✅
- Correction link → abrió `Ek6EM2` con pre-fill de 4 campos ✅
- Guest link sin token → no expuso datos privados ✅

---

## Auditoría de seguridad pública

| Dato privado (sentinel ficticio) | `en.html` público | `print.html` público |
|---|---|---|
| `G02_TEST_WIFI_NETWORK` | ✅ NOT FOUND | ✅ NOT FOUND |
| `G02_TEST_WIFI_PASSWORD_2026!` | ✅ NOT FOUND | ✅ NOT FOUND |
| `G02-2468` (gate code) | ✅ NOT FOUND | ✅ NOT FOUND |
| `G02-1357` (lockbox code) | ✅ NOT FOUND | ✅ NOT FOUND |
| `+523220000000` (teléfono) | ✅ NOT FOUND | ✅ NOT FOUND |
| `correction_token` literal | ✅ NOT FOUND | ✅ NOT FOUND |
| `guest_access_token` literal | ✅ NOT FOUND | ✅ NOT FOUND |

`wifi_password` y `house_access_private` aparecen en `en.html` solo como identificadores JS (`d.wifi_password`, `d.house_access_private` en líneas 2034–2036) — son referencias de código del template que leen la respuesta del Worker, no valores reales. Comportamiento correcto.

`print.html` tiene tres placeholders vacíos `private-house-print-block-{en|es|fr}` — correctos, se llenan vía Worker con token.

---

## Bug detectado y corregido

### Descripción

El guest link entregado sin `?lang=` mostraba en la vista EN:

```
Private Access Details — provided in English
```

### Causa raíz

En `handleGuestPrivateAccess` (worker.js), `lang = normalizePrivateBookLang(url.searchParams.get('lang'))` devuelve `''` cuando no hay `?lang=` en la URL. Luego `buildPrivateBookBlocks(secrets, '', 'en')` evaluaba:

```js
langMismatch = sourceLang && sourceLang !== lang
// = 'en' && ('' !== 'en') → true  ← BUG
```

La cadena vacía no es 'en', pero tampoco es un idioma diferente — es la ausencia del parámetro.

### Fix aplicado

En `injectPrivateDetailsIntoBookHtml` (worker.js), se agregó normalización del lang vacío:

```js
const effectiveLang = lang || 'en';
const privateBlocks = buildPrivateBookBlocks(secrets, effectiveLang, sourceLang);
```

### Resultado post-fix

| View (URL param) | Source lang (KV) | Label mostrado |
|---|---|---|
| Sin `?lang=` | `en` | `Private Access Details` ✅ |
| `?lang=en` | `en` | `Private Access Details` ✅ |
| `?lang=es` | `en` | `Detalles de acceso privado — proporcionado en inglés` ✅ |
| `?lang=fr` | `en` | `Détails d'accès privé — fourni en anglais` ✅ |

### Commits y deploy

| Acción | ID |
|---|---|
| Commit fix | `52a2691 Fix private access language annotation in default guest view` |
| Worker deploy | Version ID `5b7b680f-035f-4ee0-9e8e-2ad6229827b5` |

---

## Nota sobre `Property name:` en portada

En la portada del printable apareció `Property name: G02 Clean Test No Live`.

**Diagnóstico:** no fue un bug de código. La submission Tally `o9dG16X` (campo `kAXBor`) tiene `answer: "Property name: G02 Clean Test No Live"` — el valor fue capturado con el label incluido por error en la captura de prueba. El código es correcto: extrae y muestra el valor exacto del campo.

Todas las otras submissions tienen nombres limpios (ej. `Casa Stripe Test C`, `Maison Mar Serena Test A`). No se aplicó normalización automática.

---

## Limpieza final

### GitHub Pages

Commit: `8e25c2d Remove G-02C test villa pages`

Pages deploy run: `28306308278` — ✅ success (21s)

Archivos eliminados:
- `public/villas/property-name-g02-clean-test-no-live-o9dg16x/en.html`
- `public/villas/property-name-g02-clean-test-no-live-o9dg16x/es.html`
- `public/villas/property-name-g02-clean-test-no-live-o9dg16x/fr.html`
- `public/villas/property-name-g02-clean-test-no-live-o9dg16x/index.html`
- `public/villas/property-name-g02-clean-test-no-live-o9dg16x/print.html`
- `public/villas/property-name-g02-clean-test-no-live-o9dg16x/print.pdf`

Verificación: todos los 6 archivos devuelven HTTP 404 ✅

### KV

| Key | Estado pre-delete | Acción |
|---|---|---|
| `delivery:property-name-g02-clean-test-no-live-o9dg16x` | EXISTS | DELETED ✅ |
| `priv-property-name-g02-clean-test-no-live-o9dg16x` | EXISTS | DELETED ✅ |
| `order:pi_3TmlcXG4Nw60erBP16CoGC3H` | EXISTS | DELETED ✅ |
| `processed:pi_3TmlcXG4Nw60erBP16CoGC3H` | EXISTS | DELETED ✅ |
| `correction:property-name-g02-clean-test-no-live-o9dg16x` | NOT FOUND (TTL expirado) | — |

Verificación post-delete: 5/5 GONE ✅

---

## Conclusión

- ✅ El flujo automático sin archivos adjuntos funciona de extremo a extremo.
- ✅ El sistema no expone privados públicamente.
- ✅ El fix de anotación de idioma fue corregido, testeado y desplegado.
- ✅ La limpieza post-prueba quedó completa.
- ⏳ Pendiente: G-02D (prueba con uploads/fotos/archivos) — diferida para antes de primera venta con adjuntos.
- ⚠️ Stripe LIVE sigue pendiente y no debe activarse todavía.
