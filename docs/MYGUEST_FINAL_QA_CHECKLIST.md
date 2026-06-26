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
