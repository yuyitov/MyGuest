# MyGuest Operations Runbook

## Arquitectura aprobada

```
Tally → Cloudflare Worker → GitHub Actions → GitHub Pages
```

## Reglas de seguridad

- Nunca poner WiFi, passwords, códigos, teléfono del host ni acceso privado en GitHub Pages.
- Los privados viven en Cloudflare KV y solo se inyectan vía Worker con token.
- No traducir privados con OpenAI ni servicios externos.
- `house_access_private` debe mantenerse exactamente como lo escribió el host.
- No imprimir ni commitear secrets.

---

## Estructura de precios (estrategia 2026-07-17)

- **Precio de lista (ancla)**: $129 USD / $1,999 MXN — se muestra tachado en la landing junto al precio promocional vigente.
- **Promo vigente (2026-07-17)**: **$49 USD / $899 MXN / $69 CAD** (multi-moneda al pagar).
- **Escalera de lanzamiento** (la ejecuta Vero editando los payment links en Stripe; las URLs `buy.stripe.com` se CONSERVAN):
  1. Actual: **$49 USD** (vigente hoy; $899 MXN / $69 CAD al pagar)
  2. Sube a **$79 USD** al llegar a ~25 ventas
  3. Precio de lista: $129 USD / $1,999 MXN
- Al subir cada escalón: Vero cambia el precio en Stripe y se actualiza el número promocional en la landing (el tachado $129/$1,999 se mantiene).
- **Correcciones**: 1 ronda de correcciones gratis incluida; cada ronda adicional cuesta **$6 USD / $59 MXN**. Los payment links de cobro por corrección adicional los crea Vero en Stripe (no existen aún — no inventar URLs).
- El pricing NO vive en el Worker — solo en Stripe y en la landing.

---

## Flujo normal de venta

1. Cliente paga en Stripe.
2. Stripe webhook `checkout.session.completed` crea `order:{paymentIntentId}` en KV.
3. Cliente recibe email con link personal a Tally.
4. Cliente llena Tally.
5. Worker valida:
   - firma Tally (`TALLY_SIGNING_SECRET`);
   - `order_id` presente en submission;
   - email del formulario contra email de la orden;
   - status permitido (`paid`, `form_sent`, `failed_dispatch`).
6. Worker separa payload público (contenido de la guía) y privado (WiFi, códigos, teléfono, acceso).
7. Worker guarda privados en KV como `priv-{slug}`.
8. Worker dispara GitHub Actions (`repository_dispatch` tipo `new-villa`).
9. GitHub Actions genera guía pública en GitHub Pages (`public/villas/{slug}/`).
10. `pages.yml` llama `/notify` en el Worker.
11. Worker actualiza orden a `delivered` y envía email final con:
    - digital guide (`/guest/{slug}?token=...`);
    - printable host guide (`/print/{slug}?token=...`);
    - correction link (`/correct/{slug}?token=...`).

---

## Flujo de correcciones

- Una ronda gratuita incluida; rondas adicionales: $6 USD / $59 MXN cada una (cobro vía payment link que crea Vero en Stripe).
- Link de corrección es de un solo uso (token marcado `used: true` después del primer submit).
- Correcciones son revisión manual — no regeneración automática.
- No prometer turnaround instantáneo.
- El token de corrección vive en KV y en el email del host, nunca en GitHub Pages.
- Para aplicar correcciones: revisar email interno de alerta → editar datos → `repository_dispatch` manual.

---

## Checklist antes de activar venta real (Stripe LIVE)

- [ ] Confirmar `STRIPE_WEBHOOK_SECRET` LIVE en Cloudflare (no el de TEST).
- [ ] Confirmar Stripe LIVE webhook escucha solo `checkout.session.completed`.
- [ ] Confirmar `TALLY_FORM_URL = https://tally.so/r/MedpvA` activo en Worker.
- [ ] Confirmar `TALLY_SIGNING_SECRET` mismo valor en:
  - Tally `MedpvA` → Integrations → Webhooks
  - Tally `Ek6EM2` → Integrations → Webhooks
  - Cloudflare Worker secret `TALLY_SIGNING_SECRET`
- [ ] Confirmar Resend FROM: `MyGuest <hello@myguestguide.com>` y dominio verificado.
- [ ] Confirmar GitHub Pages funcionando: `https://myguestguide.com/villas/ocean-drive-retreat/`.
- [ ] Confirmar demos oficiales publicadas (4).
- [ ] Confirmar que no existen villas de prueba en `public/villas/`.
- [ ] Confirmar que `worker/wrangler.toml` tiene `TALLY_FORM_URL` (no se commitea, es local).
- [ ] Hacer una prueba end-to-end en TEST antes de activar LIVE.

---

## Protocolo para primer cliente real

1. No hacer cambios de código durante la primera venta real.
2. Confirmar pago en Stripe dashboard (modo LIVE).
3. Confirmar creación de `order:{paymentIntentId}` en KV — sin imprimir valores privados.
   ```
   npx wrangler kv key get "order:{paymentIntentId}" --binding MYGUEST_KV --remote
   ```
   Verificar: `status = paid`, `customer_email` correcto.
4. Confirmar email post-pago llegó al cliente.
5. Esperar que el cliente llene Tally.
6. Confirmar Tally submission procesada — `order` en KV debe avanzar a `generation_dispatched`.
7. Confirmar GitHub Actions run exitoso:
   ```
   gh run list --limit 5
   ```
8. Confirmar archivos publicados en `public/villas/{slug}/`.
9. Confirmar email final llegó al cliente (delivery record en KV: `status = delivered`).
10. Confirmar links del email:
    - digital guide público: `https://myguestguide.com/villas/{slug}/en.html`
    - guest link privado con token: `https://myguest-worker.veronica-perezarroyo.workers.dev/guest/{slug}?token=...`
    - printable privado con token: `https://myguest-worker.veronica-perezarroyo.workers.dev/print/{slug}?token=...`
11. Confirmar que GitHub Pages público NO contiene WiFi/password/códigos/teléfono/acceso privado.

---

## Diagnóstico de fallos comunes

### Email post-pago no llegó
- Verificar `order:{paymentIntentId}` en KV: ¿existe? ¿tiene `customer_email`?
- Verificar Resend logs.
- Revisar que Stripe webhook solo escucha `checkout.session.completed`.

### Tally submission rechazada
- Revisar Worker logs en Cloudflare Dashboard → Workers → myguest-worker → Logs.
- Causas comunes: `missing_order_id`, `order_email_mismatch`, `invalid_order_status`.
- Si el cliente usó un email diferente al pagar, ver `order_email_mismatch` en KV.

### GitHub Actions no corrió
- Revisar `order` en KV: ¿llegó a `generation_dispatched`?
- Confirmar `GITHUB_TOKEN` válido en Cloudflare secrets.
- Confirmar que `GITHUB_REPO = yuyitov/MyGuest` en `wrangler.toml`.

### Email final no llegó
- El endpoint `/notify` es llamado por `pages.yml` después del deploy.
- Revisar KV `delivery:{slug}`: ¿existe? ¿tiene `notified_at`?
- Si `status = delivered` pero no llegó email, revisar Resend.

### Correcciones no llegan a Vero
- Email de alerta es non-fatal (`.catch`). Revisar `correction:{slug}` en KV: ¿tiene `used: true`?
- Si `used: true` pero no llegó email, aplicar correcciones manualmente desde el formulario KV.

---

## Operaciones KV seguras

### Ver estado de una orden
```bash
npx wrangler kv key get "order:{paymentIntentId}" --binding MYGUEST_KV --remote
```

### Ver delivery record
```bash
npx wrangler kv key get "delivery:{slug}" --binding MYGUEST_KV --remote
```

### Verificar existencia sin imprimir valores privados
```bash
# Solo verificar si existe:
npx wrangler kv key get "priv-{slug}" --binding MYGUEST_KV --remote 2>&1 | head -1
```

### Limpiar KV de prueba (solo con manifest aprobado)
```bash
echo "y" | npx wrangler kv key delete "KEY" --binding MYGUEST_KV --remote
```

**Nunca borrar** sin manifest aprobado por Vero.

---

## Qué no hacer

- No borrar KV sin manifest aprobado.
- No hacer `gh run rerun` sin diagnosticar primero.
- No cambiar arquitectura sin aprobación.
- No meter secrets en `wrangler.toml` (solo vars no sensibles).
- No commitear `worker/wrangler.toml` (está en `.gitignore`).
- No publicar PDF completo sensible como archivo público.
- No usar `demo_mode: True` con datos reales de clientes.
- No mezclar webhooks TEST y LIVE de Stripe.
- No usar Payment Link TEST para clientes reales.
- No usar otros proyectos como referencia técnica para MyGuest.

---

## Variables de entorno del Worker

### En `wrangler.toml` (no secretas, sí commitear si se decidiera — actualmente ignorado)
| Variable | Valor |
|---|---|
| `GITHUB_REPO` | `yuyitov/MyGuest` |
| `FROM_EMAIL` | `MyGuest <hello@myguestguide.com>` |
| `PUBLIC_BOOK_BASE_URL` | `https://myguestguide.com` |
| `TALLY_FORM_URL` | `https://tally.so/r/MedpvA` |

### Secrets en Cloudflare (nunca en repo)
`ALERT_EMAIL`, `GITHUB_TOKEN`, `NOTIFY_SECRET`, `RESEND_API_KEY`, `STRIPE_WEBHOOK_SECRET`, `TALLY_SIGNING_SECRET`

### Nota sobre `wrangler.toml`
El archivo está en `.gitignore`. Si se despliega desde otra máquina, `TALLY_FORM_URL` debe estar en el `wrangler.toml` local o en Cloudflare Dashboard antes del deploy, de lo contrario el deploy la eliminaría del Worker.
