# G-01 — Pre-live Audit Report

**Fecha:** 2026-06-26
**Estado general:** `READY FOR LIVE — PENDING STRIPE LIVE ACTIVATION`

El producto está técnicamente funcional. Stripe LIVE no debe activarse todavía porque existen pendientes bloqueadores en producto, seguridad, pricing y marketing.

## Últimos commits relevantes

| Commit | Descripción |
|---|---|
| `bcd0941` | Add F-04 cleanup docs and operations runbook |
| `12a74fb` | Remove test villa pages from public |
| `67b3d2d` | Document Bloque D security audit results in QA checklist |
| `380fd65` | Document Bloque E results in QA checklist |
| `51ec093` | Improve MyGuest email copy |

---

## Separación de áreas

### Producto

Cubre el flujo técnico completo: Stripe checkout/webhook → Tally → Worker → GitHub Actions → GitHub Pages → emails → correcciones → privacidad de datos → soporte → T&C → primera venta real.

### Marketing

Cubre lo que es externo al flujo de entrega: landing page, identidad visual, mockups, Instagram, Pinterest, ads, analytics/pixels, UTM, CRM/email funnel, automatización de publicación, campañas, demos y cortesías como herramienta de adquisición.

### Seguridad

Cubre las capas de protección técnica y operativa: secrets, Cloudflare KV, tokens, webhooks, GitHub, Tally, Resend, XSS, logs, archivos subidos, retención de datos, bypasses de prueba, control de órdenes gratis y descuentos.

---

## Tabla 1 — Producto

| Área | Estado | Falta | Prioridad | Acción recomendada |
|---|---|---|---|---|
| **Stripe webhook** | ⚠️ TEST | `STRIPE_WEBHOOK_SECRET` en TEST — no válido para cobros reales | **Bloqueador** | Crear webhook LIVE en Stripe; actualizar secret en Cloudflare en G-06 |
| **Payment Link en landing** | ⚠️ TEST | `buy.stripe.com/00wcN5fvo5hQfcuaL8ffy00` es Payment Link TEST | **Bloqueador** | Crear producto + Payment Link LIVE; actualizar `index.html` en G-06 |
| **Términos / Reembolsos** | ❌ Ausente | Landing no tiene T&C ni política de reembolso | **Bloqueador** | Stripe puede suspender cuentas sin T&C visibles; agregar en G-02 |
| **`NOTIFY_SECRET`** | ⚠️ Sin rotar | CLAUDE.md indica rotación pendiente desde sesión anterior | **Bloqueador** | Rotar antes de LIVE (mínimo 32 bytes aleatorios) en G-04 |
| **`isVeroTest` bypass** | ⚠️ Hardcodeado | Email `veronica.perezarroyo@gmail.com` omite validación de `order_id` y status en producción; visible en código fuente público del repo | **Bloqueador** | Decidir: eliminar o convertir en env flag en G-04 |
| **Prueba end-to-end TEST** | ❌ Pendiente | No se completó una prueba completa Stripe TEST → Tally → Worker → Pages → email desde cero | **Bloqueador** | Correr en G-02 antes de activar LIVE |
| **Tally MedpvA** | ✅ Activo | — | — | Verificar que webhook apunta a URL Worker correcta antes de LIVE |
| **Tally Ek6EM2 (correcciones)** | ✅ Activo | Pre-fill pendiente verificar en navegador real | Media | Prueba visual antes de LIVE en G-02 |
| **Worker** | ✅ Desplegado (`5e1f0893`) | Ver `NOTIFY_SECRET` arriba | — | — |
| **GitHub Actions** | ✅ Funcional | Node.js 20 deprecation (deadline sept. 2026) | Post-LIVE | Actualizar actions a versiones con Node 24 |
| **GitHub Pages** | ✅ Limpio | Solo 4 demos oficiales publicadas | — | — |
| **Email post-pago** | ✅ Funcional | — | — | — |
| **Email delivery** | ✅ Funcional | — | — | — |
| **Email correcciones (alerta interna)** | ✅ Funcional | — | — | — |
| **Correcciones flow (token single-use)** | ✅ Implementado | Pre-fill Ek6EM2 sin verificar en navegador | Media | G-02 |
| **Email mismatch** | ⚠️ Gap documentado | Si `customer_email` falta en form o en KV, la comparación no se ejecuta | Media | Confirmar en QA que hidden field siempre llega; documentar procedimiento de soporte para mismatch |
| **Privacidad de datos en Pages** | ✅ Correcto | Bloque D validó — ningún dato sensible en HTML público | — | — |
| **Retención de datos en KV** | ⚠️ Sin definir | Sin TTL en `priv-{slug}`, `delivery:{slug}` — datos permanecen indefinidamente | Post-LIVE | Definir política de retención (ej. 12 meses) y TTL o proceso de borrado |
| **Soporte** | ⚠️ Informal | Solo "reply to this email" — sin SLA documentado | Pre-LIVE | Definir tiempo de respuesta mínimo y horario en G-02 |

---

## Tabla 2 — Marketing

> ⚠️ **Marketing debe mantenerse separado del producto.** No activar anuncios pagados hasta resolver: Payment Link LIVE, T&C, tracking mínimo y landing revisada.

| Elemento | Ubicación | Estado | Falta | Acción recomendada |
|---|---|---|---|---|
| **Landing page** | `public/index.html` | ✅ Publicada en `myguestguide.com` | Payment Link TEST activo; sin T&C | Actualizar a link LIVE y agregar T&C antes de anuncios |
| **OG / social meta tags** | `public/index.html` | ✅ Presentes | — | Verificar preview en social antes de publicar anuncios |
| **Logos (committedos)** | `public/landing/Identidad Visual/Logos/` | ✅ En repo | 1 imagen Gemini sin commitear | Decidir si commitear o descartar en G-05 |
| **Mascota** | `public/landing/Identidad Visual/Mascota/` | ⚠️ Untracked | `mascota_cel-Photoroom.png` sin commitear | Decidir uso en landing y commitear en G-05 |
| **Identity System PDF** | `public/landing/Identidad Visual/Myguest Visual Identity System Master Document.pdf` | ✅ En repo | — | Solo referencia interna — no exponer directamente |
| **Mockups de celular** | `public/landing/Mockups/` | ✅ Committedos (4 PNGs + source HTML) | — | Disponibles para landing o publicidad |
| **Instagram templates** | `marketing/instagram/templates/` | ✅ 9 templates listos | — | Completados |
| **Instagram exports** | `marketing/instagram/exports/` | ✅ 10 PNGs exportados | — | Listos para publicar manualmente |
| **Instagram publish.py** | `marketing/instagram/scripts/publish.py` | ⚠️ Sin verificar | Desconocido si está en uso o es borrador | Auditar antes de activar cualquier automatización en G-05 |
| **Instagram posts en `public/instagram/`** | `public/instagram/` | ✅ En Pages | Publicadas sin página índice — no rompe nada | No urgente |
| **Pinterest QA samples** | `marketing/pinterest/output/qa-sample/` | ✅ 8 PNGs generados | Aprobación visual de Vero pendiente | Revisar en G-05 antes de continuar con los 32 pins finales |
| **Pinterest 32 pins finales** | `marketing/pinterest/output/pins/` | ⚠️ Solo 2 renderizados | 30 pendientes | No renderizar hasta aprobación de QA samples |
| **Pinterest Lote 01 (publicado)** | `marketing/pinterest/pins/Pin-01/` | ✅ 20 pins generados | Seguimiento en Excel | Continuar workflow semanal de ChatGPT |
| **Pinterest templates v2** | `marketing/pinterest/templates/` | ✅ 8 templates | Pendiente aprobación visual | No usar hasta aprobar QA samples |
| **Sales materials** | `marketing/assets/` | ✅ PDF + DOCX | — | Solo referencia interna |
| **Analytics / pixel** | Ninguna | ❌ Ausente | Sin Google Analytics, Meta Pixel, UTM, tracker de ningún tipo | Decidir si agregar antes de anuncios pagados en G-05 |
| **CRM / email funnel** | Ninguna | ❌ Ausente | Sin captura de leads ni secuencia de emails | Post-LIVE; no es bloqueador para primera venta |
| **Automatización de publicación** | `marketing/instagram/scripts/publish.py` | ⚠️ No verificado | — | Auditar en G-05 antes de activar |

---

## Tabla 3 — Seguridad

> Pre-live obligatorio marcado como **Bloqueador**.

| Amenaza | Impacto | Protección actual | Gap | Prioridad | Acción recomendada |
|---|---|---|---|---|---|
| **`NOTIFY_SECRET` sin rotar** | Alto | Protege endpoint `/notify` llamado por `pages.yml` | Rotación documentada como pendiente en CLAUDE.md | **Bloqueador** | Rotar en G-04 (mínimo 32 bytes aleatorios); actualizar en GitHub Actions Secrets y Cloudflare |
| **`isVeroTest` hardcodeado** | Medio | Email `veronica.perezarroyo@gmail.com` omite validación de `order_id` y status | Email visible en código fuente público del repo | **Bloqueador** | G-04: eliminar o mover a env flag en Cloudflare; no usar como mecanismo de cortesías |
| **Verificación 2FA en cuentas críticas** | Crítico | Recomendado en CLAUDE.md | No confirmado activo en Cloudflare, GitHub, Stripe, Tally, Resend, dominio | **Pre-LIVE** | G-04: verificar y activar 2FA en todas las cuentas críticas antes de cobros reales |
| **DKIM / SPF de Resend** | Alto | `hello@myguestguide.com` en Resend | No verificado que los registros DNS estén activos | **Pre-LIVE** | G-04: verificar en DNS que DKIM y SPF de Resend están publicados |
| **Robo de secrets (Cloudflare)** | Crítico | Secrets en Cloudflare; `wrangler.toml` en `.gitignore` | Dependencia total de la cuenta Cloudflare; 2FA no confirmado | Alta | G-04: confirmar 2FA en Cloudflare; revisar permisos de API tokens |
| **`GITHUB_TOKEN` scope excesivo** | Medio | Token en Cloudflare secrets; solo dispara `repository_dispatch` | No verificado que el scope sea mínimo | Alta | G-04: revisar que el token tenga scope mínimo (solo `contents:write` o `actions:write`); sin acceso a settings ni secrets |
| **Acceso a Cloudflare KV** | Crítico | Solo el Worker tiene binding a MYGUEST_KV; no expuesto públicamente | Dependencia total de la cuenta Cloudflare | Alta | G-04: confirmar 2FA y permisos de API tokens |
| **Tokens guest/print/correction sin expiración** | Medio | 32 bytes aleatorios; `cache-control: no-store`; no en código público | Sin TTL — un token sigue válido indefinidamente | Media | Post-LIVE: definir TTL para tokens; considerar revocación de clientes pasados |
| **Email mismatch — comparación omitida** | Medio | Bloqueo si ambos emails están presentes y son distintos | Si `customer_email` falta en form o en KV, el bloqueo no se ejecuta | Media | G-04: confirmar que hidden field Tally siempre envía valor; documentar procedimiento de soporte |
| **Webhooks Tally falsos** | Alto | HMAC-SHA256 con `TALLY_SIGNING_SECRET` | Mismo secret para MedpvA y Ek6EM2 — si se filtra, ambos forms quedan expuestos | Media | Post-LIVE: considerar secrets distintos por form; por ahora documentar como riesgo aceptado |
| **Webhooks Stripe falsos** | Alto | `STRIPE_WEBHOOK_SECRET` validado | En TEST — valor LIVE diferente, requiere rotación controlada | Alta | G-06: único secret LIVE configurado al activar modo producción |
| **Una compra → múltiples books** | Medio | `order:{pi}` guarda status; solo `paid/form_sent/failed_dispatch` permiten generar | `isVeroTest` bypass en producción puede omitir esa validación | Media | G-04: al eliminar `isVeroTest`, la validación queda completa |
| **Logs con datos privados** | Bajo | Solo 3 `console.log` — ninguno imprime WiFi/codes/tokens | Imprime `slug` y `ALERT_EMAIL` destino — no sensibles | Baja | Mantener vigilancia en futuras modificaciones; no acción inmediata |
| **XSS / inyección desde campos del cliente** | Medio | `escapeHtml()` y `escapeAttribute()` en todos los campos privados del Worker | — | Baja | Mantener; nunca usar `innerHTML` con datos de usuario |
| **Archivos subidos por cliente** | Medio | Trigger `needs_manual_extraction`; Vero revisa manualmente | No se valida tipo MIME en la recepción del Worker actual | Post-LIVE | Agregar validación de extensión/MIME antes de aceptar adjuntos |
| **Retención de datos privados en KV** | Medio | Sin TTL en `priv-{slug}` ni `delivery:{slug}` | Datos permanecen en KV indefinidamente | Post-LIVE | Definir política de retención (ej. 12 meses) y proceso de borrado |
| **Stripe dashboard / cuenta bancaria** | Crítico | Protección de la cuenta Stripe | 2FA no confirmado; payout account no revisado | Alta | G-04: verificar 2FA en Stripe; revisar payout account; sin usuarios compartidos |
| **Tally account comprometida** | Alto | Acceso solo para Vero | 2FA no confirmado en Tally | Alta | G-04: activar 2FA en Tally |
| **GitHub Pages expone datos privados** | Crítico | Validado en Bloque D — ningún dato sensible en Pages | — | — | Mantener; no requiere acción adicional |

---

## Tabla 4 — Pricing, descuentos, demos gratis y cortesías

### Hallazgos en el repo

| Elemento | Estado actual | Riesgo | Decisión pendiente | Acción recomendada |
|---|---|---|---|---|
| **Precio en landing** | `$29 USD` en `public/index.html` — en EN, ES, FR | ✅ Consistente | Confirmar que Price en Stripe TEST también es `$29` y que LIVE será el mismo | Verificar antes de G-06 |
| **Etiqueta de precio** | "Launch price" / "Precio de lanzamiento" en landing | ✅ Correcto para MVP | Definir cuándo sube el precio y qué se cambiará en la landing | Documentar en G-03 |
| **Payment Link en landing** | `buy.stripe.com/00wcN5fvo5hQfcuaL8ffy00` (TEST) | ⚠️ TEST activo | Reemplazar por LIVE en G-06 | No cambiar hasta G-06 |
| **Precio en Worker** | No existe lógica de pricing en `worker.js` | ✅ Correcto | — | Mantener así — pricing vive en Stripe y landing, no en lógica interna |
| **Descuentos / promo codes** | No implementados en Worker ni en landing | ✅ Sin riesgo activo | Definir si se usarán en G-03 | Si se implementan, deben terminar en orden trazable; nunca abrir Tally sin `order_id` |
| **Demos gratis / `isVeroTest`** | Email `veronica.perezarroyo@gmail.com` omite `order_id` en Worker | ⚠️ No es un sistema de cortesías — es un bypass de prueba hardcodeado | Decidir si se elimina o convierte en env flag antes de LIVE | No usar como mecanismo de cortesías; diseñar flujo separado en G-03/G-04 |
| **Cortesías manuales** | Documentadas en checklist (`stripe_event_type: "courtesy"`) — comando KV manual disponible | ⚠️ Flujo sin formato `{ID_UNICO}` definido | Definir formato de ID de cortesía (sugerencia: `courtesy-{slug}-{YYYYMMDD}`) | Documentar flujo completo en G-03 |
| **`amount: 0` en cortesías** | Worker acepta `amount_total = 0` — no bloquea órdenes de monto cero | ⚠️ Cualquier orden con monto 0 puede activar el flujo | Esto es intencional para cortesías, pero debe ser controlado | Confirmar que solo Vero puede crear órdenes con `amount: 0` en KV |
| **A/B testing de precios** | No implementado | ✅ Sin riesgo | Definir estrategia en G-03 | No activar A/B antes de tener analytics mínimo |
| **Paquetes (N Airbnbs)** | No implementados | ✅ Sin riesgo activo | Definir si se ofrecerán en G-03 | Si se implementan: `1 paquete = N books autorizados`, controlado por orden |

---

### Precio introductorio

- Precio deseado: **$29 USD** (trilingual mobile guide + printable PDF).
- Landing publica `$29 USD` en EN, ES y FR.
- El Payment Link actual es TEST — pendiente verificar que el precio en Stripe también sea `$29`.
- Al crear el Payment Link LIVE en G-06, confirmar que el precio coincide con lo publicado en la landing.

### Precio futuro

- La etiqueta "Launch price / Precio de lanzamiento" anticipa un precio mayor posterior.
- El precio futuro no debe hardcodearse en el Worker — vive en Stripe y en la landing.
- Cuando suba el precio: actualizar la landing + crear un nuevo Payment Link en Stripe.

### Prueba de dos precios

- Si se prueban dos precios simultáneamente: usar dos Payment Links distintos con tracking separado (UTM diferenciado).
- Evitar mezclar datos sin UTM.
- No activar A/B testing antes de tener analytics mínimo configurado.

### Descuentos

- Los descuentos deben controlarse desde Stripe (coupon codes) o desde una orden aprobada manualmente.
- Nunca abrir Tally sin `order_id` válido — incluso con descuento del 100%.
- Cada descuento debe terminar en una orden trazable con `order:{ID}` en KV.

### Demos gratis y cortesías

**Regla:** `isVeroTest` no es un sistema de cortesías. Es un bypass de prueba. No usarlo para enviar cortesías a clientes.

**Flujo correcto para una cortesía:**

1. Vero aprueba la cortesía (quién, cuántas propiedades, motivo).
2. Crear manualmente en KV: `order:courtesy-{slug}-{YYYYMMDD}` con `amount: 0`, `stripe_event_type: courtesy`, `status: paid`.
3. Enviar el link de Tally con `order_id=courtesy-{slug}-{YYYYMMDD}&customer_email={EMAIL}`.
4. El resto del flujo es idéntico al de un pago real.

**Registro mínimo requerido para cada cortesía:**

| Campo | Descripción |
|---|---|
| `order_id` | ID en KV (`courtesy-{slug}-{YYYYMMDD}`) |
| `customer_email` | Email del receptor |
| `property_name` | Nombre de la propiedad |
| `books_authorized` | Número de books autorizados (por defecto: 1) |
| `created_at` | Fecha ISO |
| `reason` | Motivo de la cortesía |
| `used` | Si ya fue procesado |

**Pendiente definir:** formato oficial del `{ID_UNICO}` para cortesías (sugerencia: `courtesy-{slug}-{YYYYMMDD}`).

### Hosts con múltiples Airbnbs

- Un mismo cliente puede usar el mismo email para varios books.
- **Regla:** `1 pago = 1 order_id = 1 book`. El email no es el control — el `order_id` sí.
- Para paquetes futuros: `1 paquete = N books autorizados`, con cupo controlado en KV.
- Implementación sugerida para paquete: `order:{ID}` con campo `books_remaining: N`, decrementado en cada generación.

---

## Riesgos bancarios / Stripe

- MyGuest no guarda datos bancarios en el repo, Worker, Tally ni KV. ✅
- La cuenta bancaria vive solo dentro de la cuenta Stripe.
- Proteger Stripe con 2FA — **no confirmado todavía**.
- Revisar payout account antes de LIVE: confirmar que los fondos van a la cuenta correcta.
- No compartir acceso administrador de Stripe.
- No usar usuarios compartidos ni API keys de múltiples proyectos bajo la misma cuenta.
- El `STRIPE_WEBHOOK_SECRET` en Cloudflare debe ser del webhook LIVE — nunca el de TEST.

---

## Próximos bloques recomendados

### G-02 — Producto pre-live

- Agregar T&C mínimos y política de reembolso en la landing.
- Definir SLA de soporte mínimo.
- Verificar pre-fill de Ek6EM2 en navegador real.
- Correr prueba end-to-end TEST completa: pago simulado → Tally → Worker → Pages → email.
- Revisar landing sin cambiar Stripe LIVE todavía.

### G-03 — Pricing / demos / descuentos

- Confirmar precio introductorio `$29 USD` vs Stripe TEST.
- Definir si habrá precio normal posterior y cuándo.
- Definir si habrá códigos de descuento y cómo implementarlos de forma trazable.
- Definir flujo oficial de cortesías con formato de ID y registro.
- Definir si se ofrecerá paquete para hosts con múltiples Airbnbs.
- Decidir estrategia de A/B testing de precios (requiere analytics mínimo primero).

### G-04 — Security hardening

- Rotar `NOTIFY_SECRET` (mínimo 32 bytes aleatorios).
- Decidir y ejecutar la eliminación o conversión de `isVeroTest` a env flag.
- Verificar 2FA en: Cloudflare, GitHub, Stripe, Tally, Resend y dominio.
- Verificar registros DKIM/SPF de Resend en DNS.
- Revisar scope mínimo de `GITHUB_TOKEN` en Cloudflare secrets.
- Documentar procedimiento de soporte para email mismatch.
- Diseñar flujo seguro de courtesy orders si se aprueba.
- Revisar payout account en Stripe.

### G-05 — Marketing inventory

- Revisar y decidir assets untracked (mascota, logo Gemini).
- Revisar Pinterest QA samples y aprobar antes de renderizar 32 pins finales.
- Auditar `publish.py` antes de activar automatización.
- Decidir si agregar analytics (Google Analytics, Meta Pixel) y UTM antes de anuncios pagados.
- Separar claramente el ciclo de marketing del ciclo de producto.

### G-06 — Stripe LIVE activation

- Crear producto, precio y Payment Link LIVE en Stripe.
- Crear webhook LIVE solo con `checkout.session.completed`.
- Reemplazar `STRIPE_WEBHOOK_SECRET` en Cloudflare con el signing secret LIVE.
- Actualizar `public/index.html` con el Payment Link LIVE.
- Revisar payout account.
- Hacer primera venta real controlada y seguir el protocolo del runbook.

---

## Conclusión

El producto está técnicamente cerca de LIVE. No debe venderse todavía.

Los bloqueadores principales están claros:

1. Stripe en TEST — no recibe cobros reales.
2. Payment Link TEST activo en la landing.
3. T&C y política de reembolso ausentes — riesgo de suspensión de cuenta Stripe.
4. `NOTIFY_SECRET` sin rotar.
5. `isVeroTest` hardcodeado en código fuente público.
6. Prueba end-to-end TEST limpia no completada.

Marketing debe manejarse como capa completamente separada del producto. No activar anuncios pagados antes de resolver el Payment Link LIVE, los T&C y el tracking mínimo.

Pricing, descuentos y cortesías deben definirse antes de campañas. Todo book generado — pagado o de cortesía — debe ser trazable con su propio `order_id` en KV.

Seguridad requiere hardening pre-live: 2FA en todas las cuentas críticas, `NOTIFY_SECRET` rotado, `isVeroTest` eliminado o convertido en flag controlado, DKIM/SPF verificados.

Demos gratis y cortesías deben ser trazables y no deben depender de bypasses de email hardcodeados.
