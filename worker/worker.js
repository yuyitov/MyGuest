/**
 * MyGuest Worker — Rescate funcional
 *
 * Flujo:
 * Tally → Worker → KV privados → GitHub repository_dispatch
 *
 * Variables esperadas en Cloudflare:
 * - GITHUB_REPO = yuyitov/MyGuest
 * - GITHUB_TOKEN = secret
 * - TALLY_SIGNING_SECRET = secret, reservado para validación posterior
 * - MYGUEST_KV = binding al namespace MYGUEST_PRIVATE
 */

 const SENSITIVE_KEYS = [
    'wifi_ssid',
    'wifi_password',
    'door_code',
    'building_code',
    'host_phone',
    'house_access_private',
    'private_notes',
    'private_access_notes',
    'private_access_details',
    'guest_access_token'
  ];

const REQUIRED_KEYS = [
  'property_name',
  'property_address',
  'style',
  'property_environment',
  'primary_language'
];

const VALID_STYLES = ['Minimalist', 'Coastal', 'Classic', 'Sunset'];
const VALID_LANGUAGES = ['English', 'Español', 'Français'];
const VALID_PROPERTY_ENVIRONMENTS = ['Beach', 'City', 'Cozy'];

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const pathname = url.pathname;

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    try {
      const ip = request.headers.get('cf-connecting-ip') || 'unknown';
      const minuteSlot = Math.floor(Date.now() / 60000);
      const hourSlot   = Math.floor(Date.now() / 3600000);

      if (request.method === 'GET' && pathname === '/health') {
        return jsonResponse({ ok: true, worker: 'myguest-worker' });
      }

      if (request.method === 'GET' && pathname.startsWith('/guest/')) {
        const allowed = await checkRateLimit(env, `rl:guest:${ip}:${hourSlot}`, 60, 3600);
        if (!allowed) return privateErrorHtml('Too many requests. Please try again later.', 429);
        return await handleGuestPrivateAccess(request, env);
      }

      if (request.method === 'GET' && pathname.startsWith('/print/')) {
        const allowed = await checkRateLimit(env, `rl:print:${ip}:${hourSlot}`, 30, 3600);
        if (!allowed) return privateErrorHtml('Too many requests. Please try again later.', 429);
        return await handlePrintAccess(request, env);
      }

      if (request.method === 'GET' && pathname.startsWith('/correct/')) {
        const allowed = await checkRateLimit(env, `rl:correct:${ip}:${hourSlot}`, 20, 3600);
        if (!allowed) return correctionErrorHtml('Too many requests. Please try again later.', 429);
        return await handleCorrectionAccess(request, env);
      }

      if (request.method === 'POST' && (pathname === '/' || pathname === '/tally-webhook')) {
        const allowed = await checkRateLimit(env, `rl:tally:${ip}:${minuteSlot}`, 10, 120);
        if (!allowed) return jsonResponse({ ok: false, error: 'Too many requests' }, 429);
        return await handleTallyWebhook(request, env, ctx);
      }

      // ─── NUEVO 16.1-B ────────────────────────────────────────────────────
      if (request.method === 'POST' && pathname === '/stripe/webhook') {
        return await handleStripeWebhook(request, env);
      }

      if (request.method === 'POST' && pathname === '/notify') {
        const allowed = await checkRateLimit(env, `rl:notify:${ip}:${minuteSlot}`, 20, 120);
        if (!allowed) return jsonResponse({ ok: false, error: 'Too many requests' }, 429);
        return await handleNotify(request, env);
      }
      // ─────────────────────────────────────────────────────────────────────

      return jsonResponse({ ok: false, error: 'Not found' }, 404);
    } catch (error) {
      console.error('Worker error:', safeError(error));

      if (pathname.startsWith('/guest/') || pathname.startsWith('/print/')) {
        return privateErrorHtml('Private access is temporarily unavailable.', 500);
      }

      return jsonResponse(
        {
          ok: false,
          error: 'Internal worker error',
          message: error.message
        },
        500
      );
    } 
  }
};

async function verifyTallySignature(rawBody, signatureHeader, secret) {
  // Source: https://tally.so/help/webhooks and https://developers.tally.so
  // Header: "Tally-Signature" (HTTP headers are case-insensitive)
  // Algorithm: HMAC-SHA256 of JSON.stringify(parsedPayload)
  // Format: base64-encoded digest (NOT hex)
  if (!secret || !signatureHeader) return false;

  let normalizedBody;
  try {
    normalizedBody = JSON.stringify(JSON.parse(rawBody));
  } catch {
    normalizedBody = rawBody;
  }

  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(normalizedBody));
  const expectedBase64 = btoa(String.fromCharCode(...new Uint8Array(sig)));
  return timingSafeEqual(expectedBase64, signatureHeader.trim());
}

async function handleTallyWebhook(request, env, ctx) {
  assertEnv(env);

  const rawBody = await request.text().catch(() => null);

  if (rawBody === null) {
    return jsonResponse({ ok: false, error: 'Could not read request body' }, 400);
  }

  // HMAC signature validation — rejects requests not from Tally.
  // Fail-closed: without the secret configured, no webhook is accepted.
  if (!env.TALLY_SIGNING_SECRET) {
    return jsonResponse({ ok: false, error: 'Webhook signature validation not configured' }, 500);
  }
  const sigHeader = request.headers.get('tally-signature') || '';
  const valid = await verifyTallySignature(rawBody, sigHeader, env.TALLY_SIGNING_SECRET);
  if (!valid) {
    return jsonResponse({ ok: false, error: 'Invalid webhook signature' }, 401);
  }

  let rawPayload;
  try {
    rawPayload = JSON.parse(rawBody);
  } catch {
    rawPayload = null;
  }

  if (!rawPayload) {
    return jsonResponse({ ok: false, error: 'Invalid JSON payload' }, 400);
  }

  const normalized = normalizeTallyPayload(rawPayload);

  // Formulario interno de revisión manual — flujo distinto al intake normal
  const flowType = cleanValue(getAnswer(normalized.answers, 'flow_type')) || '';
  if (flowType === 'manual_extraction_review') {
    return await handleManualExtractionReview(request, normalized, env);
  }

  // Formulario de correcciones — detectar antes del guard de order_id/pago
  const formType = cleanValue(getAnswer(normalized.answers, 'form_type')) || '';
  if (formType === 'corrections') {
    return await handleCorrectionsSubmission(normalized, env);
  }

  if (!normalized.submission_id) {
    return jsonResponse({
      ok: false,
      error: 'Missing submission_id',
      hint: 'Tally payload did not include a recognizable submission id.'
    }, 400);
  }

  const now = new Date().toISOString();

  // ─── NUEVO: Single-use order_id guard ────────────────────────────────────
  const incomingOrderId = cleanValue(getAnswer(normalized.answers, 'order_id')) || '';
  let reservedOrderRecord = null;

  if (incomingOrderId) {
    const existingOrder = await env.MYGUEST_KV.get(`order:${incomingOrderId}`, { type: 'json' }).catch(() => null);

    // order_id presente pero no existe en KV → inválido/inventado
    if (!existingOrder) {
      await env.MYGUEST_KV.put(
        `invalid_order:${incomingOrderId}:${normalized.submission_id}`,
        JSON.stringify({ order_id: incomingOrderId, submission_id: normalized.submission_id, attempted_at: now }),
        { expirationTtl: 2592000 }
      ).catch(() => {});
      return jsonResponse({ ok: false, status: 'invalid_order_id', order_id: incomingOrderId }, 403);
    }

    // Verificar coincidencia de email si el form lo incluye — con trazabilidad en KV
    const formEmail = (cleanValue(getAnswer(normalized.answers, 'customer_email')) || '').toLowerCase().trim();
    const orderEmail = (existingOrder.customer_email || existingOrder.email || '').toLowerCase().trim();
    if (formEmail && orderEmail && formEmail !== orderEmail) {
      await env.MYGUEST_KV.put(
        `email_mismatch:${incomingOrderId}:${normalized.submission_id}`,
        JSON.stringify({
          order_id: incomingOrderId,
          submission_id: normalized.submission_id,
          form_email: formEmail,
          order_email: orderEmail,
          attempted_at: now
        }),
        { expirationTtl: 2592000 }
      ).catch(() => {});
      return jsonResponse({ ok: false, status: 'order_email_mismatch', order_id: incomingOrderId }, 403);
    }

    // Courtesy order vs paid order — rutas de validación distintas
    const isCourtesy = existingOrder.type === 'courtesy_order';

    if (isCourtesy) {
      const courtesyExpired = existingOrder.expires_at && new Date(existingOrder.expires_at) < new Date(now);
      const courtesyRevoked = ['revoked', 'cancelled'].includes(existingOrder.status);
      const booksUsed       = Number(existingOrder.books_used || 0);
      const booksAuthorized = Number(existingOrder.books_authorized || 0);

      let courtesyError = null;
      if (courtesyRevoked)                     courtesyError = 'courtesy_order_revoked';
      else if (courtesyExpired)                courtesyError = 'courtesy_order_expired';
      else if (existingOrder.status !== 'active') courtesyError = 'courtesy_order_not_active';
      else if (booksUsed >= booksAuthorized)   courtesyError = 'courtesy_order_exhausted';

      if (courtesyError) {
        await env.MYGUEST_KV.put(
          `invalid_order_status:${incomingOrderId}:${normalized.submission_id}`,
          JSON.stringify({ order_id: incomingOrderId, submission_id: normalized.submission_id, blocked_by: courtesyError, attempted_at: now }),
          { expirationTtl: 2592000 }
        ).catch(() => {});
        return jsonResponse({ ok: false, status: courtesyError, order_id: incomingOrderId }, 409);
      }
    } else {
      // Paid order — allowlist explícita de estados válidos para generar book
      const allowedStatuses = ['paid', 'form_sent', 'failed_dispatch'];
      if (!allowedStatuses.includes(existingOrder.status)) {
        await env.MYGUEST_KV.put(
          `invalid_order_status:${incomingOrderId}:${normalized.submission_id}`,
          JSON.stringify({ order_id: incomingOrderId, submission_id: normalized.submission_id, blocked_by_status: existingOrder.status, attempted_at: now }),
          { expirationTtl: 2592000 }
        ).catch(() => {});
        return jsonResponse({ ok: false, status: 'invalid_order_status', order_id: incomingOrderId }, 409);
      }
    }

    reservedOrderRecord = existingOrder;
  }
  // ─────────────────────────────────────────────────────────────────────────

  // ─── Guard: bloquear submissions sin order_id ────────────────────────────
  if (!incomingOrderId) {
    const noOrderEmail = (cleanValue(getAnswer(normalized.answers, 'customer_email')) || '').toLowerCase().trim();

    await env.MYGUEST_KV.put(
      `missing_order:${normalized.submission_id}`,
      JSON.stringify({
        submission_id: normalized.submission_id,
        form_email:    noOrderEmail || '(empty)',
        attempted_at:  now
      }),
      { expirationTtl: 2592000 }
    ).catch(() => {});

    return jsonResponse({
      ok:            false,
      status:        'missing_order_id',
      submission_id: normalized.submission_id
    }, 403);
  }
  // ─────────────────────────────────────────────────────────────────────────

  const indexKey = `subm-${normalized.submission_id}`;

  let index = await env.MYGUEST_KV.get(indexKey, { type: 'json' });

  if (!index) {
    index = {
      submission_id: normalized.submission_id,
      slug: null,
      private_record_key: null,
      status: 'received',
      attempt_count: 0,
      last_error: null,
      last_updated_at: now
    };
  }

  index.attempt_count = Number(index.attempt_count || 0) + 1;
  index.status = 'received';
  index.last_error = null;
  index.last_updated_at = now;

  await env.MYGUEST_KV.put(indexKey, JSON.stringify(index));

  const validation = validateRequiredPublicFields(normalized.answers);

  if (!validation.ok) {
    index.status = 'failed_validation';
    index.last_error = validation.error;
    index.last_updated_at = now;
    await env.MYGUEST_KV.put(indexKey, JSON.stringify(index));

    return jsonResponse({
      ok: false,
      status: 'failed_validation',
      missing: validation.missing,
      invalid: validation.invalid,
      error: validation.error
    }, 400);
  }

  const slug = index.slug || makeSlug(
    getAnswer(normalized.answers, 'property_name') || 'villa',
    normalized.submission_id
  );

  const privateRecordKey = `priv-${slug}`;

  const existingPrivate = await env.MYGUEST_KV.get(privateRecordKey, { type: 'json' }).catch(() => null);
  const guestToken =
    existingPrivate?.guest_access?.guest_access_token ||
    createSecureToken();

  const origin = new URL(request.url).origin;

  const privatePayload = buildPrivatePayload({
    normalized,
    slug,
    privateRecordKey,
    guestToken,
    origin,
    now
  });

  try {
    await env.MYGUEST_KV.put(privateRecordKey, JSON.stringify(privatePayload));

    index.slug = slug;
    index.private_record_key = privateRecordKey;
    index.status = 'stored_private';
    index.last_updated_at = now;
    await env.MYGUEST_KV.put(indexKey, JSON.stringify(index));
  } catch (error) {
    index.status = 'failed_private_storage';
    index.last_error = error.message;
    index.last_updated_at = now;
    await env.MYGUEST_KV.put(indexKey, JSON.stringify(index));

    throw error;
  }

  const publicPayload = buildPublicPayload({
    normalized,
    slug,
    privateRecordKey,
    origin,
    now
  });

  // ─── Delivery record base (para email al completar) ─────────────────────
  let customerEmail = cleanValue(getAnswer(normalized.answers, 'customer_email')) || '';
  if (!customerEmail && reservedOrderRecord) {
    customerEmail = reservedOrderRecord.customer_email || reservedOrderRecord.email || '';
  }
  const langMap = { 'English': 'en', 'Español': 'es', 'Français': 'fr' };
  const bookLang = langMap[cleanValue(getAnswer(normalized.answers, 'primary_language'))] || 'en';
  const publicBase = (cleanValue(env.PUBLIC_BOOK_BASE_URL) || 'https://myguestguide.com').replace(/\/+$/, '');
  // ─────────────────────────────────────────────────────────────────────────

  // ─── Detección de adjuntos — DEBE ocurrir ANTES del dispatch ─────────────
  // Si el cliente subió materiales (PDF, Word, fotos, capturas), el flujo
  // se pausa aquí. No se genera el book hasta que Vero revise y extraiga
  // la información manualmente. Estado: needs_manual_extraction.
  const existingBookFile   = getAnswer(normalized.answers, 'existing_book_file');
  const existingBookPhotos = getAnswer(normalized.answers, 'existing_book_photos');
  const hasMaterials =
    hasUploadedMaterial(existingBookFile) ||
    hasUploadedMaterial(existingBookPhotos);

  if (hasMaterials) {
    // Guardar registro de intake para revisión manual
    try {
      await env.MYGUEST_KV.put(`intake:${slug}`, JSON.stringify({
        slug,
        submission_id: normalized.submission_id,
        customer_email: customerEmail,
        existing_book_file: existingBookFile,
        existing_book_photos: existingBookPhotos,
        has_materials: true,
        status: 'needs_manual_extraction',
        created_at: now,
        original_answers: normalized.answers
      }));
    } catch (err) {
      console.error('intake record save failed (non-fatal):', safeError(err));
    }

    // Actualizar estado del índice
    index.status = 'needs_manual_extraction';
    index.last_updated_at = now;
    await env.MYGUEST_KV.put(indexKey, JSON.stringify(index));

    // Marcar order como pendiente de extracción manual
    if (incomingOrderId && reservedOrderRecord) {
      try {
        const updatedOrderUpload = {
          ...reservedOrderRecord,
          status: 'needs_manual_extraction',
          submission_id: normalized.submission_id,
          slug,
          submitted_at: now
        };
        if (reservedOrderRecord.type === 'courtesy_order') {
          updatedOrderUpload.books_used = Number(reservedOrderRecord.books_used || 0) + 1;
          updatedOrderUpload.used_at    = now;
          updatedOrderUpload.audit_log  = [
            ...(reservedOrderRecord.audit_log || []),
            { event: 'submission_accepted_needs_manual_extraction', submission_id: normalized.submission_id, slug, at: now }
          ];
        }
        await env.MYGUEST_KV.put(`order:${incomingOrderId}`, JSON.stringify(updatedOrderUpload));
      } catch (err) {
        console.error('order manual extraction status update failed (non-fatal):', safeError(err));
      }
    }

    // Guardar delivery record con estado pausado
    const deliveryRecord = {
      slug,
      order_id: incomingOrderId || null,
      customer_email: customerEmail,
      public_url: buildPublicBookUrl(env, slug, bookLang),
      guest_access_url: privatePayload.guest_access.guest_access_url,
      status: 'needs_manual_extraction',
      created_at: now
    };
    try {
      await env.MYGUEST_KV.put(`delivery:${slug}`, JSON.stringify(deliveryRecord));
    } catch (err) {
      console.error('delivery record save failed (non-fatal):', safeError(err));
    }

    // Notificar a Vero por email — ctx.waitUntil garantiza que el fetch a Resend
    // se completa aunque el Worker ya haya devuelto la respuesta HTTP.
    if (env.ALERT_EMAIL && env.RESEND_API_KEY) {
      const propertyName = cleanValue(getAnswer(normalized.answers, 'property_name')) || slug;
      const clientName   = cleanValue(getAnswer(normalized.answers, 'customer_name')) || '';
      const emailPromise = (async () => {
        console.log('alert email: attempting send to', env.ALERT_EMAIL);
        try {
          const result = await sendEmail({
            env,
            to:      env.ALERT_EMAIL,
            subject: `[MyGuest] Revisión manual pendiente: ${propertyName}`,
            html:    buildAlertEmail({ propertyName, clientName, customerEmail, slug, submissionId: normalized.submission_id, now, existingBookFile, existingBookPhotos })
          });
          console.log('alert email sent', result?.id || '');
        } catch (err) {
          console.error('alert email failed:', safeError(err));
        }
      })();
      if (ctx?.waitUntil) {
        ctx.waitUntil(emailPromise);
      }
    }

    // Responder sin despachar a GitHub — Vero debe revisar primero
    return jsonResponse({
      ok: true,
      status: 'needs_manual_extraction',
      submission_id: normalized.submission_id,
      slug,
      message: 'Submission received. Manual extraction required before generation.'
    });
  }
  // ─────────────────────────────────────────────────────────────────────────

  // Reservar order ANTES del dispatch para evitar doble generación (anti-race)
  if (incomingOrderId && reservedOrderRecord) {
    try {
      const updatedOrderDispatch = {
        ...reservedOrderRecord,
        status: 'submitted',
        submission_id: normalized.submission_id,
        slug,
        submitted_at: now
      };
      if (reservedOrderRecord.type === 'courtesy_order') {
        updatedOrderDispatch.books_used = Number(reservedOrderRecord.books_used || 0) + 1;
        updatedOrderDispatch.used_at    = now;
        updatedOrderDispatch.audit_log  = [
          ...(reservedOrderRecord.audit_log || []),
          { event: 'submission_accepted', submission_id: normalized.submission_id, slug, at: now }
        ];
      }
      await env.MYGUEST_KV.put(`order:${incomingOrderId}`, JSON.stringify(updatedOrderDispatch));
    } catch (err) {
      console.error('order reservation failed:', safeError(err));
      throw new Error('Failed to reserve order — aborting dispatch');
    }
  }

  try {
    await dispatchToGitHub(publicPayload, env);

    index.status = 'dispatched_to_github';
    index.last_error = null;
    index.last_updated_at = now;
    await env.MYGUEST_KV.put(indexKey, JSON.stringify(index));

    // Marcar order como generation_dispatched (no-fatal)
    if (incomingOrderId) {
      const cur = await env.MYGUEST_KV.get(`order:${incomingOrderId}`, { type: 'json' }).catch(() => null);
      if (cur) {
        await env.MYGUEST_KV.put(`order:${incomingOrderId}`, JSON.stringify({
          ...cur, status: 'generation_dispatched', dispatched_at: now
        })).catch(err => console.error('order dispatch status update failed (non-fatal):', safeError(err)));
      }
    }
  } catch (error) {
    index.status = 'failed_dispatch';
    index.last_error = error.message;
    index.last_updated_at = now;
    await env.MYGUEST_KV.put(indexKey, JSON.stringify(index));

    // Revertir order a failed_dispatch para permitir reintento
    if (incomingOrderId) {
      const cur = await env.MYGUEST_KV.get(`order:${incomingOrderId}`, { type: 'json' }).catch(() => null);
      if (cur) {
        await env.MYGUEST_KV.put(`order:${incomingOrderId}`, JSON.stringify({
          ...cur, status: 'failed_dispatch', last_error: error.message, last_updated_at: now
        })).catch(() => {});
      }
    }

    throw error;
  }

  // Guardar delivery record
  const deliveryRecord = {
    slug,
    order_id: incomingOrderId || null,
    customer_email: customerEmail,
    public_url: buildPublicBookUrl(env, slug, bookLang),
    guest_access_url: privatePayload.guest_access.guest_access_url,
    status: 'pending',
    created_at: now
  };
  try {
    await env.MYGUEST_KV.put(`delivery:${slug}`, JSON.stringify(deliveryRecord));
  } catch (err) {
    console.error('delivery record save failed (non-fatal):', safeError(err));
  }

  return jsonResponse({
    ok: true,
    status: 'dispatched_to_github',
    submission_id: normalized.submission_id,
    slug,
    private_record_key: privateRecordKey,
    guest_access_url: privatePayload.guest_access.guest_access_url
  });
}

async function handleGuestPrivateAccess(request, env) {
  if (!env.MYGUEST_KV) {
    return privateErrorHtml('Private access is not configured.', 500);
  }

  const url = new URL(request.url);
  const token = url.searchParams.get('token') || '';

  const match = url.pathname.match(/^\/guest\/([^/]+)$/);
  const slug = match ? decodeURIComponent(match[1]) : null;

  if (!slug || !token) {
    return privateErrorHtml('Missing or invalid private access link.', 401);
  }

  const privateRecordKey = `priv-${slug}`;
  const record = await env.MYGUEST_KV.get(privateRecordKey, { type: 'json' });

  if (!record) {
    return privateErrorHtml('Private access record was not found.', 404);
  }

  const expectedToken = record?.guest_access?.guest_access_token;

  if (!expectedToken || !timingSafeEqual(token, expectedToken)) {
    return privateErrorHtml('This private access link is invalid or expired.', 403);
  }

  const lang = normalizePrivateBookLang(url.searchParams.get('lang'));
  const publicBookUrl = buildPublicBookUrl(env, slug, lang);

  const publicResponse = await fetch(publicBookUrl, {
    headers: {
      'accept': 'text/html'
    },
    cf: {
      cacheTtl: 60,
      cacheEverything: false
    }
  });

  if (!publicResponse.ok) {
    return privateErrorHtml('The public guest guide is not available yet.', 404);
  }

  const publicHtml = await publicResponse.text();

  const privateHtml = injectPrivateDetailsIntoBookHtml({
    html: publicHtml,
    slug,
    token,
    secrets: record.secrets || {},
    lang
  });

  return new Response(privateHtml, {
    status: 200,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'no-store, no-cache, must-revalidate, private',
      'pragma': 'no-cache',
      'x-robots-tag': 'noindex, nofollow, noarchive',
      'x-content-type-options': 'nosniff',
      'referrer-policy': 'no-referrer'
    }
  });
}

async function handlePrintAccess(request, env) {
  if (!env.MYGUEST_KV) {
    return privateErrorHtml('Private access is not configured.', 500);
  }

  const url = new URL(request.url);
  const token = url.searchParams.get('token') || '';

  const match = url.pathname.match(/^\/print\/([^/]+)$/);
  const slug = match ? decodeURIComponent(match[1]) : null;

  if (!slug || !token) {
    return privateErrorHtml('Missing or invalid print access link.', 401);
  }

  const record = await env.MYGUEST_KV.get(`priv-${slug}`, { type: 'json' });

  if (!record) {
    return privateErrorHtml('Print access record was not found.', 404);
  }

  const expectedToken = record?.guest_access?.guest_access_token;
  if (!expectedToken || !timingSafeEqual(token, expectedToken)) {
    return privateErrorHtml('This print access link is invalid or expired.', 403);
  }

  const base = cleanValue(env.PUBLIC_BOOK_BASE_URL) || 'https://yuyitov.github.io/MyGuest';
  const printUrl = `${base.replace(/\/+$/, '')}/villas/${encodeURIComponent(slug)}/print.html`;

  const printResponse = await fetch(printUrl, { cf: { cacheTtl: 60, cacheEverything: false } });
  if (!printResponse.ok) {
    return privateErrorHtml('The printable guide is not available yet.', 404);
  }

  const printHtml = await printResponse.text();
  const injected = injectPrivateDetailsIntoPrintHtml({ html: printHtml, secrets: record.secrets || {} });

  return new Response(injected, {
    status: 200,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'no-store, no-cache, must-revalidate, private',
      'pragma': 'no-cache',
      'x-robots-tag': 'noindex, nofollow, noarchive',
      'x-content-type-options': 'nosniff',
      'referrer-policy': 'no-referrer'
    }
  });
}

function injectPrivateDetailsIntoPrintHtml({ html, secrets }) {
  let output = String(html || '');
  const s = secrets || {};
  const sourceLang = s._source_lang || 'en';

  for (const lang of ['en', 'es', 'fr']) {
    const lbl = PRIVATE_BOOK_LABELS[lang];
    const rows = [];
    if (s.wifi_ssid)            rows.push(`<div class="contact-row"><span class="contact-label">${lbl.wifiNetwork}</span><span class="contact-val">${escapeHtml(String(s.wifi_ssid))}</span></div>`);
    if (s.wifi_password)        rows.push(`<div class="contact-row"><span class="contact-label">${lbl.wifiPassword}</span><span class="contact-val">${escapeHtml(String(s.wifi_password))}</span></div>`);
    if (s.door_code)            rows.push(`<div class="contact-row"><span class="contact-label">${lbl.doorCode}</span><span class="contact-val">${escapeHtml(String(s.door_code))}</span></div>`);
    if (s.building_code)        rows.push(`<div class="contact-row"><span class="contact-label">${lbl.buildingCode}</span><span class="contact-val">${escapeHtml(String(s.building_code))}</span></div>`);
    if (s.house_access_private) {
      const langMismatch = sourceLang && sourceLang !== lang;
      const accessLabel = langMismatch
        ? `${lbl.access} — ${ACCESS_PROVIDED_IN[lang] || 'provided in'} ${(LANG_NAMES[lang] || LANG_NAMES.en)[sourceLang] || sourceLang}`
        : lbl.access;
      rows.push(`<div class="contact-row"><span class="contact-label">${escapeHtml(accessLabel)}</span><span class="contact-val">${escapeHtml(String(s.house_access_private))}</span></div>`);
    }
    if (s.host_phone)           rows.push(`<div class="contact-row"><span class="contact-label">${lbl.hostPhone}</span><span class="contact-val">${escapeHtml(String(s.host_phone))}</span></div>`);

    if (rows.length > 0) {
      const privateBlock = `<div class="contact-rows" style="margin-top:20px;padding-top:16px;border-top:1px solid #e0d8ce">${rows.join('')}</div>`;
      output = output.split(`<div id="private-house-print-block-${lang}"></div>`).join(privateBlock);
    }
  }

  const phoneRow = s.host_phone
    ? `<div class="contact-row"><span class="contact-label">Phone</span><span class="contact-val">${escapeHtml(String(s.host_phone))}</span></div>`
    : '';
  output = output.split('<div id="private-phone-contact-block"></div>').join(phoneRow);

  return output;
}

function normalizeTallyPayload(payload) {
  let submissionId =
    payload?.id ||
    payload?.submission_id ||
    payload?.submissionId ||
    payload?.responseId ||
    payload?.data?.id ||
    payload?.data?.submission_id ||
    payload?.data?.submissionId ||
    payload?.data?.responseId ||
    null;

  const submittedAt =
    payload?.submitted_at ||
    payload?.submittedAt ||
    payload?.createdAt ||
    payload?.data?.submitted_at ||
    payload?.data?.submittedAt ||
    payload?.data?.createdAt ||
    new Date().toISOString();

    const answers = {};

  // Permite pruebas manuales con JSON plano desde PowerShell.
  // Ejemplo: { property_name, property_address, style, primary_language, ... }
  copyTopLevelAnswers(answers, payload);

  if (payload?.answers && typeof payload.answers === 'object' && !Array.isArray(payload.answers)) {
    copyAnswerObject(answers, payload.answers);
  }

  if (payload?.data?.answers && typeof payload.data.answers === 'object' && !Array.isArray(payload.data.answers)) {
    copyAnswerObject(answers, payload.data.answers);
  }

  // Tally envía hidden fields pre-rellenados (vía URL params) en hiddenFields separado de fields
  if (payload?.data?.hiddenFields && typeof payload.data.hiddenFields === 'object' && !Array.isArray(payload.data.hiddenFields)) {
    copyAnswerObject(answers, payload.data.hiddenFields);
  }

  if (payload?.hiddenFields && typeof payload.hiddenFields === 'object' && !Array.isArray(payload.hiddenFields)) {
    copyAnswerObject(answers, payload.hiddenFields);
  }

  const fields =
    Array.isArray(payload?.data?.fields) ? payload.data.fields :
    Array.isArray(payload?.fields) ? payload.fields :
    [];

  for (const field of fields) {
    const value = extractTallyFieldValue(field);

    const keys = [
      field?.key,
      field?.name,
      field?.label,
      field?.title,
      field?.id
    ].filter(Boolean);

    for (const key of keys) {
      answers[String(key)] = value;
      answers[normalizeKey(String(key))] = value;
    }
  }

  return {
    submission_id: String(submissionId || ''),
    submitted_at: submittedAt,
    answers,
    raw: payload
  };
}

function copyAnswerObject(target, source) {
  for (const [key, value] of Object.entries(source)) {
    target[key] = value;
    target[normalizeKey(key)] = value;
  }
}

function copyTopLevelAnswers(target, source) {
  if (!source || typeof source !== 'object' || Array.isArray(source)) return;

  const reservedKeys = new Set([
    'id',
    'submission_id',
    'submissionId',
    'responseId',
    'submitted_at',
    'submittedAt',
    'createdAt',
    'data',
    'answers',
    'fields'
  ]);

  for (const [key, value] of Object.entries(source)) {
    if (reservedKeys.has(key)) continue;
    target[key] = value;
    target[normalizeKey(key)] = value;
  }
}

function extractTallyFieldValue(field) {
  if (!field || typeof field !== 'object') return field;

  const rawValue =
    'value' in field ? field.value :
    'answer' in field ? field.answer :
    'answers' in field ? field.answers :
    'text' in field ? field.text :
    null;

  // Tally Multiple Choice manda IDs; aquí los convertimos al texto real.
  if (Array.isArray(rawValue) && Array.isArray(field.options)) {
    const selectedTexts = rawValue
      .map((selectedId) => {
        const option = field.options.find((opt) => opt.id === selectedId);
        return option ? option.text : selectedId;
      })
      .filter(Boolean);

    if (selectedTexts.length === 1) return selectedTexts[0];
    return selectedTexts;
  }

  if (typeof rawValue === 'string' && Array.isArray(field.options)) {
    const option = field.options.find((opt) => opt.id === rawValue);
    return option ? option.text : rawValue;
  }

  return rawValue;
}

function buildPrivatePayload({ normalized, slug, privateRecordKey, guestToken, origin, now }) {
  const answers = normalized.answers;

  return {
    metadata: {
      payload_version: '1.0',
      source: 'tally',
      submission_id: normalized.submission_id,
      submitted_at: normalized.submitted_at,
      slug,
      private_record_key: privateRecordKey,
      status: 'stored_private'
    },
        secrets: {
      wifi_ssid: cleanValue(getAnswer(answers, 'wifi_ssid')),
      wifi_password: cleanValue(getAnswer(answers, 'wifi_password')),

      // Se conserva soporte para registros viejos, pero ya no se mostrará como tarjeta separada.
      door_code: cleanValue(getAnswer(answers, 'door_code')),
      building_code: cleanValue(getAnswer(answers, 'building_code')),

      host_phone: cleanValue(getAnswer(answers, 'host_phone')),

      // Fuente única para lo que debe aparecer en Access & Parking privado.
      house_access_private:
        cleanValue(getAnswer(answers, 'house_access_private')) ||
        cleanValue(getAnswer(answers, 'private_access_details')) ||
        cleanValue(getAnswer(answers, 'private_access_notes')),

      private_notes: cleanValue(getAnswer(answers, 'private_notes')),

      // Idioma en que fue capturado el formulario. Se usa para anotar el bloque
      // de access cuando el huésped abre la guía en un idioma diferente.
      // No es un dato sensible — es solo el código de idioma ('en', 'es', 'fr').
      _source_lang: (() => {
        const pl = cleanValue(getAnswer(answers, 'primary_language'));
        if (pl === 'Español') return 'es';
        if (pl === 'Français') return 'fr';
        return 'en';
      })()
    },
    guest_access: {
      guest_access_enabled: true,
      guest_access_method: 'secure_token',
      guest_access_token: guestToken,
      guest_access_url: `${origin}/guest/${slug}?token=${guestToken}`,
      guest_access_pin_required: false,
      last_updated_at: now
    }
  };
}

function buildPublicPayload({ normalized, slug, privateRecordKey, origin, now }) {
  const answers = normalized.answers;

  return {
    metadata: {
      payload_version: '1.0',
      source: 'tally',
      submission_id: normalized.submission_id,
      submitted_at: normalized.submitted_at,
      slug,
      template_version: 'master',
      private_record_key: privateRecordKey,
      generated_private_url: `${origin}/guest/${slug}`,
      status: 'received'
    },
    property: {
      property_name: cleanValue(getAnswer(answers, 'property_name')),
      property_address: cleanValue(getAnswer(answers, 'property_address')),
      style: cleanValue(getAnswer(answers, 'style')),
      property_environment: cleanValue(getAnswer(answers, 'property_environment')) || 'Beach',
      primary_language: cleanValue(getAnswer(answers, 'primary_language'))
    },
    outputs: {
      // El formulario ya no pregunta esto: MyGuest genera siempre mobile + PDF.
      mobile_version: true,
      print_pdf: true
    },
    ingest_inputs: {
      additional_notes: cleanValue(getAnswer(answers, 'additional_notes'))
    },
    content: {
      checkin: {
        checkin_time: cleanValue(getAnswer(answers, 'checkin_time')),
        checkout_time: cleanValue(getAnswer(answers, 'checkout_time')),
        house_access_public: cleanValue(getAnswer(answers, 'house_access_public')),
        parking_info: cleanValue(getAnswer(answers, 'parking_info'))
      },
      about_house: {
        welcome_message: cleanValue(getAnswer(answers, 'welcome_message')),
        about_hosts: cleanValue(getAnswer(answers, 'about_hosts')),
        amenities_list: cleanValue(getAnswer(answers, 'amenities_list')),
        property_photos: cleanValue(getAnswer(answers, 'property_photos')),
        pet_friendly: normalizeBooleanOrNull(getAnswer(answers, 'pet_friendly')),
        pet_rules: cleanValue(getAnswer(answers, 'pet_rules'))
      },
      location_transport: {
        google_maps_link: cleanValue(getAnswer(answers, 'google_maps_link')),
        directions_text: cleanValue(getAnswer(answers, 'directions_text')),
        transport_options: cleanValue(getAnswer(answers, 'transport_options'))
      },
      rules_info: {
        house_rules: cleanValue(getAnswer(answers, 'house_rules')),
        things_to_know: cleanValue(getAnswer(answers, 'things_to_know')),
        before_you_leave: cleanValue(getAnswer(answers, 'before_you_leave'))
      },
      recommendations: buildRecommendationsPayload(answers),
      contact_social: {
        host_email: cleanValue(getAnswer(answers, 'host_email')),
        emergency_contacts: cleanValue(getAnswer(answers, 'emergency_contacts')),
        airbnb_review_link: cleanValue(getAnswer(answers, 'airbnb_review_link')),
        instagram_handle: cleanValue(getAnswer(answers, 'instagram_handle'))
      }
    }
  };
}

function buildRecommendationsPayload(answers) {
  const recommendations = {
    // Compatibilidad con formulario anterior / extracción IA.
    places_to_eat: cleanValue(getAnswer(answers, 'places_to_eat')),
    places_to_drink: cleanValue(getAnswer(answers, 'places_to_drink')),
    things_to_do: cleanValue(getAnswer(answers, 'things_to_do')),
    local_directory: cleanValue(getAnswer(answers, 'local_directory'))
  };

  for (let i = 1; i <= 5; i++) {
    recommendations[`restaurant_${i}_name`] = cleanValue(getAnswer(answers, `restaurant_${i}_name`));
    recommendations[`restaurant_${i}_maps_link`] = cleanValue(getAnswer(answers, `restaurant_${i}_maps_link`));
    recommendations[`restaurant_${i}_phone`] = cleanValue(getAnswer(answers, `restaurant_${i}_phone`));

    recommendations[`bar_${i}_name`] = cleanValue(getAnswer(answers, `bar_${i}_name`));
    recommendations[`bar_${i}_maps_link`] = cleanValue(getAnswer(answers, `bar_${i}_maps_link`));
    recommendations[`bar_${i}_phone`] = cleanValue(getAnswer(answers, `bar_${i}_phone`));

    recommendations[`activity_${i}_name`] = cleanValue(getAnswer(answers, `activity_${i}_name`));
    recommendations[`activity_${i}_link`] = cleanValue(getAnswer(answers, `activity_${i}_link`));
    recommendations[`activity_${i}_phone`] = cleanValue(getAnswer(answers, `activity_${i}_phone`));
  }

  return recommendations;
}

async function dispatchToGitHub(payload, env) {
  if (!env.GITHUB_REPO) {
    throw new Error('Missing GITHUB_REPO');
  }

  if (!env.GITHUB_TOKEN) {
    throw new Error('Missing GITHUB_TOKEN');
  }

  const response = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/dispatches`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: 'application/vnd.github+json',
      'Content-Type': 'application/json',
      'User-Agent': 'myguest-worker'
    },
    body: JSON.stringify({
      event_type: 'new-villa',
      client_payload: payload
    })
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`GitHub dispatch failed: ${response.status} ${body}`);
  }
}

function validateRequiredPublicFields(answers) {
  const missing = [];

  for (const key of REQUIRED_KEYS) {
    const value = getAnswer(answers, key);
    if (isEmpty(value)) missing.push(key);
  }

  const invalid = [];

  const style = cleanValue(getAnswer(answers, 'style'));
  if (style && !VALID_STYLES.includes(style)) {
    invalid.push(`style must be one of: ${VALID_STYLES.join(', ')}`);
  }

  const primaryLanguage = cleanValue(getAnswer(answers, 'primary_language'));
  if (primaryLanguage && !VALID_LANGUAGES.includes(primaryLanguage)) {
    invalid.push(`primary_language must be one of: ${VALID_LANGUAGES.join(', ')}`);
  }

  const propertyEnvironment = cleanValue(getAnswer(answers, 'property_environment'));
  if (propertyEnvironment && !VALID_PROPERTY_ENVIRONMENTS.includes(propertyEnvironment)) {
    invalid.push(`property_environment must be one of: ${VALID_PROPERTY_ENVIRONMENTS.join(', ')}`);
  }

  return {
    ok: missing.length === 0 && invalid.length === 0,
    missing,
    invalid,
    error: [...missing.map((key) => `Missing ${key}`), ...invalid].join('; ')
  };
}

function assertEnv(env) {
  const missing = [];

  if (!env.MYGUEST_KV) missing.push('MYGUEST_KV');
  if (!env.GITHUB_REPO) missing.push('GITHUB_REPO');
  if (!env.GITHUB_TOKEN) missing.push('GITHUB_TOKEN');

  if (missing.length) {
    throw new Error(`Missing environment/binding: ${missing.join(', ')}`);
  }
}

function getAnswer(answers, key) {
  if (!answers || typeof answers !== 'object') return undefined;

  if (key in answers) return answers[key];

  const normalizedKey = normalizeKey(key);
  if (normalizedKey in answers) return answers[normalizedKey];

  return undefined;
}

function normalizeKey(key) {
  return String(key || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
}

function makeSlug(propertyName, submissionId) {
  const base = String(propertyName || 'villa')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'villa';

  // Usamos los últimos 10 caracteres del submission_id para evitar que
  // pruebas manuales como "manual-menu12-test-..." generen siempre el mismo slug.
  const suffix = String(submissionId || '')
    .replace(/[^a-zA-Z0-9]/g, '')
    .slice(-10)
    .toLowerCase() || createShortSuffix();

  return `${base}-${suffix}`;
}

function createShortSuffix() {
  const bytes = new Uint8Array(4);
  crypto.getRandomValues(bytes);
  return Array.from(bytes)
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
}

function createSecureToken() {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);

  let binary = '';
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }

  return btoa(binary)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');
}

function normalizeBoolean(value) {
  if (typeof value === 'boolean') return value;

  const normalized = String(value || '')
    .trim()
    .toLowerCase();

  if (['true', 'yes', 'sí', 'si', '1', 'on'].includes(normalized)) return true;
  if (['false', 'no', '0', 'off'].includes(normalized)) return false;

  return Boolean(value);
}

function normalizeBooleanOrNull(value) {
  if (isEmpty(value)) return null;
  return normalizeBoolean(value);
}

function cleanValue(value) {
  if (value === undefined || value === null) return '';

  if (Array.isArray(value)) {
    return value.filter((item) => item !== undefined && item !== null && item !== '');
  }

  if (typeof value === 'object') {
    return value;
  }

  return String(value).trim();
}

function isEmpty(value) {
  if (value === undefined || value === null) return true;
  if (typeof value === 'string' && value.trim() === '') return true;
  if (Array.isArray(value) && value.length === 0) return true;
  return false;
}

function hasUploadedMaterial(value) {
  if (value === undefined || value === null) return false;

  if (typeof value === 'string') {
    const s = value.trim().toLowerCase();
    if (s === '' || s === 'null' || s === 'undefined' ||
        s === '[]' || s === '{}' || s === 'none') return false;
    return s.length > 0;
  }

  if (Array.isArray(value)) {
    return value.some(item =>
      item !== null && item !== undefined && item !== '' && (
        typeof item === 'object'
          ? !!(item.url || item.name || item.id)
          : String(item).trim().length > 0
      )
    );
  }

  if (typeof value === 'object') {
    return !!(value.url || value.name || value.id);
  }

  return false;
}

function safeError(error) {
  return {
    message: error?.message || 'Unknown error',
    name: error?.name || 'Error'
  };
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      ...corsHeaders()
    }
  });
}

// Human-readable language names for the "provided in X" annotation.
// Keyed by [displayLang][sourceLang].
const LANG_NAMES = {
  en: { en: 'English',  es: 'Spanish',   fr: 'French'   },
  es: { en: 'inglés',   es: 'español',   fr: 'francés'  },
  fr: { en: 'anglais',  es: 'espagnol',  fr: 'français' },
};

// Phrase prepended to the language name when there is a mismatch.
const ACCESS_PROVIDED_IN = {
  en: 'provided in',
  es: 'proporcionado en',
  fr: 'fourni en',
};

const PRIVATE_BOOK_LABELS = {
  en: {
    wifiNetwork:   'WiFi Network',
    wifiPassword:  'WiFi Password',
    privateAccess: 'Private Access Details',
    hostPhone:     'Host Phone',
    doorCode:      'Door Code',
    buildingCode:  'Building Code',
    access:        'Access',
  },
  es: {
    wifiNetwork:   'Red WiFi',
    wifiPassword:  'Contraseña WiFi',
    privateAccess: 'Detalles de acceso privado',
    hostPhone:     'Teléfono del anfitrión',
    doorCode:      'Código de puerta',
    buildingCode:  'Código de edificio',
    access:        'Acceso',
  },
  fr: {
    wifiNetwork:   'Réseau WiFi',
    wifiPassword:  'Mot de passe WiFi',
    privateAccess: "Détails d'accès privé",
    hostPhone:     "Téléphone de l'hôte",
    doorCode:      'Code de porte',
    buildingCode:  "Code d'immeuble",
    access:        'Accès',
  },
};

function normalizePrivateBookLang(value) {
  const lang = String(value || '').trim().toLowerCase();
  return ['en', 'es', 'fr'].includes(lang) ? lang : '';
}

function buildPublicBookUrl(env, slug, lang) {
  const base =
    cleanValue(env.PUBLIC_BOOK_BASE_URL) ||
    'https://yuyitov.github.io/MyGuest';

  const safeBase = String(base).replace(/\/+$/, '');
  const fileName = lang ? `${lang}.html` : 'index.html';

  return `${safeBase}/villas/${encodeURIComponent(slug)}/${fileName}`;
}

function injectPrivateDetailsIntoBookHtml({ html, slug, token, secrets, lang }) {
  let output = String(html || '');

  const sourceLang = secrets._source_lang || '';
  // Treat missing lang param as 'en' (default) so that when the guest link
  // has no ?lang=, the mismatch check doesn't flag en-source as a foreign language.
  const effectiveLang = lang || 'en';
  const privateBlocks = buildPrivateBookBlocks(secrets, effectiveLang, sourceLang);

  output = replacePrivateTarget(output, 'private-wifi-content', privateBlocks.wifi);
  output = replacePrivateTarget(output, 'private-access-content', privateBlocks.access);
  output = replacePrivateTarget(output, 'private-contact-content', privateBlocks.contact);

  output = output.replace(
    'WiFi details are protected and appear only with your secure guest access link.',
    privateBlocks.wifi
      ? 'Your WiFi details for this stay are shown below.'
      : 'WiFi details are protected and appear only with your secure guest access link.'
  );

  output = rewritePrivateLanguageLinks(output, slug, token);
  output = addPrivateRobotsMeta(output);
  output = replacePrivateClientFetchCall(output);

  return output;
}

function buildPrivateBookBlocks(secrets, lang, sourceLang) {
  const lbl = PRIVATE_BOOK_LABELS[lang] || PRIVATE_BOOK_LABELS.en;
  const wifiSsid = cleanValue(secrets.wifi_ssid);
  const wifiPassword = cleanValue(secrets.wifi_password);

  const privateAccessDetails =
    cleanValue(secrets.house_access_private) ||
    cleanValue(secrets.private_access_details) ||
    cleanValue(secrets.private_access_notes);

  const hostPhone = cleanValue(secrets.host_phone);

  const wifi = [
    buildBookPrivateCard(lbl.wifiNetwork, wifiSsid),
    buildBookPrivateCard(lbl.wifiPassword, wifiPassword)
  ].join('');

  // If the form was filled in a different language than the one being viewed,
  // annotate the label so the guest knows the content is in the original language.
  const langMismatch = sourceLang && sourceLang !== lang;
  const accessLabel = langMismatch
    ? `${lbl.privateAccess} — ${ACCESS_PROVIDED_IN[lang] || 'provided in'} ${(LANG_NAMES[lang] || LANG_NAMES.en)[sourceLang] || sourceLang.toUpperCase()}`
    : lbl.privateAccess;

  const access = [
    buildBookPrivateCard(accessLabel, privateAccessDetails, true)
  ].join('');

  const contact = [
    buildBookPrivateCard(lbl.hostPhone, hostPhone)
  ].join('');

  return {
    wifi,
    access,
    contact
  };
}

function buildBookPrivateCard(label, value, multiline = false) {
  if (isEmpty(value)) return '';

  const content = multiline
    ? formatMultiline(value)
    : escapeHtml(value);

  return `
    <div class="private-card">
      <div class="private-card-title">${escapeHtml(label)}</div>
      <div class="private-card-text">${content}</div>
    </div>
  `;
}

function replacePrivateTarget(html, targetId, content) {
  const pattern = new RegExp(
    `<div\\s+id=["']${targetId}["']\\s*>\\s*<\\/div>`,
    'i'
  );

  return String(html || '').replace(
    pattern,
    `<div id="${targetId}">${content || ''}</div>`
  );
}

function addPrivateRobotsMeta(html) {
  let output = String(html || '');

  if (!output.includes('name="robots"')) {
    output = output.replace(
      '</head>',
      '    <meta name="robots" content="noindex,nofollow,noarchive">\n</head>'
    );
  }

  return output;
}

function rewritePrivateLanguageLinks(html, slug, token) {
  const privateBase = `/guest/${encodeURIComponent(slug)}?token=${encodeURIComponent(token)}`;

  let output = String(html || '');

  output = output.replace(
    /href=(["'])(?:\.\/)?(index|en|es|fr)\.html\1/g,
    function (_, quote, page) {
      const langParam = page === 'index' ? '' : `&lang=${encodeURIComponent(page)}`;
      return `href=${quote}${privateBase}${langParam}${quote}`;
    }
  );

  output = output.replace(
    /href=(["'])(?:https?:\/\/[^"']+)?\/?MyGuest\/villas\/[^"']+\/(index|en|es|fr)\.html\1/g,
    function (_, quote, page) {
      const langParam = page === 'index' ? '' : `&lang=${encodeURIComponent(page)}`;
      return `href=${quote}${privateBase}${langParam}${quote}`;
    }
  );

  return output;
}

function replacePrivateClientFetchCall(html) {
  const revealScript = `
        cleanupDynamicContent();

        (function revealServerRenderedPrivateSections() {
            var targetIds = [
                "private-wifi-content",
                "private-access-content",
                "private-contact-content"
            ];

            function isPlaceholderTextLocal(text) {
                var clean = String(text || "").trim();
                return !clean ||
                    clean === "-" ||
                    clean.toLowerCase() === "n/a" ||
                    clean.toLowerCase() === "na" ||
                    clean.toLowerCase() === "none" ||
                    clean.toLowerCase() === "null" ||
                    clean.indexOf("{{") >= 0 ||
                    clean.indexOf("}}") >= 0;
            }

            targetIds.forEach(function (id) {
                var target = document.getElementById(id);
                if (!target || !target.children.length) return;

                var block = target.closest("[data-field-block]");
                if (block) {
                    block.classList.remove("is-hidden");

                    block.querySelectorAll("[data-dynamic]").forEach(function (el) {
                        if (isPlaceholderTextLocal(el.textContent)) {
                            el.classList.add("is-hidden");
                        }
                    });
                }

                var screen = target.closest("[data-hide-if-empty]");
                if (screen) {
                    screen.classList.remove("is-hidden");

                    var screenId = screen.getAttribute("id");
                    if (screenId) {
                        document.querySelectorAll('a[href="#' + screenId + '"]').forEach(function (link) {
                            link.classList.remove("is-hidden");
                        });
                    }
                }
            });
        })();`;

  return String(html || '').replace(
    /cleanupDynamicContent\(\);\s*loadPrivateDetails\(\);/,
    revealScript
  );
}

function renderPrivateGuestHtml({ slug, secrets, updatedAt }) {
  const wifiSsid = cleanValue(secrets.wifi_ssid);
  const wifiPassword = cleanValue(secrets.wifi_password);
  const privateAccessDetails =
    cleanValue(secrets.house_access_private) ||
    cleanValue(secrets.private_access_details) ||
    cleanValue(secrets.private_access_notes);

  const hostPhone = cleanValue(secrets.host_phone);

  const hasPrivateAccessDetails = !isEmpty(privateAccessDetails);

  const cards = [];

  if (!isEmpty(wifiSsid) || !isEmpty(wifiPassword)) {
    cards.push(`
      <section class="card">
        <div class="card-icon">📶</div>
        <div>
          <p class="label">WiFi</p>
          ${!isEmpty(wifiSsid) ? detailRow('Network', wifiSsid) : ''}
          ${!isEmpty(wifiPassword) ? detailRow('Password', wifiPassword, true) : ''}
        </div>
      </section>
    `);
  }

  if (hasPrivateAccessDetails) {
    cards.push(`
      <section class="card">
        <div class="card-icon">🔑</div>
        <div>
          <p class="label">Private Access Details</p>
          <div class="text-block">${formatMultiline(privateAccessDetails)}</div>
        </div>
      </section>
    `);
  }

 

  if (!isEmpty(hostPhone)) {
    cards.push(`
      <section class="card">
        <div class="card-icon">☎️</div>
        <div>
          <p class="label">Host Phone</p>
          <a class="phone" href="tel:${escapeAttribute(hostPhone)}">${escapeHtml(hostPhone)}</a>
        </div>
      </section>
    `);
  }

 
  if (!cards.length) {
    cards.push(`
      <section class="card">
        <div class="card-icon">ℹ️</div>
        <div>
          <p class="label">Private Details</p>
          <p class="muted">No private guest details are available for this property yet.</p>
        </div>
      </section>
    `);
  }

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow,noarchive">
  <title>Private Guest Details</title>
  <style>
    :root {
      --bg: #f7f3ee;
      --card: #ffffff;
      --text: #2d2722;
      --muted: #766b61;
      --border: #eadfd3;
      --accent: #9b6b43;
      --accent-soft: #f0e2d3;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, #fff7ed 0, transparent 34%),
        linear-gradient(180deg, #fbf7f2 0%, var(--bg) 100%);
      color: var(--text);
    }

    .page {
      width: 100%;
      max-width: 520px;
      margin: 0 auto;
      padding: 28px 18px 36px;
    }

    .hero {
      padding: 26px 22px;
      border-radius: 28px;
      background: linear-gradient(135deg, #2d2722 0%, #5f4633 100%);
      color: #fff;
      box-shadow: 0 18px 45px rgba(45, 39, 34, 0.18);
      margin-bottom: 18px;
    }

    .eyebrow {
      margin: 0 0 10px;
      font-size: 12px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      opacity: 0.75;
    }

    h1 {
      margin: 0;
      font-size: 30px;
      line-height: 1.05;
      letter-spacing: -0.04em;
    }

    .hero p:last-child {
      margin: 12px 0 0;
      color: rgba(255,255,255,0.78);
      font-size: 15px;
      line-height: 1.45;
    }

    .card {
      display: grid;
      grid-template-columns: 42px 1fr;
      gap: 14px;
      align-items: start;
      margin-top: 14px;
      padding: 18px;
      border: 1px solid var(--border);
      border-radius: 22px;
      background: rgba(255,255,255,0.88);
      box-shadow: 0 12px 30px rgba(92, 70, 48, 0.08);
      backdrop-filter: blur(8px);
    }

    .card-icon {
      width: 42px;
      height: 42px;
      display: grid;
      place-items: center;
      border-radius: 16px;
      background: var(--accent-soft);
      font-size: 20px;
    }

    .label {
      margin: 0 0 10px;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--accent);
      font-weight: 800;
    }

    .detail {
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid #f0e8df;
    }

    .detail:first-of-type {
      margin-top: 0;
      padding-top: 0;
      border-top: 0;
    }

    .detail-title {
      display: block;
      margin-bottom: 4px;
      font-size: 12px;
      color: var(--muted);
      font-weight: 700;
    }

    .detail-value {
      overflow-wrap: anywhere;
      font-size: 18px;
      line-height: 1.35;
      font-weight: 700;
    }

    .secret {
      display: inline-block;
      padding: 6px 10px;
      border-radius: 12px;
      background: #f8efe6;
      border: 1px solid #ead7c2;
      letter-spacing: 0.02em;
    }

    .text-block {
      white-space: normal;
      overflow-wrap: anywhere;
      font-size: 16px;
      line-height: 1.6;
      color: #3d342d;
    }

    .text-block p {
      margin: 0 0 10px;
    }

    .text-block p:last-child {
      margin-bottom: 0;
    }

    .phone {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      min-height: 46px;
      padding: 12px 14px;
      border-radius: 14px;
      background: var(--accent);
      color: #fff;
      text-decoration: none;
      font-weight: 800;
      overflow-wrap: anywhere;
      text-align: center;
    }

    .muted {
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
    }

    .footer {
      margin-top: 20px;
      text-align: center;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }

    .security {
      margin-top: 16px;
      padding: 14px 16px;
      border-radius: 18px;
      background: #fff8ef;
      color: #7a5739;
      border: 1px solid #ecdcc8;
      font-size: 13px;
      line-height: 1.5;
    }

    @media (max-width: 420px) {
      .page {
        padding: 18px 12px 28px;
      }

      .hero {
        padding: 22px 18px;
        border-radius: 24px;
      }

      h1 {
        font-size: 27px;
      }

      .card {
        grid-template-columns: 36px 1fr;
        gap: 12px;
        padding: 16px;
        border-radius: 20px;
      }

      .card-icon {
        width: 36px;
        height: 36px;
        border-radius: 14px;
        font-size: 18px;
      }

      .detail-value {
        font-size: 17px;
      }
    }
  </style>
</head>
<body>
  <main class="page">
    <header class="hero">
      <p class="eyebrow">Private guest access</p>
      <h1>Details for your stay</h1>
      <p>Use this secure page for WiFi, access instructions, codes, and private host details.</p>
    </header>

    ${cards.join('\n')}

    <div class="security">
      This page is protected by a private token. Do not share this link publicly.
    </div>

    <footer class="footer">
      MyGuest private access${updatedAt ? ` · Updated ${escapeHtml(updatedAt)}` : ''}<br>
      ${escapeHtml(slug)}
    </footer>
  </main>
</body>
</html>`;
}

function privateErrorHtml(message, status = 403) {
  const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow,noarchive">
  <title>Private Access</title>
  <style>
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 20px;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f7f3ee;
      color: #2d2722;
    }

    .box {
      width: 100%;
      max-width: 420px;
      padding: 28px;
      border-radius: 26px;
      background: #fff;
      border: 1px solid #eadfd3;
      box-shadow: 0 16px 40px rgba(92, 70, 48, 0.12);
      text-align: center;
    }

    .icon {
      width: 54px;
      height: 54px;
      display: grid;
      place-items: center;
      margin: 0 auto 16px;
      border-radius: 18px;
      background: #f0e2d3;
      font-size: 26px;
    }

    h1 {
      margin: 0 0 10px;
      font-size: 25px;
      letter-spacing: -0.03em;
    }

    p {
      margin: 0;
      color: #766b61;
      line-height: 1.5;
    }
  </style>
</head>
<body>
  <main class="box">
    <div class="icon">🔒</div>
    <h1>Private access unavailable</h1>
    <p>${escapeHtml(message)}</p>
  </main>
</body>
</html>`;

  return new Response(html, {
    status,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'no-store, no-cache, must-revalidate, private',
      'pragma': 'no-cache',
      'x-robots-tag': 'noindex, nofollow, noarchive',
      'x-content-type-options': 'nosniff',
      'referrer-policy': 'no-referrer',
      'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; script-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none';"
    }
  });
}

function detailRow(label, value, isSecret = false) {
  if (isEmpty(value)) return '';

  const className = isSecret ? 'detail-value secret' : 'detail-value';

  return `
    <div class="detail">
      <span class="detail-title">${escapeHtml(label)}</span>
      <span class="${className}">${escapeHtml(value)}</span>
    </div>
  `;
}

function formatMultiline(value) {
  return String(value || '')
    .split(/\n{2,}/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean)
    .map((paragraph) => `<p>${escapeHtml(paragraph).replace(/\n/g, '<br>')}</p>`)
    .join('');
}

function textContainsValue(text, value) {
  if (isEmpty(text) || isEmpty(value)) return false;

  const normalizedText = normalizeComparableText(text);
  const normalizedValue = normalizeComparableText(value);

  return normalizedText.includes(normalizedValue);
}

function normalizeComparableText(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/\s+/g, '')
    .replace(/[^a-z0-9]/g, '');
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function escapeAttribute(value) {
  return escapeHtml(value).replace(/`/g, '&#096;');
}

function corsHeaders() {
  return {
    'access-control-allow-origin': 'https://myguestguide.com',
    'access-control-allow-methods': 'GET, POST, OPTIONS',
    'access-control-allow-headers': 'Content-Type, Authorization'
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// BLOQUE 16.1-B — Stripe · Notify · Email (Resend)
// Env vars nuevas requeridas:
//   STRIPE_WEBHOOK_SECRET  — secreto del webhook en Stripe dashboard
//   RESEND_API_KEY         — API key de Resend
//   FROM_EMAIL             — remitente, obligatorio (ej: "MyGuest <hello@myguestguide.com>")
//   TALLY_FORM_URL         — URL base del formulario Tally (obligatorio)
//   NOTIFY_SECRET          — secreto requerido para el endpoint /notify
// ═══════════════════════════════════════════════════════════════════════════

async function handleStripeWebhook(request, env) {
  if (!env.STRIPE_WEBHOOK_SECRET) {
    return jsonResponse({ ok: false, error: 'Stripe webhook not configured' }, 500);
  }

  const rawBody = await request.text();
  const signatureHeader = request.headers.get('stripe-signature') || '';

  const valid = await validateStripeSignature(rawBody, signatureHeader, env.STRIPE_WEBHOOK_SECRET);
  if (!valid) {
    return jsonResponse({ ok: false, error: 'Invalid Stripe signature' }, 400);
  }

  let event;
  try {
    event = JSON.parse(rawBody);
  } catch {
    return jsonResponse({ ok: false, error: 'Invalid JSON' }, 400);
  }

  const type = event?.type;
  if (type !== 'checkout.session.completed' && type !== 'payment_intent.succeeded') {
    return jsonResponse({ ok: true, ignored: true, type });
  }

  const session = event?.data?.object || {};

  // Filtro por producto: la cuenta de Stripe es compartida con otros productos
  // (HMU Link), así que este webhook recibe TODAS las ventas de la cuenta.
  // Solo checkout.session.completed trae payment_link; payment_intent.succeeded
  // no se puede atribuir a un producto, así que se ignora con el filtro activo.
  const expectedPaymentLink = (env.STRIPE_PAYMENT_LINK_ID || '').trim();
  if (expectedPaymentLink) {
    if (type !== 'checkout.session.completed') {
      return jsonResponse({ ok: true, ignored: true, reason: 'unattributable_event_type' });
    }
    if ((session.payment_link || '') !== expectedPaymentLink) {
      return jsonResponse({ ok: true, ignored: true, reason: 'other_product' });
    }
  }

  const paymentIntentId =
    type === 'checkout.session.completed'
      ? (session.payment_intent || session.id || '')
      : (session.id || '');
  const customerEmail =
    session.customer_email ||
    session.customer_details?.email ||
    session.receipt_email ||
    '';
  const amountTotal = session.amount_total ?? session.amount ?? 0;
  const currency = session.currency || '';

  if (!paymentIntentId) {
    return jsonResponse({ ok: false, error: 'Missing payment_intent id' }, 400);
  }

  const processedKey = `processed:${paymentIntentId}`;
  const alreadyProcessed = await env.MYGUEST_KV.get(processedKey).catch(() => null);
  if (alreadyProcessed) {
    return jsonResponse({ ok: true, idempotent: true, paymentIntentId });
  }

  const now = new Date().toISOString();
  const orderId = paymentIntentId;

  // 1. Guardar order record — si falla, Stripe reintenta
  try {
    await env.MYGUEST_KV.put(`order:${orderId}`, JSON.stringify({
      payment_intent_id: paymentIntentId,
      customer_email: customerEmail,
      email: customerEmail,
      amount: amountTotal,
      currency,
      stripe_event_type: type,
      status: 'paid',
      created_at: now
    }));
  } catch (err) {
    console.error('order record save failed:', safeError(err));
    return jsonResponse({ ok: false, error: 'Failed to save order record' }, 500);
  }

  // 2. Sin customer_email: marcar processed (no hay email que enviar)
  if (!customerEmail) {
    console.error(`stripe: no customer_email for paymentIntent=${paymentIntentId}`);
    await env.MYGUEST_KV.put(processedKey, '1', { expirationTtl: 604800 });
    return jsonResponse({ ok: true, paymentIntentId, hasEmail: false });
  }

  // 3. RESEND_API_KEY obligatorio — Stripe reintenta si falta
  if (!env.RESEND_API_KEY) {
    return jsonResponse({ ok: false, error: 'RESEND_API_KEY not configured' }, 500);
  }

  // 4. TALLY_FORM_URL obligatorio — sin él el cliente no recibe link real
  const baseForm = (env.TALLY_FORM_URL || '').trim();
  if (!baseForm) {
    return jsonResponse({ ok: false, error: 'TALLY_FORM_URL not configured' }, 500);
  }

  // 5. Construir URL del formulario con order_id y customer_email
  const formUrl = `${baseForm}${baseForm.includes('?') ? '&' : '?'}order_id=${encodeURIComponent(orderId)}&customer_email=${encodeURIComponent(customerEmail)}`;

  // 6. Enviar email post-pago — si falla, NO marcar processed (Stripe reintenta)
  try {
    await sendEmail({
      env,
      to: customerEmail,
      subject: 'Complete your MyGuest welcome book — one form to go',
      html: buildFormEmail({ formUrl })
    });
  } catch (err) {
    console.error('post-payment email failed:', safeError(err));
    return jsonResponse({ ok: false, error: 'Failed to send post-payment email' }, 500);
  }

  // 7. Solo marcar processed después de order guardado + email enviado
  await env.MYGUEST_KV.put(processedKey, '1', { expirationTtl: 604800 });

  return jsonResponse({ ok: true, paymentIntentId, hasEmail: true });
}

async function handleNotify(request, env) {
  const notifySecret = (env.NOTIFY_SECRET || '').trim();
  if (!notifySecret) {
    return jsonResponse({ ok: false, error: 'NOTIFY_SECRET not configured' }, 500);
  }

  const authHeader = request.headers.get('authorization') || '';
  const provided = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : '';
  if (!timingSafeEqual(provided, notifySecret)) {
    return jsonResponse({ ok: false, error: 'Unauthorized' }, 401);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ ok: false, error: 'Invalid JSON' }, 400);
  }

  const slug = (body?.slug || '').trim();
  if (!slug) {
    return jsonResponse({ ok: false, error: 'Missing slug' }, 400);
  }

  const deliveryKey = `delivery:${slug}`;
  const delivery = await env.MYGUEST_KV.get(deliveryKey, { type: 'json' }).catch(() => null);

  if (!delivery) {
    return jsonResponse({ ok: false, error: 'delivery record not found', slug }, 404);
  }

  // Idempotencia — no reenviar si ya fue entregado
  if (delivery.status === 'delivered') {
    return jsonResponse({ ok: true, slug, idempotent: true, alreadyDelivered: true });
  }

  const guestAccessUrl = delivery.guest_access_url || '';
  const customerEmail  = delivery.customer_email   || '';

  // Derive print URL from guestAccessUrl: same token, /print/ instead of /guest/
  const printUrl = guestAccessUrl ? guestAccessUrl.replace('/guest/', '/print/') : '';

  // Correction token — idempotent: reuse existing record for this slug
  const correctionKey = `correction:${slug}`;
  let correctionRecord = await env.MYGUEST_KV.get(correctionKey, { type: 'json' }).catch(() => null);
  if (!correctionRecord) {
    const correctionToken = createSecureToken();
    correctionRecord = {
      slug,
      customer_email: customerEmail,
      token: correctionToken,
      used: false,
      created_at: new Date().toISOString(),
      used_at: null
    };
    await env.MYGUEST_KV.put(correctionKey, JSON.stringify(correctionRecord))
      .catch(err => console.error('correction record save failed (non-fatal):', safeError(err)));
  }
  const correctionUrl = `${new URL(request.url).origin}/correct/${encodeURIComponent(slug)}?token=${correctionRecord.token}`;

  if (!customerEmail) {
    console.error(`notify: no customer_email for slug=${slug}`);
    await env.MYGUEST_KV.put(deliveryKey, JSON.stringify({
      ...delivery, status: 'no_email', notified_at: new Date().toISOString()
    })).catch(() => {});
    return jsonResponse({ ok: false, error: 'no customer_email on delivery record', slug }, 422);
  }

  if (!env.RESEND_API_KEY) {
    return jsonResponse({ ok: false, error: 'RESEND_API_KEY not configured' }, 500);
  }

  try {
    await sendEmail({
      env,
      to: customerEmail,
      subject: 'Your MyGuest welcome book is ready',
      html: buildDeliveryEmail({ guestAccessUrl, printUrl, correctionUrl })
    });
  } catch (err) {
    console.error('delivery email failed:', safeError(err));
    await env.MYGUEST_KV.put(deliveryKey, JSON.stringify({
      ...delivery,
      print_url: printUrl,
      status: 'email_failed',
      notified_at: new Date().toISOString()
    })).catch(() => {});
    return jsonResponse({ ok: false, error: 'Failed to send delivery email', slug }, 500);
  }

  // ok:true solo cuando el email realmente se envió
  await env.MYGUEST_KV.put(deliveryKey, JSON.stringify({
    ...delivery,
    print_url: printUrl,
    correction_token: correctionRecord?.token || null,
    status: 'delivered',
    notified_at: new Date().toISOString()
  })).catch(() => {});

  // Actualizar order a delivered (no-fatal)
  if (delivery.order_id) {
    const orderRecord = await env.MYGUEST_KV.get(`order:${delivery.order_id}`, { type: 'json' }).catch(() => null);
    if (orderRecord) {
      await env.MYGUEST_KV.put(`order:${delivery.order_id}`, JSON.stringify({
        ...orderRecord,
        status: 'delivered',
        delivered_at: new Date().toISOString()
      })).catch(err => console.error('order delivered status update failed (non-fatal):', safeError(err)));
    }
  }

  return jsonResponse({ ok: true, slug, emailSent: true });
}

async function validateStripeSignature(rawBody, signatureHeader, secret) {
  if (!signatureHeader || !secret) return false;

  const parts = {};
  for (const part of signatureHeader.split(',')) {
    const idx = part.indexOf('=');
    if (idx > 0) parts[part.slice(0, idx)] = part.slice(idx + 1);
  }

  const timestamp = parts['t'];
  const signature  = parts['v1'];
  if (!timestamp || !signature) return false;

  if (Math.abs(Date.now() / 1000 - parseInt(timestamp, 10)) > 300) return false;

  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const sigBytes = await crypto.subtle.sign(
    'HMAC', key, encoder.encode(`${timestamp}.${rawBody}`)
  );
  const expectedHex = Array.from(new Uint8Array(sigBytes))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');

  return timingSafeEqual(expectedHex, signature);
}

async function checkRateLimit(env, key, limit, ttlSeconds) {
  if (!env.MYGUEST_KV) return true;
  try {
    const current = parseInt(await env.MYGUEST_KV.get(key) || '0', 10);
    if (current >= limit) return false;
    await env.MYGUEST_KV.put(key, String(current + 1), { expirationTtl: ttlSeconds });
    return true;
  } catch {
    return true;
  }
}

function timingSafeEqual(a, b) {
  const sa = String(a || '');
  const sb = String(b || '');
  if (sa.length !== sb.length) return false;
  let diff = 0;
  for (let i = 0; i < sa.length; i++) {
    diff |= sa.charCodeAt(i) ^ sb.charCodeAt(i);
  }
  return diff === 0;
}

async function sendEmail({ env, to, subject, html }) {
  const apiKey = (env.RESEND_API_KEY || '').trim();
  const from   = (env.FROM_EMAIL    || '').trim();

  if (!apiKey) throw new Error('RESEND_API_KEY not configured');
  // Sin fallback a proposito: un remitente por defecto apunta a un dominio no
  // verificado en Resend, que rechaza el envio con un 403 dificil de leer.
  // Mejor fallar aqui, con el nombre de la variable que falta.
  if (!from)   throw new Error('FROM_EMAIL not configured');
  if (!to)     throw new Error('sendEmail: missing recipient');

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ from, to, subject, html })
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Resend error ${response.status}: ${text}`);
  }

  return response.json();
}

function buildAlertEmail({ propertyName, clientName, customerEmail, slug, submissionId, now, existingBookFile, existingBookPhotos }) {
  const reviewParams = [
    ['flow_type',              'manual_extraction_review'],
    ['original_submission_id', submissionId   || ''],
    ['slug',                   slug           || ''],
    ['property_name',          propertyName   || ''],
    ['client_name',            clientName     || ''],
    ['customer_email',         customerEmail  || ''],
  ].filter(([, v]) => v);
  const reviewUrl = `https://tally.so/r/yP1y9B?${new URLSearchParams(reviewParams).toString()}`;
  const tallySubmissionsUrl = 'https://tally.so/forms/MedpvA/submissions';

  const rows = [
    ['Propiedad',     escapeHtml(propertyName)],
    ['Cliente',       escapeHtml(clientName || '—')],
    ['Email cliente', escapeHtml(customerEmail || '—')],
    ['Slug',          escapeHtml(slug)],
    ['Submission ID', escapeHtml(submissionId)],
    ['Recibido',      escapeHtml(now)],
  ].map(([label, value]) =>
    `<tr><td style="padding:6px 12px;color:#888;white-space:nowrap">${label}</td>` +
    `<td style="padding:6px 12px;color:#111;font-family:monospace">${value}</td></tr>`
  ).join('');

  function fileListHtml(files, heading) {
    const list = Array.isArray(files) ? files : [];
    const items = list.filter(f => f && f.url && f.name);
    if (!items.length) return '';
    const lis = items.map(f => {
      const name = escapeHtml(String(f.name));
      const url  = escapeAttribute(String(f.url));
      const mime = f.mimeType ? ` <span style="color:#888;font-size:12px">${escapeHtml(String(f.mimeType))}</span>` : '';
      return `<li style="margin-bottom:6px">` +
        `<a href="${url}" target="_blank" rel="noopener noreferrer" ` +
        `style="color:#2D6A73;font-weight:600;word-break:break-all">${name}</a>${mime}` +
        `</li>`;
    }).join('');
    return `<div style="margin-bottom:14px">` +
      `<div style="font-size:11px;font-weight:700;letter-spacing:0.8px;color:#666;` +
      `text-transform:uppercase;margin-bottom:6px">${escapeHtml(heading)}</div>` +
      `<ul style="margin:0;padding-left:18px;font-size:14px;color:#111;line-height:1.6">${lis}</ul>` +
      `</div>`;
  }

  const filesHtml = fileListHtml(existingBookFile,   'Guía existente (PDF / Word)') +
                    fileListHtml(existingBookPhotos,  'Fotos / capturas del cliente');

  const filesSectionHtml = filesHtml
    ? `<div style="background:#f0f7f7;border-left:3px solid #2D6A73;border-radius:0 6px 6px 0;` +
      `padding:16px 20px;margin:0 0 24px">` +
      `<p style="font-size:11px;font-weight:700;letter-spacing:1px;color:#2D6A73;margin:0 0 12px">` +
      `ARCHIVOS DEL CLIENTE — DESCARGA ANTES DE CONTINUAR</p>` +
      filesHtml +
      `<p style="font-size:12px;color:#888;margin:10px 0 0">` +
      `También disponibles en <a href="${escapeAttribute(tallySubmissionsUrl)}" ` +
      `target="_blank" rel="noopener noreferrer" style="color:#2D6A73">Tally → Submissions</a> ` +
      `bajo submission <span style="font-family:monospace">${escapeHtml(submissionId)}</span>.</p>` +
      `</div>`
    : '';

  return `<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:40px 0">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0"
           style="background:#fff;border-radius:12px;padding:40px;max-width:560px">
      <tr><td>
        <p style="font-size:12px;font-weight:700;letter-spacing:1px;color:#59C3C3;margin:0 0 8px">MYGUEST — ALERTA INTERNA</p>
        <h1 style="font-size:20px;font-weight:700;color:#111;margin:0 0 16px">
          Revisión manual pendiente
        </h1>
        <p style="color:#444;line-height:1.6;margin:0 0 24px">
          Un cliente subió archivos adjuntos. Descarga los archivos, extrae la información
          y completa el formulario de revisión antes de generar la guía.
        </p>
        ${filesSectionHtml}
        <table style="width:100%;border-collapse:collapse;background:#f9f9f9;border-radius:8px;margin:0 0 24px">${rows}</table>
        <p style="text-align:center;margin:0">
          <a href="${escapeAttribute(reviewUrl)}"
             style="background:#2D6A73;color:#fff;padding:14px 28px;border-radius:8px;
                    text-decoration:none;font-size:15px;font-weight:600;display:inline-block">
            Abrir formulario de revisión →
          </a>
        </p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>`;
}

function buildFormEmail({ formUrl }) {
  const btn = formUrl
    ? `<p style="text-align:center;margin:32px 0">
         <a href="${escapeAttribute(formUrl)}"
            style="background:#111;color:#fff;padding:14px 28px;border-radius:8px;
                   text-decoration:none;font-size:16px;font-weight:600">
           Fill out the form →
         </a>
       </p>`
    : '<p style="color:#444">Please check your email for further instructions.</p>';

  return `<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:40px 0">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0"
           style="background:#fff;border-radius:12px;padding:40px;max-width:560px">
      <tr><td>
        <h1 style="font-size:22px;font-weight:700;color:#111;margin:0 0 16px">
          One step left — tell us about your property
        </h1>
        <p style="color:#444;line-height:1.6;margin:0 0 16px">
          Thank you for your purchase. To build your personalized welcome book,
          please fill out the short form below. It takes about 5 minutes.
        </p>
        ${btn}
        <p style="color:#999;font-size:13px;margin:16px 0 0;text-align:center">
          This link is personal and tied to your purchase. Please do not forward it.
        </p>
        <p style="color:#999;font-size:13px;margin:24px 0 0">
          If you have any questions, just reply to this email.
        </p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>`;
}

function buildDeliveryEmail({ guestAccessUrl, printUrl, correctionUrl }) {
  const btn = (href, label, description) =>
    href
      ? `<div style="margin:0 0 16px 0;padding:20px;background:#f9f9f9;border-radius:8px">
           <a href="${escapeAttribute(href)}"
              style="color:#2D6A73;font-size:16px;font-weight:700;text-decoration:none">${label}</a>
           <p style="color:#666;font-size:13px;margin:6px 0 0;line-height:1.5">${description}</p>
         </div>`
      : '';

  return `<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:40px 0">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0"
           style="background:#fff;border-radius:12px;padding:40px;max-width:560px">
      <tr><td>
        <h1 style="font-size:22px;font-weight:700;color:#111;margin:0 0 8px">
          Your welcome book is ready
        </h1>
        <p style="color:#666;line-height:1.6;margin:0 0 28px;font-size:15px">
          Your personalized MyGuest guide has been generated with everything your guests need.
          Use the links below to access your guide and share the guest link with your guests.
        </p>
        ${btn(guestAccessUrl,
          'Open digital guide →',
          'Full guide with WiFi, access codes, and all stay details. Send this link to your guests.')}
        ${btn(printUrl,
          'Open printable guide →',
          'Host print-ready version with all details, including WiFi and access codes. Open it to print or save as PDF before sharing.')}
        ${btn(correctionUrl,
          'Request corrections →',
          'One free correction round is included. Use this link once to request changes. We review correction requests manually and will apply approved changes as soon as possible.')}
        <div style="background:#faf7f4;border:1px solid #ddd5cc;border-radius:8px;padding:14px 16px;margin:24px 0 0">
          <p style="color:#776150;font-size:13px;margin:0;line-height:1.6">
            Both links contain your complete stay information. Keep them private and share only with your guests.
          </p>
        </div>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>`;
}

// ─── Flujo de correcciones one-time ──────────────────────────────────────────

async function handleCorrectionAccess(request, env) {
  if (!env.MYGUEST_KV) {
    return correctionErrorHtml('Service unavailable. Please try again later.', 500);
  }

  const url = new URL(request.url);
  const token = url.searchParams.get('token') || '';
  const match = url.pathname.match(/^\/correct\/([^/]+)$/);
  const slug = match ? decodeURIComponent(match[1]) : null;

  if (!slug || !token) {
    return correctionErrorHtml('This link is not valid.', 400);
  }

  const record = await env.MYGUEST_KV.get(`correction:${slug}`, { type: 'json' }).catch(() => null);

  if (!record || !timingSafeEqual(token, record.token)) {
    return correctionErrorHtml('This link is not valid.', 404);
  }

  if (record.used) {
    return correctionErrorHtml(
      "You&#39;ve already used your included correction request. For any additional changes, please contact us by email.",
      200
    );
  }

  const tallyUrl =
    'https://tally.so/r/Ek6EM2' +
    '?slug=' + encodeURIComponent(slug) +
    '&correction_token=' + encodeURIComponent(record.token) +
    '&customer_email=' + encodeURIComponent(record.customer_email || '') +
    '&form_type=corrections';

  return correctionPageHtml(tallyUrl);
}

async function handleCorrectionsSubmission(normalized, env) {
  const now = new Date().toISOString();
  const slug           = cleanValue(getAnswer(normalized.answers, 'slug'))             || '';
  const correctionToken = cleanValue(getAnswer(normalized.answers, 'correction_token')) || '';

  if (!slug || !correctionToken) {
    return jsonResponse({ ok: false, error: 'Missing slug or correction_token' }, 400);
  }

  const correctionKey = `correction:${slug}`;
  const record = await env.MYGUEST_KV.get(correctionKey, { type: 'json' }).catch(() => null);

  if (!record || !timingSafeEqual(correctionToken, record.token)) {
    return jsonResponse({ ok: false, error: 'Invalid correction token', slug }, 403);
  }

  if (record.used) {
    return jsonResponse({ ok: true, idempotent: true, slug });
  }

  await env.MYGUEST_KV.put(correctionKey, JSON.stringify({
    ...record,
    used: true,
    used_at: now
  })).catch(err => console.error('correction mark used failed (non-fatal):', safeError(err)));

  if (env.ALERT_EMAIL && env.RESEND_API_KEY) {
    const corrections = {
      'Welcome message':  cleanValue(getAnswer(normalized.answers, 'welcome_message'))  || '',
      'Property details': cleanValue(getAnswer(normalized.answers, 'property_details')) || '',
      'House rules':      cleanValue(getAnswer(normalized.answers, 'house_rules'))      || '',
      'Recommendations':  cleanValue(getAnswer(normalized.answers, 'recommendations'))  || '',
      'Anything else':    cleanValue(getAnswer(normalized.answers, 'anything_else'))    || '',
    };
    await sendEmail({
      env,
      to: env.ALERT_EMAIL,
      subject: `[MyGuest] Corrections requested: ${slug}`,
      html: buildCorrectionsAlertEmail({ slug, corrections, customerEmail: record.customer_email, now, publicBookBaseUrl: env.PUBLIC_BOOK_BASE_URL || 'https://myguestguide.com' })
    }).catch(err => console.error('corrections alert email failed (non-fatal):', safeError(err)));
  }

  return jsonResponse({ ok: true, slug });
}

function buildCorrectionsAlertEmail({ slug, corrections, customerEmail, now, publicBookBaseUrl = 'https://myguestguide.com' }) {
  const rows = Object.entries(corrections)
    .filter(([, v]) => v)
    .map(([label, value]) =>
      `<tr>
        <td style="padding:8px 12px;font-weight:600;color:#444;vertical-align:top;width:140px;border-top:1px solid #eee">${escapeHtml(label)}</td>
        <td style="padding:8px 12px;color:#222;white-space:pre-wrap;border-top:1px solid #eee">${escapeHtml(value)}</td>
      </tr>`
    ).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:40px 0">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0"
           style="background:#fff;border-radius:12px;padding:40px;max-width:560px">
      <tr><td>
        <h1 style="font-size:20px;font-weight:700;color:#111;margin:0 0 8px">Corrections requested</h1>
        <p style="color:#666;font-size:14px;margin:0 0 24px;line-height:1.6">
          <strong>Guide:</strong> ${escapeHtml(slug)}<br>
          <strong>Customer:</strong> ${escapeHtml(customerEmail || '—')}<br>
          <strong>At:</strong> ${escapeHtml(now)}<br>
          <strong>View guide:</strong> <a href="${escapeAttribute(publicBookBaseUrl)}/villas/${encodeURIComponent(slug)}/en.html"
            style="color:#2D6A73">${escapeHtml(publicBookBaseUrl)}/villas/${escapeHtml(slug)}/en.html</a>
        </p>
        ${rows
          ? `<table width="100%" cellpadding="0" cellspacing="0"
                    style="border:1px solid #eee;border-radius:8px;border-collapse:collapse">
               ${rows}
             </table>`
          : '<p style="color:#999;font-size:14px">No correction fields were filled in.</p>'
        }
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>`;
}

function correctionErrorHtml(message, status = 400) {
  const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow,noarchive">
  <title>Correction Request</title>
  <style>
    body { margin:0; min-height:100vh; display:grid; place-items:center; padding:20px;
           font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;
           background:#f7f3ee; color:#2d2722; }
    .box { width:100%; max-width:420px; padding:28px; border-radius:26px;
           background:#fff; border:1px solid #eadfd3;
           box-shadow:0 16px 40px rgba(92,70,48,0.12); text-align:center; }
    .icon { width:54px; height:54px; display:grid; place-items:center;
            margin:0 auto 16px; border-radius:18px; background:#f0e2d3; font-size:26px; }
    h1 { margin:0 0 10px; font-size:20px; letter-spacing:-0.03em; }
    p { margin:0; color:#766b61; line-height:1.6; font-size:15px; }
  </style>
</head>
<body>
  <main class="box">
    <div class="icon">✉️</div>
    <h1>Correction Request</h1>
    <p>${message}</p>
  </main>
</body>
</html>`;
  return new Response(html, {
    status,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'no-store, no-cache, must-revalidate, private',
      'pragma': 'no-cache',
      'x-robots-tag': 'noindex, nofollow, noarchive',
      'x-content-type-options': 'nosniff',
      'referrer-policy': 'no-referrer'
    }
  });
}

function correctionPageHtml(tallyUrl) {
  const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow,noarchive">
  <title>Request Corrections</title>
  <style>
    body { margin:0; min-height:100vh; display:grid; place-items:center; padding:20px;
           font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;
           background:#f7f3ee; color:#2d2722; }
    .box { width:100%; max-width:440px; padding:32px; border-radius:26px;
           background:#fff; border:1px solid #eadfd3;
           box-shadow:0 16px 40px rgba(92,70,48,0.12); text-align:center; }
    .icon { width:54px; height:54px; display:grid; place-items:center;
            margin:0 auto 16px; border-radius:18px; background:#e8f0f1; font-size:26px; }
    h1 { margin:0 0 10px; font-size:22px; letter-spacing:-0.03em; }
    p { margin:0 0 24px; color:#766b61; line-height:1.6; font-size:15px; }
    .btn { display:inline-block; background:#2D6A73; color:#fff; font-size:16px;
           font-weight:700; text-decoration:none; padding:14px 28px;
           border-radius:12px; letter-spacing:-0.01em; }
    .note { margin-top:20px !important; margin-bottom:0 !important;
            font-size:12px; color:#aaa; line-height:1.5; }
  </style>
</head>
<body>
  <main class="box">
    <div class="icon">✏️</div>
    <h1>Request corrections</h1>
    <p>Use the form below to describe what you&#39;d like to change in your guide.<br>
       This link can only be used once.</p>
    <a class="btn" href="${escapeAttribute(tallyUrl)}">Open corrections form →</a>
    <p class="note">One free correction round is included with your guide.</p>
  </main>
</body>
</html>`;
  return new Response(html, {
    status: 200,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'no-store, no-cache, must-revalidate, private',
      'pragma': 'no-cache',
      'x-robots-tag': 'noindex, nofollow, noarchive',
      'x-content-type-options': 'nosniff',
      'referrer-policy': 'no-referrer'
    }
  });
}

// ─── Flujo de revisión manual ─────────────────────────────────────────────────

async function handleManualExtractionReview(request, normalized, env) {
  const now = new Date().toISOString();
  const reviewSubmissionId = normalized.submission_id || `review-${Date.now()}`;

  const originalSubmissionId = cleanValue(getAnswer(normalized.answers, 'original_submission_id')) || '';
  const slug                  = cleanValue(getAnswer(normalized.answers, 'slug')) || '';

  if (!originalSubmissionId) {
    return jsonResponse({ ok: false, error: 'Missing original_submission_id in review form' }, 400);
  }
  if (!slug) {
    return jsonResponse({ ok: false, error: 'Missing slug in review form' }, 400);
  }

  const indexKey    = `subm-${originalSubmissionId}`;
  const intakeKey   = `intake:${slug}`;
  const privateKey  = `priv-${slug}`;
  const deliveryKey = `delivery:${slug}`;

  const [index, intakeRecord, privateRecord, deliveryRecord] = await Promise.all([
    env.MYGUEST_KV.get(indexKey,    { type: 'json' }).catch(() => null),
    env.MYGUEST_KV.get(intakeKey,   { type: 'json' }).catch(() => null),
    env.MYGUEST_KV.get(privateKey,  { type: 'json' }).catch(() => null),
    env.MYGUEST_KV.get(deliveryKey, { type: 'json' }).catch(() => null),
  ]);

  if (!index) {
    return jsonResponse({ ok: false, error: 'Original submission not found', submission_id: originalSubmissionId }, 404);
  }
  if (!privateRecord) {
    return jsonResponse({ ok: false, error: 'Private record not found', slug }, 404);
  }
  const ALLOWED_REVIEW_STATUSES = new Set(['needs_manual_extraction', 'manual_extraction_incomplete']);
  if (!ALLOWED_REVIEW_STATUSES.has(index.status)) {
    return jsonResponse({
      ok: false,
      error: 'Submission is not awaiting manual extraction or re-review',
      current_status: index.status
    }, 409);
  }

  // Check if Vero confirmed the extraction is complete before doing anything irreversible.
  // isManualExtractionApproved tries multiple candidate keys in priority order and requires
  // an unambiguous affirmative answer. Conservative default: missing or ambiguous → block.
  const extractionComplete = isManualExtractionApproved(normalized.answers);

  if (!extractionComplete) {
    index.status = 'manual_extraction_incomplete';
    index.last_updated_at = now;
    await env.MYGUEST_KV.put(indexKey, JSON.stringify(index)).catch(() => {});

    if (intakeRecord) {
      await env.MYGUEST_KV.put(intakeKey, JSON.stringify({
        ...intakeRecord,
        status: 'manual_extraction_incomplete',
        review_submission_id: reviewSubmissionId,
        manual_review_at: now
      })).catch(() => {});
    }

    if (deliveryRecord) {
      await env.MYGUEST_KV.put(deliveryKey, JSON.stringify({
        ...deliveryRecord,
        status: 'manual_extraction_incomplete',
        manual_review_at: now
      })).catch(() => {});
    }

    const orderId = deliveryRecord?.order_id;
    if (orderId) {
      try {
        const orderRecord = await env.MYGUEST_KV.get(`order:${orderId}`, { type: 'json' }).catch(() => null);
        if (orderRecord) {
          await env.MYGUEST_KV.put(`order:${orderId}`, JSON.stringify({
            ...orderRecord,
            status: 'manual_extraction_incomplete',
            last_updated_at: now
          }));
        }
      } catch (err) {
        console.error('review: order status update failed (non-fatal):', safeError(err));
      }
    }

    console.log('manual extraction incomplete:', JSON.stringify({ slug, original_submission_id: originalSubmissionId }));

    return jsonResponse({
      ok: true,
      status: 'manual_extraction_incomplete',
      slug,
      original_submission_id: originalSubmissionId,
      message: 'Extraction marked as incomplete. Book generation was not triggered. Submit again with "Si — lista para generar" when ready.'
    });
  }

  // Merge: original client answers + Vero's manually extracted answers
  const originalAnswers = intakeRecord?.original_answers || {};
  const reviewAnswers   = normalized.answers;
  const { merged, conflicts, additions } = mergeAnswersForReview(originalAnswers, reviewAnswers);

  console.log('manual extraction merge:', JSON.stringify({
    slug,
    original_submission_id: originalSubmissionId,
    fields_added_count: additions.length,
    fields_added: additions,
    conflicts_count: conflicts.length,
    conflict_keys: conflicts
  }));

  // Update sensitive secrets with merged data (existing value wins if both present)
  const SENSITIVE_MERGE = [
    'wifi_ssid', 'wifi_password', 'door_code', 'building_code',
    'host_phone', 'house_access_private', 'private_notes'
  ];
  const updatedSecrets = { ...(privateRecord.secrets || {}) };
  for (const key of SENSITIVE_MERGE) {
    const fromMerge = cleanValue(getAnswer(merged, key));
    if (fromMerge && !updatedSecrets[key]) {
      updatedSecrets[key] = fromMerge;
    }
  }

  const updatedPrivateRecord = {
    ...privateRecord,
    secrets: updatedSecrets,
    metadata: {
      ...(privateRecord.metadata || {}),
      status: 'manual_extraction_complete',
      manual_review_at: now,
      review_submission_id: reviewSubmissionId
    },
    manual_extraction: {
      reviewed_at: now,
      review_submission_id: reviewSubmissionId,
      fields_added_count: additions.length,
      fields_added: additions,
      conflicts_count: conflicts.length,
      conflict_keys: conflicts
    }
  };

  try {
    await env.MYGUEST_KV.put(privateKey, JSON.stringify(updatedPrivateRecord));
  } catch (err) {
    console.error('review: failed to update private record (aborting dispatch):', safeError(err));
    return jsonResponse({ ok: false, error: 'Failed to update private record', slug }, 500);
  }

  // Build public payload for GitHub dispatch using merged answers
  const origin = new URL(request.url).origin;
  const fakeNormalized = {
    submission_id: originalSubmissionId,
    submitted_at:  privateRecord.metadata?.submitted_at || now,
    answers:       merged
  };
  const publicPayload = buildPublicPayload({
    normalized:       fakeNormalized,
    slug,
    privateRecordKey: privateKey,
    origin,
    now
  });

  // Update index and dispatch
  index.status = 'manual_extraction_complete';
  index.last_updated_at = now;
  await env.MYGUEST_KV.put(indexKey, JSON.stringify(index)).catch(() => {});

  try {
    await dispatchToGitHub(publicPayload, env);
  } catch (err) {
    index.status = 'failed_dispatch';
    index.last_error = err.message;
    index.last_updated_at = now;
    await env.MYGUEST_KV.put(indexKey, JSON.stringify(index)).catch(() => {});
    console.error('review: github dispatch failed:', safeError(err));
    throw err;
  }

  index.status = 'dispatched_to_github';
  index.last_updated_at = now;
  await env.MYGUEST_KV.put(indexKey, JSON.stringify(index)).catch(() => {});

  // Update delivery record status
  try {
    const delivery = deliveryRecord;
    if (delivery) {
      await env.MYGUEST_KV.put(deliveryKey, JSON.stringify({
        ...delivery,
        status: 'dispatched_to_github',
        manual_review_at: now
      }));
    }
  } catch (err) {
    console.error('review: delivery record update failed (non-fatal):', safeError(err));
  }

  console.log('manual extraction dispatch success:', slug);

  return jsonResponse({
    ok: true,
    status: 'dispatched_to_github',
    slug,
    original_submission_id: originalSubmissionId,
    fields_added: additions.length,
    conflicts: conflicts.length,
    message: 'Manual extraction complete. Generation dispatched to GitHub.'
  });
}

function isManualExtractionApproved(answers) {
  // Candidate keys for the extraction-complete confirmation field, in priority order.
  // Covers: generic aliases, all normalized variants of the yP1y9B label, and
  // alternative labels that could appear if the form is ever modified.
  const CONFIRMATION_KEYS = [
    'review_confirmed',
    'la_extraccion_esta_completa_y_lista_para_generar_la_guia',
    'la_extraccion_esta_completa_y_lista_para_generar',
    'extraccion_completa',
    'extraction_complete',
    'confirmacion_extraccion',
  ];

  let raw = '';
  for (const key of CONFIRMATION_KEYS) {
    const val = getAnswer(answers, key);
    if (val === null || val === undefined) continue;
    // MULTIPLE_CHOICE with allowMultiple=false still arrives as a single string after
    // extractTallyFieldValue resolves option IDs to text. Guard against an array just in case.
    raw = Array.isArray(val) ? val.filter(Boolean).join(' ').trim() : String(val).trim();
    if (raw) break;
  }

  if (!raw) return false;

  const norm = raw
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .trim();

  // Unambiguous affirmative signals
  if (norm.startsWith('si') || norm.startsWith('yes')) return true;
  if (norm.includes('lista para generar') || norm.includes('ready to generate')) return true;

  return false;
}

function mergeAnswersForReview(original, review) {
  // Campos propios del formulario interno — no son datos de la propiedad
  const REVIEW_META_KEYS = new Set([
    'flow_type', 'original_submission_id', 'slug',
    'review_confirmed', 'extraction_notes', 'reviewer_name',
    'submission_id', 'submissionId', 'responseId',
    // Normalized keys from yP1y9B fields that are internal to the review form.
    // Must stay in sync with CONFIRMATION_KEYS in isManualExtractionApproved.
    'la_extraccion_esta_completa_y_lista_para_generar_la_guia',
    'la_extraccion_esta_completa_y_lista_para_generar',
    'extraccion_completa',
    'extraction_complete',
    'confirmacion_extraccion',
    'notas_internas_de_la_extraccion',
  ]);

  const merged    = { ...original };
  const conflicts = [];
  const additions = [];

  for (const [key, reviewValue] of Object.entries(review)) {
    if (REVIEW_META_KEYS.has(key)) continue;

    const cleanReview = typeof reviewValue === 'string' ? reviewValue.trim() : reviewValue;
    if (cleanReview === null || cleanReview === undefined || cleanReview === '') continue;

    const originalValue   = original[key];
    const cleanOriginal   = typeof originalValue === 'string' ? originalValue.trim() : originalValue;
    const originalIsEmpty = (cleanOriginal === null || cleanOriginal === undefined || cleanOriginal === '');

    if (originalIsEmpty) {
      merged[key] = cleanReview;
      additions.push(key);
    } else {
      // Original value wins — conflict recorded (key name only, never values)
      conflicts.push(key);
    }
  }

  return { merged, conflicts, additions };
}
