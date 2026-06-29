# MyGuest — Final QA Checklist

## Estado actual

* Paso 1 cerrado: repo diagnosticado, sincronizado y `.gitignore` creado.
* Paso 2 cerrado: mobile private access muestra idioma de origen cuando hay mismatch.
* Bloque A cerrado técnicamente:

  * traducción pública EN/ES/FR desde idioma fuente no inglés;
  * printable corrige English desde fuente French;
  * pet\_friendly localizado;
  * pet\_rules traducible;
  * private access no se traduce por seguridad;
  * private access en mobile y printable muestra anotación de idioma.
* Prueba A validó lo principal del Bloque A.
* Prueba B se pospone para QA final.
* **G-02B cerrado**: landing + términos + privacidad + reembolsos publicados.
* **G-02C cerrado**: prueba end-to-end TEST sin adjuntos completada, fix Worker desplegado, villa limpiada.
  Ver detalle en `docs/G02C_CLEAN_TEST_REPORT.md`.

---

## QA final por bloque

### Paso 2 — Mobile private access

Revisar al final:

* En idioma fuente, el bloque access no muestra anotación.
* Si la guía cambia a otro idioma, muestra anotación:

  * EN: `provided in French/Spanish`
  * ES: `proporcionado en francés/inglés`
  * FR: `fourni en anglais/espagnol`
* El contenido privado NO se traduce.
* WiFi password, códigos, host phone y private access no se mandan a OpenAI.
* El cambio solo ocurre en rutas Worker con token.

---

### Bloque A — Printable / traducción / pets

Revisar al final:

* Printable siempre genera:

  * English
  * Español
  * Français
* Si el formulario se llenó en French:

  * English se traduce a inglés;
  * Español se traduce a español;
  * Français usa fuente limpia.
* Si el formulario se llenó en English:

  * English usa fuente;
  * Español y Français se traducen.
* Si el formulario se llenó en Spanish:

  * Español usa fuente;
  * English y Français se traducen.
* `pet_friendly` aparece localizado:

  * English: Yes / No
  * Español: Sí / No
  * Français: Oui / Non
* `pet_rules` aparece en los 3 idiomas.
* House rules se ve como bloque limpio.
* Recommendations sin Google Places muestran solo nombres.
* No aparece `Open map`.
* No hay links clickeables de Google Maps en recomendaciones.
* No se usa query param de Google Maps como dirección falsa.
* HTML público no contiene privados reales.

---

### Bloque B — Corrections + one-time

Revisar al final:

* Email final contiene botón `Request corrections`.
* Link de correcciones abre `/correct/<slug>?token=...`.
* Formulario `Ek6EM2` abre prellenado con:

  * slug;
  * correction\_token;
  * customer\_email;
  * form\_type=corrections.
* Al enviar corrección:

  * Worker marca `used:true`;
  * llega email interno a MyGuest/Vero;
  * no se regenera automáticamente guía si no está diseñado para eso.
* Segundo intento:

  * bloqueado;
  * muestra mensaje de contactar por email.
* Cortesía real solo se usa una vez.
* Email de Vero puede reutilizar para pruebas.
* Email mismatch bloquea.
* Pago/order\_id no se puede reutilizar.

---

## Pendientes específicos Bloque B

### Variables / Secrets a confirmar

Estado verificado con `wrangler secret list` (solo nombres, sin valores):

| Variable | Tipo | Estado |
|---|---|---|
| `ALERT_EMAIL` | secret | ✅ Presente |
| `GITHUB_TOKEN` | secret | ✅ Presente |
| `NOTIFY_SECRET` | secret | ✅ Presente |
| `RESEND_API_KEY` | secret | ✅ Presente |
| `STRIPE_WEBHOOK_SECRET` | secret | ✅ Presente |
| `TALLY_SIGNING_SECRET` | secret | ✅ Presente |
| `STRIPE_SECRET_KEY` | secret | ⚠️ No encontrado — verificar si el Worker lo necesita |
| `TALLY_FORM_URL` | var | ❌ Faltante — requerido por `handleStripeWebhook` para enviar link de formulario al cliente |

Variables de entorno en `wrangler.toml` (no secretas):

* `GITHUB_REPO` = `yuyitov/MyGuest` ✅
* `FROM_EMAIL` = `MyGuest <hello@myguestguide.com>` ✅
* `PUBLIC_BOOK_BASE_URL` = `https://myguestguide.com` ✅

**Acción requerida antes de pago real**: configurar `TALLY_FORM_URL` como variable de entorno en Cloudflare Worker (Dashboard → Workers & Pages → myguest-worker → Settings → Variables and Secrets → Add variable). Valor: URL del formulario principal de Tally con el `order_id` y `customer_email` como parámetros de entrada (ej: `https://tally.so/r/MedpvA`).

**Sobre `STRIPE_SECRET_KEY`**: el Worker actual no usa Stripe SDK — valida firmas HMAC con `STRIPE_WEBHOOK_SECRET`. `STRIPE_SECRET_KEY` no parece ser necesario para el Worker. Confirmar que no hay código que lo requiera antes de conectar Stripe real.

---

### Corrections one-time

Confirmado en código (`handleCorrectionAccess`, `handleCorrectionsSubmission`):

* El link **no se consume al abrirse** — `used:true` solo ocurre cuando Tally envía el webhook.
* Segundo intento: la página de error muestra *"You've already used your included correction request."* antes de que el formulario sea alcanzable.
* El webhook de Tally es idempotente si llega duplicado.
* El email interno a Vero incluye los campos rellenados (Welcome message, Property details, House rules, Recommendations, Anything else).

Confirmar en QA final:

* Abrir el link de correcciones no consume el token.
* Formulario `Ek6EM2` llega prellenado con los 4 campos (`slug`, `correction_token`, `customer_email`, `form_type`).
* Enviar el formulario marca `used:true` en KV (`correction:{slug}`).
* Segundo intento en navegador muestra página de error, no el formulario.
* Email interno llega a `ALERT_EMAIL` con el contenido correcto.

---

### Cortesías MVP

No existe una entidad "cortesía" en el código. No hay endpoint, coupon code ni bypass.

Para MVP, una cortesía se maneja como un `order:{id}` creado manualmente en KV con `status: 'paid'`, por Vero/operadora. El Worker lo valida igual que un pago real de Stripe.

**Lifecycle obligatorio** (idéntico al pago real):

```
paid → submitted → generation_dispatched → delivered
```

Una vez que el order sale de `paid`, no puede reutilizarse para otra guía.

**Restricciones para cortesías MVP**:

* No inventar un endpoint de cortesías ahora.
* No crear cortesías reusables.
* No usar páginas públicas para generar cortesías.
* No dar cortesías sin registrar el record en KV primero.

**Comando para crear cortesía manual** (documentar antes de primera venta):

```bash
npx wrangler kv key put "order:{ID_UNICO}" \
  '{"payment_intent_id":"{ID_UNICO}","customer_email":"{EMAIL_CLIENTE}","email":"{EMAIL_CLIENTE}","amount":0,"currency":"usd","stripe_event_type":"courtesy","status":"paid","created_at":"{ISO_DATE}"}' \
  --binding MYGUEST_KV --remote
```

Luego enviar al cliente el link de Tally con `order_id={ID_UNICO}&customer_email={EMAIL_CLIENTE}`.

**Pendiente**: definir el formato del `{ID_UNICO}` para cortesías (sugerencia: `courtesy-{slug}-{fecha}` para identificarlas fácilmente en KV).

---

### Email mismatch — gap documentado

El check de email mismatch en `handleTallyWebhook` (líneas 212–224) tiene la condición:

```js
if (formEmail && orderEmail && formEmail !== orderEmail)
```

Si `customer_email` no llega en el form o el order record no tiene email → **la comparación no se ejecuta** y el bloqueo no ocurre.

Confirmar en QA final:

* Que el hidden field `customer_email` de Tally (`MedpvA`) siempre envía el valor pre-llenado en el webhook.
* Que el order record en KV siempre tiene `customer_email` (viene de Stripe o del comando manual de cortesía).
* Si QA detecta que puede faltar, abrir fix para endurecer la validación (requerir email en ambos lados antes de continuar).

---

### Paid / order\_id one-time

Confirmado en código:

* **Status permitidos para generar**: `paid`, `form_sent`, `failed_dispatch`.
* **`failed_dispatch`** permite reintento si el dispatch a GitHub falló.
* **Después de dispatch exitoso**: status avanza a `generation_dispatched` → ya no está en la allowlist → bloqueado.
* **Después de email enviado**: status avanza a `delivered` → también bloqueado.
* **Excepción de Vero** (`veronica.perezarroyo@gmail.com`): solo bypasea el check de status. No bypasea: order inexistente en KV, email mismatch, ni campos requeridos faltantes.

Confirmar en QA final:

* Que un order reutilizado bloquea con `{ status: 'invalid_order_status' }`.
* Que email mismatch bloquea con `{ status: 'order_email_mismatch' }`.
* Que Vero puede reutilizar un order en `submitted` para re-prueba (si quedó bloqueado en fallo).
* Que Vero no puede inventar un `order_id` que no existe en KV.

---

### Bloque C — Pago real

Revisar al final:

* Pago real aprobado en Stripe.
* Tally recibe `order_id`.
* Worker valida que el pago esté completo.
* Si el pago no está completo, bloquea.
* Si el pago ya fue usado, bloquea.
* Si el email no coincide, bloquea.
* Si todo coincide, genera guía.
* Email final llega.
* No se puede reutilizar el mismo pago para otra guía.

---

## Resultado prueba Stripe test mode — 2026-06-26

Estado: ✅ Exitosa end-to-end.

### Flujo validado

* Stripe test Payment Link cobró con tarjeta de prueba.
* Evento procesado: `checkout.session.completed`.
* `payment_intent.succeeded` fue removido del webhook test porque llegaba sin email.
* Worker creó `order:{paymentIntentId}` con:

  * status `paid`;
  * customer\_email correcto;
  * email correcto;
  * amount `10000`;
  * currency `mxn`.
* Worker envió email post-pago con link a Tally:

  * `order_id`;
  * `customer_email`.
* Tally abrió con hidden fields correctos.
* Tally webhook pasó guards:

  * no `missing_order_id`;
  * no `invalid_order_id`;
  * no `order_email_mismatch`;
  * no `invalid_order_status`.
* GitHub Actions generó la guía (run `28218298459` — success).
* GitHub Pages publicó la villa (run `28218310922` — commit `6e763bd`).
* `/notify` fue llamado.
* Worker envió email final con Open digital guide, Open printable guide, Request corrections.
* Correction token fue creado.
* Order terminó en status `delivered`.

### Datos de prueba documentados

| Campo | Valor |
|---|---|
| PaymentIntentId | `pi_3TmRf9G4Nw60erBP0ODPa4Ww` |
| Slug | `casa-stripe-test-c-yxvm7r0` |
| Generator run | `28218298459` |
| Pages deploy run | `28218310922` |
| Commit generado por Actions | `6e763bd` |

### Lección aprendida — webhook events

Para Payment Links de Stripe Checkout, suscribir el webhook **solo a `checkout.session.completed`**. El evento `payment_intent.succeeded` no incluye el email del comprador y, al llegar primero, sella la idempotencia antes de que el evento con email pueda procesarse.

---

## Pendiente antes de producción live

* Crear/confirmar webhook Stripe LIVE.
* Dejar webhook live solo con:

  * `checkout.session.completed`
* Configurar `STRIPE_WEBHOOK_SECRET` en Cloudflare con el signing secret del endpoint **live** antes de ventas reales.
* Crear producto/precio live.
* Crear Payment Link live.
* Confirmar que el checkout live captura email del comprador.
* Hacer prueba real con pago real solo cuando se apruebe.
* No usar el secret de TEST en producción live.
* No usar Payment Link TEST para clientes reales.

---

### Bloque E — Tally + emails

Revisar al final:

* Formulario principal `MedpvA` tiene campos obligatorios correctos.
* Hidden fields funcionan:

  * customer\_email;
  * order\_id;
  * form\_type.
* Campos de pets aparecen o se usan correctamente.
* Instrucciones del formulario son claras.
* Email final tiene:

  * Open digital guide;
  * Open printable guide;
  * Request corrections;
  * aviso de privacidad de links.
* Email interno de correcciones es claro.
* No hay textos ambiguos o de prueba en emails de producción.

---

## Resultado Bloque E — Tally + emails

Estado: ✅ Cerrado técnicamente, pendiente QA final.

### Tally `MedpvA`

* Hidden fields revisados y limpiados manualmente:

  * `order_id`
  * `customer_email`
  * `form_type`
* Se eliminaron duplicados de hidden fields.
* Se corrigió etiqueta visible `6.additional_notes` a `Additional notes`.
* Webhook esperado:
  `https://myguest-worker.veronica-perezarroyo.workers.dev/tally-webhook`
* Signing secret actualizado con el nuevo `TALLY_SIGNING_SECRET`.

### Tally `Ek6EM2`

* Hidden fields confirmados:

  * `slug`
  * `correction_token`
  * `customer_email`
  * `form_type`
* Texto introductorio actualizado para aclarar:

  * una ronda gratuita incluida;
  * correcciones adicionales pueden tener costo;
  * revisión manual;
  * no prometer regeneración instantánea.
* Webhook esperado:
  `https://myguest-worker.veronica-perezarroyo.workers.dev/tally-webhook`
* Signing secret actualizado con el mismo `TALLY_SIGNING_SECRET`.

### `TALLY_SIGNING_SECRET`

* Rotado manualmente.
* Mismo valor configurado en:

  * `MedpvA`;
  * `Ek6EM2`;
  * Cloudflare Worker secret `TALLY_SIGNING_SECRET`.
* Nueva versión Worker por rotación:
  `256cddd1-bf81-4c26-9cbf-4e856593ae74`

### Emails

* Commit de copy: `51ec093`
* Worker deploy: `18558930-85ec-4060-bec1-71bb93badd48`
* Cambios aplicados:

  * email post-pago ahora aclara que el link es personal y ligado a la compra;
  * email final aclara que el digital guide es para compartir con huéspedes;
  * printable guide se aclara como versión para host, para imprimir o guardar PDF;
  * correcciones se aclaran como revisión manual sin prometer regeneración instantánea;
  * email interno de correcciones incluye link público a la guía:
    `https://myguestguide.com/villas/{slug}/en.html`
* No se cambiaron:

  * tokens;
  * rutas;
  * guards;
  * Stripe;
  * Tally logic;
  * KV;
  * GitHub Actions;
  * PDF/printable.

### `TALLY_FORM_URL`

* Se restauró como var local en `worker/wrangler.toml`:
  `TALLY_FORM_URL = "https://tally.so/r/MedpvA"`
* `worker/wrangler.toml` está ignorado por `.gitignore`, no se commitea.
* Deploy con `TALLY_FORM_URL` activo:
  `5e1f0893-5aa2-40b0-97ed-fbe92858d858`
* **Nota operativa:** si se despliega desde otra máquina, esta variable debe existir
  en el `wrangler.toml` local o en Cloudflare Dashboard antes del deploy, de lo
  contrario el deploy la eliminaría del Worker.

### Pendiente QA final Bloque E

* Confirmar que `MedpvA` sigue enviando Tally webhook correctamente después de la rotación del signing secret.
* Confirmar que `Ek6EM2` envía correcciones correctamente.
* Confirmar visualmente los nuevos textos de emails en una corrida de QA final.
* Confirmar que `STRIPE_WEBHOOK_SECRET` se cambie de TEST a LIVE antes de venta real.

---

### Bloque D — Seguridad final

Revisar al final:

* GitHub Pages público NO contiene:

  * WiFi password;
  * door code;
  * lockbox code;
  * access code;
  * host phone;
  * private access details;
  * guest access token;
  * correction token.
* Revisar:

  * `public/villas/*/en.html`
  * `public/villas/*/es.html`
  * `public/villas/*/fr.html`
  * `public/villas/*/index.html`
  * `public/villas/*/print.html`
  * `public/villas/*/print.pdf`
* No marcar como fallo nombres técnicos JS tipo:

  * `d.wifi_password`
  * `house_access_private`
  * `private_access`
* Sí marcar como fallo valores reales.
* Confirmar que privados solo aparecen vía Worker con token.

---

## Resultado Bloque D — Seguridad final

Estado: ✅ Limpio. Sin hallazgos críticos ni altos.

### GitHub Pages público

* No se encontraron datos privados reales en:

  * `public/villas/*/en.html`
  * `public/villas/*/es.html`
  * `public/villas/*/fr.html`
  * `public/villas/*/index.html`
  * `public/villas/*/print.html`
  * `public/villas/*/print.pdf`
* No se encontraron valores privados dummy usados en pruebas:

  * `TEST_PASSWORD_123`
  * `TEST_CODE_1234`
  * `TEST_WIFI_MY_GUEST`
  * `+52 322 000 0000`
* No se encontraron tokens reales de guest/corrections en páginas públicas.
* Solo aparecen referencias técnicas JS como:

  * `d.wifi_password`
  * `d.house_access_private`
  * `d.host_phone`
  * template literal `token=${...}`
* Esas referencias son aceptables porque no contienen valores reales.

### Printable / PDF público

* `print.html` público contiene placeholders vacíos para inyección por Worker.
* `print.pdf` público fue generado solo con payload público.
* No hay WiFi/password/códigos/teléfono/private access en PDF público.
* Los privados del printable solo deben aparecer vía:
  `/print/{slug}?token=...`

### Demos oficiales

Mantener estas demos:

* `ocean-drive-retreat`
* `the-soho-loft`
* `casa-selva-tulum`
* `le-marais-flat`

Nota: Las credenciales que aparecen en demos oficiales son ficticias y aceptadas como `demo_mode`.

### Secrets en repo

No se encontraron valores reales de:

* `whsec_`
* `sk_live_`
* `sk_test_`
* `rk_live_`
* `rk_test_`
* Resend API keys
* `NOTIFY_SECRET`
* `TALLY_SIGNING_SECRET`
* `GITHUB_TOKEN`
* guest tokens
* correction tokens

Solo hay referencias a nombres de variables `env.*`, lo cual es correcto.

### Gap funcional no bloqueante

Se detectó que algunas villas de prueba antiguas tienen formatos de placeholder `print.html` distintos:

* `private-house-print-block-en/es/fr` — formato actual, Worker inyecta correctamente
* `private-house-print-block` (sin sufijo) — formato antiguo, Worker NO inyecta
* `private-phone-contact-block` — formato diferente en `casa-stripe-test-c-yxvm7r0`, Worker NO inyecta

Impacto:

* No es riesgo de seguridad — los placeholders están vacíos en GitHub Pages.
* Puede causar que villas antiguas no muestren privados en printable con token.
* Se resuelve limpiando esas villas en Bloque F o agregando compatibilidad posterior.

### Villas de prueba pendientes de limpieza en Bloque F

| Slug | Tipo |
|---|---|
| `casa-stripe-test-c-yxvm7r0` | Prueba Stripe end-to-end |
| `maison-mar-serena-test-a-0vvvveq` | Prueba multilingüe |
| `casa-mar-serena-qorqzox` | Prueba |
| `casa-mar-serena-dq18xql` | Prueba |
| `casa-mar-serena-m1olz20` | Prueba |
| `casa-mar-serena-jemxyk9` | Prueba |
| `maison-mar-serena-gbaea4l` | Prueba multilingüe |
| `hmac-test-no-entregar-zezdgrg` | Test HMAC — explícitamente marcado |
| `casa-sin-adjuntos-final-no-entregar-nqv9plw` | Test adjuntos |
| `casa-cortesia-sin-adjuntos-1wkbjko` | Prueba cortesía |
| `test-sin-adjuntos-arj9ekd` | Prueba |

### Conclusión

* Bloque D queda limpio en seguridad.
* No hay datos privados ni tokens válidos expuestos en GitHub Pages.
* No hay secrets de infraestructura en el repo.
* La limpieza de villas de prueba pasa a Bloque F.
* El gap de placeholders print antiguos es funcional, no de seguridad.

---

### Bloque F — Limpieza + documentación final

Revisar al final:

* Limpiar KV de pruebas:

  * `subm-*`
  * `delivery:*`
  * `priv-*`
  * `correction:*`
* Limpiar villas de prueba:

  * `public/villas/casa-mar-serena-*`
  * `public/villas/maison-mar-serena-*`
  * slugs con `test`, `no-entregar`, `hmac-test`, etc.
* No borrar demos oficiales:

  * `ocean-drive-retreat`
  * `the-soho-loft`
  * `casa-selva-tulum`
  * `le-marais-flat`
* Documentar operación:

  * cómo vender;
  * cómo generar link de Tally con email/order\_id;
  * cómo revisar GitHub Actions;
  * cómo revisar KV;
  * cómo reenviar o investigar fallos;
  * cómo limpiar pruebas;
  * qué datos nunca van a GitHub Pages.

---

## Resultado Bloque F — Limpieza final

Estado: ✅ F-02 y F-03 completados. Pendiente activar Stripe LIVE antes de venta real.

### F-02 — Limpieza pública

* Commit: `12a74fb`
* GitHub Pages run: `28269927211`
* Resultado:

  * 11 carpetas de prueba eliminadas de `public/villas/`;
  * 66 archivos eliminados;
  * GitHub Pages deploy terminó `success`;
  * las carpetas ya no están publicadas en `myguestguide.com/villas/`.
* Demos oficiales mantenidas:

  * `ocean-drive-retreat`
  * `the-soho-loft`
  * `casa-selva-tulum`
  * `le-marais-flat`

### F-03 — Limpieza KV

* Manifest esperado: 30 keys.
* Existentes antes de borrar: 29.
* Saltadas por `NOT FOUND`: 1 (`processed:pi_3TmRf9G4Nw60erBP0ODPa4Ww` — ya no existía).
* Borradas: 29.
* Verificación post-borrado: 29/29 `GONE`.
* `Still exists`: 0.
* No se borró nada fuera del manifest.
* Demos no tocados.
* Worker, Cloudflare secrets, Stripe, Tally y archivos no tocados.

### Estado final de limpieza

* GitHub Pages público queda sin villas de prueba.
* KV queda sin registros de pruebas documentadas.
* Demos oficiales permanecen.
* Repo queda sin modificaciones tracked después de commits.
* Persisten untracked locales conocidos, diferidos para revisión separada:

  * `books/scripts/_regen_print_only.py`
  * `package-lock.json`
  * `public/landing/Identidad Visual/Logos/...`
  * `public/landing/Identidad Visual/Mascota/`
  * `worker/C...Tempprint_test.html`

### Pendiente antes de producción real

⚠️ **No vender hasta completar esta fase:**

* `STRIPE_WEBHOOK_SECRET` sigue en TEST — no válido para ventas reales.
* Falta configurar Stripe LIVE:

  * crear webhook LIVE solo con `checkout.session.completed`;
  * actualizar `STRIPE_WEBHOOK_SECRET` en Cloudflare con el signing secret LIVE;
  * crear producto/precio/payment link LIVE;
  * hacer prueba controlada con venta real aprobada.

---

---

## Resultado G-02C — Prueba end-to-end TEST limpia

**Fecha:** 2026-06-27
**Estado:** ✅ Cerrada y limpia. Ver reporte completo en `docs/G02C_CLEAN_TEST_REPORT.md`.

### Resumen ejecutivo

| Paso | Resultado |
|---|---|
| Pago Stripe TEST | ✅ Procesado |
| Email post-pago | ✅ Recibido con link Tally + hidden fields |
| Tally MedpvA enviado | ✅ Sin adjuntos, datos ficticios |
| GitHub Actions generator `28276098824` | ✅ success (2m17s) |
| GitHub Pages deploy `28276151599` | ✅ success (24s) |
| 6 archivos generados (en/es/fr/index/print.html/print.pdf) | ✅ HTTP 200 |
| Email final | ✅ Recibido con 3 links |
| Guest link con token → privados visibles | ✅ |
| Print link con token → privados inyectados | ✅ |
| Correction link → Ek6EM2 con pre-fill 4 campos | ✅ |
| Guest link sin token → no expone privados | ✅ |
| Auditoría pública anti-fuga | ✅ Limpia |

### Bug corregido en esta prueba

Bug `provided in English` en vista EN sin `?lang=`:

* Commit: `52a2691 Fix private access language annotation in default guest view`
* Worker deploy: `5b7b680f-035f-4ee0-9e8e-2ad6229827b5`
* Fix: `effectiveLang = lang || 'en'` en `injectPrivateDetailsIntoBookHtml`

### Limpieza

* Commit: `8e25c2d Remove G-02C test villa pages`
* Pages run: `28306308278` — ✅ success
* KV: 4 keys deleted, 5/5 GONE

### Pendiente derivado

* G-02D: prueba con uploads/fotos — diferida para antes de primera venta con adjuntos.

---

## Pruebas finales pendientes

Dejar anotadas estas pruebas para el cierre final:

### Prueba 1 — French + pets

* Primary language: French
* Pet friendly: Yes
* Pet rules lleno
* Sin adjuntos

### Prueba 2 — English + no pets

* Primary language: English
* Pet friendly: No
* Sin adjuntos

### Prueba 3 — Corrections one-time

* Abrir correction link.
* Enviar una corrección.
* Confirmar `used:true`.
* Intentar segundo uso y confirmar bloqueo.

### Prueba 4 — Cortesía one-time

* Usar cortesía válida.
* Intentar reutilizarla con cliente real.
* Confirmar bloqueo.
* Confirmar excepción de email de Vero si aplica.

### Prueba 5 — Pago real

* Pagar.
* Generar guía.
* Intentar reutilizar order\_id.
* Confirmar bloqueo.

### Prueba 6 — Seguridad final

* Escanear HTML público y PDF público.
* Confirmar que no hay privados reales.
