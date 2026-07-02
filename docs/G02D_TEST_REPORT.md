# G02D-B TEST REPORT — Uploads + Manual Extraction

**Fecha de prueba:** 2026-07-01  
**Entorno:** Stripe TEST, Worker desplegado, GitHub Pages  
**Slug de prueba:** `g02d-upload-test-villa-6dv9zop`  
**Submission ID original (Tally MedpvA):** `6Dv9zoP`  
**Formulario de revisión:** yP1y9B — MyGuest Manual Extraction Review  
**Worker deploy ID:** `63db37bd-d9b5-414d-862d-a5b3ab1b3202`

---

## Alcance de la prueba

- Pago Stripe TEST (MXN $100.00, tarjeta 4242, entorno de prueba confirmado)
- Envío de MedpvA con adjuntos dummy: PDF (1084 bytes) + JPEG real (364 bytes, FF D8 FF)
- Detección de adjuntos por Worker → bloqueo de generación automática
- KV → `needs_manual_extraction`
- Email interno de alerta con links de archivos y link a yP1y9B
- yP1y9B: prueba con "No — falta información"
- yP1y9B: prueba con "Sí — lista para generar" + datos dummy
- Dispatch a GitHub Actions
- Despliegue a GitHub Pages
- Email final de entrega
- Auditoría anti-fuga en HTML público

---

## Resultados

### Prueba "No — falta información"

| Registro KV | Status final |
|-------------|-------------|
| `subm-6Dv9zoP` | `manual_extraction_incomplete` |
| `intake:g02d-upload-test-villa-6dv9zop` | `manual_extraction_incomplete` |
| `delivery:g02d-upload-test-villa-6dv9zop` | `manual_extraction_incomplete` |
| `order:pi_3To8NuG4Nw60erBP1IimN7eR` | `manual_extraction_incomplete` |
| `priv-g02d-upload-test-villa-6dv9zop` | `stored_private` (sin cambios) |

- Dispatch a GitHub Actions: **NO ejecutado** ✅
- Email final al cliente: **NO enviado** ✅
- `delivery.notified_at`: **ausente** ✅
- `console.log` Worker: `manual extraction incomplete: {slug, original_submission_id}` ✅

### Prueba "Sí — lista para generar"

| Registro KV | Status final |
|-------------|-------------|
| `subm-6Dv9zoP` | `dispatched_to_github` |
| `intake:g02d-upload-test-villa-6dv9zop` | actualizado con merge de revisión |
| `delivery:g02d-upload-test-villa-6dv9zop` | `delivered` |
| `order:pi_3To8NuG4Nw60erBP1IimN7eR` | `delivered` |
| `priv-g02d-upload-test-villa-6dv9zop` | `manual_extraction_complete` |

- `delivery.notified_at`: `2026-07-02T00:30:17.584Z` ✅
- `priv.secrets`: WiFi, door_code, building_code, lockbox_code, host_phone, house_access_private — todos dummy, todos presentes ✅
- GitHub Actions `MyGuest Generator`: **success** (`2026-07-02T00:28:21Z`) ✅
- GitHub Actions `Deploy MyGuest Pages`: **success** (`2026-07-02T00:29:49Z`) ✅
- Archivos generados: `index.html`, `es.html`, `fr.html`, `print.html`, `print.pdf` ✅
- Email `/notify` llamado: `2026-07-02T00:30:16Z` ✅

### Auditoría anti-fuga (HTML público)

Términos buscados en `public/villas/g02d-upload-test-villa-6dv9zop/`:

```
G02D_TEST_WIFI_REVIEW · G02D_TEST_PASSWORD_REVIEW_2026 · G02D-DOOR-1111
G02D-BUILDING-2222 · G02D-LOCKBOX-3333 · 322 000 0000 · G02D private access
```

**Resultado: ningún término encontrado en ningún archivo HTML público.** ✅

Los datos privados dummy viven únicamente en KV (`priv-...`) y se sirven desde el Worker con token válido.

---

## Bugs encontrados y corregidos durante G02D-B

### 1. yP1y9B — hidden fields faltantes

**Problema:** El formulario yP1y9B solo tenía `flow_type` como hidden field. Los campos `original_submission_id`, `slug`, `property_name`, `customer_email`, `client_name` no existían como hidden fields. Tally no pasa params de URL a campos visibles automáticamente.

**Corrección:** Se agregaron 5 hidden fields vía Tally MCP (`configure_blocks` en bloque `4c18efb5`).

### 2. yP1y9B — inputs visibles bloqueantes

**Problema:** Los 5 campos de identificación (Original Submission ID, slug, property_name, client_name, customer_email) existían como INPUT_TEXT/EMAIL visibles y obligatorios (al menos `original_submission_id` marcado `isRequired: true`). Al abrir el formulario desde el link del email, Tally no prellenaba los campos visibles con los URL params, bloqueando el avance.

**Corrección:** Se eliminaron los 10 bloques (5 pares TITLE + INPUT) vía Tally MCP (`remove_blocks`). Los campos de identificación ahora se capturan únicamente vía hidden fields.

### 3. yP1y9B — signing secret ausente en webhook

**Problema:** El webhook de yP1y9B fue configurado sin signing secret. El Worker tiene `TALLY_SIGNING_SECRET` activo. La función `verifyTallySignature` (línea 118) retorna `false` si `signatureHeader` está vacío, causando 401 silencioso. Tally marcaba el evento como "Failed"; el Worker mostraba `Ok` en `wrangler tail` porque el 401 es una respuesta controlada.

**Corrección:** Se copió el mismo signing secret del webhook activo de MedpvA al webhook de yP1y9B desde Tally UI.

### 4. Worker — camino "No" no implementado

**Problema:** `handleManualExtractionReview` no tenía ningún camino para cuando la extracción se marca como incompleta. Si se enviaba yP1y9B sin aprobación, el Worker continuaba hacia el dispatch.

**Corrección:** Se añadió la rama `!extractionComplete` que actualiza todos los registros KV a `manual_extraction_incomplete` y retorna sin dispatch.

### 5. Worker — retry bloqueado por estado

**Problema:** El guard de estado en `handleManualExtractionReview` solo aceptaba `needs_manual_extraction`. Después de una respuesta "No" (estado `manual_extraction_incomplete`), un segundo submit con "Sí" era rechazado con 409.

**Corrección:** Se reemplazó el check estricto por `ALLOWED_REVIEW_STATUSES = new Set(['needs_manual_extraction', 'manual_extraction_incomplete'])`.

---

## Pendientes menores (no bloqueantes)

### Bloque visual "Caso en revisión" en yP1y9B

El bloque TEXT de contexto agregado en yP1y9B muestra los placeholders literales `{property_name}`, `{slug}`, `{original_submission_id}`, `{customer_email}` en lugar de los valores reales cuando el formulario se abre desde el link del email de alerta.

**Causa probable:** Los pipe variables `{nombre}` de Tally requieren que el campo esté configurado como pipe variable explícito vinculado a un hidden field, no solo como texto libre con sintaxis `{nombre}`. El bloque TEXT actual usa el texto literal, que Tally no resuelve automáticamente contra los hidden fields del mismo formulario.

**Impacto:** Ninguno sobre el flujo real. Los hidden fields sí llegan correctamente al payload del webhook y son la fuente real que usa el Worker (`original_submission_id`, `slug`, etc.). El bloque visual es solo orientación para Vero durante la revisión.

**Acción sugerida (post-MVP):** Reemplazar el bloque TEXT por un INPUT de solo lectura con default vinculado al hidden field, o eliminar el bloque y confiar en los hidden fields que sí funcionan.

### Verificaciones visuales pendientes (manuales)

- [ ] Confirmar visualmente que el email final recibido tiene el link correcto a la guía con token
- [ ] Abrir la guía mobile (`/guest/g02d-upload-test-villa-6dv9zop?token=...`) y confirmar que los privados dummy se muestran correctamente (WiFi, códigos, acceso)
- [ ] Abrir la guía imprimible (`/print/g02d-upload-test-villa-6dv9zop?token=...`) y confirmar lo mismo
- [ ] Confirmar visualmente que sin token los datos privados no aparecen

---

## Archivos modificados esperados en commit

```
worker/worker.js          — cambios en handleManualExtractionReview,
                            nueva función isManualExtractionApproved,
                            ALLOWED_REVIEW_STATUSES, REVIEW_META_KEYS

docs/G02D_TEST_REPORT.md  — este documento
```

### Archivos untracked que NO deben committearse

```
books/scripts/_regen_print_only.py
package-lock.json
public/landing/Identidad Visual/Logos/Gemini_Generated_Image_*.png
public/landing/Identidad Visual/Mascota/
worker/C꡻UsersveronAppDataLocalTempprint_test.html   ← artefacto temporal, borrar manualmente
```
