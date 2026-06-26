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
