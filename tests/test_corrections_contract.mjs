import assert from 'node:assert/strict';

import { loadWorker } from './worker_module.mjs';

const workerModule = await loadWorker();
const {
  correctionPageHtml,
  correctionQuota,
  consumeCorrectionQuota,
  handleBuyCorrection,
  handlePaidCorrectionPurchase,
  isPaidCorrectionSession,
  paidCorrectionPageHtml,
} = workerModule;
const tallyUrl = 'https://tally.so/r/test?slug=villa&correction_token=fake';

class MemoryKV {
  constructor(records = {}) {
    this.records = new Map(Object.entries(records));
  }

  async get(key, options) {
    const value = this.records.get(key);
    if (value == null) return null;
    return options?.type === 'json' ? JSON.parse(value) : value;
  }

  async put(key, value) {
    this.records.set(key, value);
  }
}

async function signedStripeRequest(event, secret) {
  const body = JSON.stringify(event);
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const bytes = await crypto.subtle.sign(
    'HMAC',
    key,
    new TextEncoder().encode(`${timestamp}.${body}`)
  );
  const signature = Array.from(new Uint8Array(bytes))
    .map((value) => value.toString(16).padStart(2, '0'))
    .join('');
  return new Request('https://worker.example/stripe/webhook', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'stripe-signature': `t=${timestamp},v1=${signature}`,
    },
    body,
  });
}

{
  const response = correctionPageHtml(tallyUrl, 2);
  const html = await response.text();

  assert.equal(response.status, 200);
  assert.match(html, /2 free correction rounds are included/);
  assert.match(html, /remains available while you have included correction rounds left/);
  assert.doesNotMatch(html, /can only be used once/i);
  assert.doesNotMatch(html, /One free correction round is included/i);
  assert.match(html, /noindex,nofollow,noarchive/);
}

{
  const html = await correctionPageHtml(tallyUrl, 1).text();
  assert.match(html, /One free correction round is included/);
}

{
  const record = { free_total: 2, free_used: 2, paid_remaining: 1 };
  assert.deepEqual(correctionQuota(record, {}), {
    total: 2,
    used: 2,
    includedRemaining: 0,
    paidRemaining: 1,
    remaining: 1,
  });
  const consumed = consumeCorrectionQuota(record, {});
  assert.equal(consumed.paid, true);
  assert.equal(consumed.record.free_used, 2);
  assert.equal(consumed.record.paid_remaining, 0);
  assert.equal(consumed.record.used, true);
}

{
  assert.equal(
    isPaidCorrectionSession('checkout.session.completed', {
      metadata: { myguest_correction: '1' },
    }),
    true
  );
  assert.equal(
    isPaidCorrectionSession('checkout.session.completed', { metadata: {} }),
    false
  );
  assert.equal(
    isPaidCorrectionSession('payment_intent.succeeded', {
      metadata: { myguest_correction: '1' },
    }),
    false
  );
}

{
  const html = await paidCorrectionPageHtml(
    'https://worker.example/buy-correction?slug=villa&token=fake'
  ).text();
  assert.match(html, /\$6 USD \/ \$59 MXN/);
  assert.match(html, /two included correction rounds have been used/i);
  assert.match(html, /noindex,nofollow,noarchive/);
}

{
  const kv = new MemoryKV({
    'delivery:villa-mar': JSON.stringify({
      order_id: 'pi_original',
      customer_email: 'owner@example.com',
    }),
    'correction:villa-mar': JSON.stringify({
      token: 'secure-token',
      customer_email: 'owner@example.com',
      free_total: 2,
      free_used: 2,
    }),
    'order:pi_original': JSON.stringify({ currency: 'mxn' }),
  });
  const originalFetch = globalThis.fetch;
  let stripeBody = '';
  globalThis.fetch = async (url, options) => {
    assert.equal(url, 'https://api.stripe.com/v1/checkout/sessions');
    stripeBody = options.body;
    return new Response(
      JSON.stringify({ url: 'https://checkout.stripe.com/c/pay/test' }),
      { status: 200, headers: { 'content-type': 'application/json' } }
    );
  };
  try {
    const response = await handleBuyCorrection(
      new URL('https://worker.example/buy-correction?slug=villa-mar&token=secure-token'),
      { MYGUEST_KV: kv, STRIPE_SECRET_KEY: 'sk_test_fake' }
    );
    assert.equal(response.status, 302);
    assert.equal(response.headers.get('location'), 'https://checkout.stripe.com/c/pay/test');
    const params = new URLSearchParams(stripeBody);
    assert.equal(params.get('line_items[0][price_data][currency]'), 'mxn');
    assert.equal(params.get('line_items[0][price_data][unit_amount]'), '5900');
    assert.equal(params.get('metadata[myguest_correction]'), '1');
    assert.equal(params.get('metadata[slug]'), 'villa-mar');
    assert.equal(params.get('customer_email'), 'owner@example.com');
  } finally {
    globalThis.fetch = originalFetch;
  }
}

{
  const kv = new MemoryKV({
    'delivery:villa-mar': JSON.stringify({
      order_id: 'pi_original',
      customer_email: 'owner@example.com',
    }),
    'correction:villa-mar': JSON.stringify({
      token: 'secure-token',
      customer_email: 'owner@example.com',
      free_total: 2,
      free_used: 2,
      paid_remaining: 0,
    }),
  });
  const env = {
    MYGUEST_KV: kv,
    RESEND_API_KEY: 're_test_fake',
    FROM_EMAIL: 'MyGuest <hello@myguestguide.com>',
    MYGUEST_WORKER_URL: 'https://worker.example',
  };
  const originalFetch = globalThis.fetch;
  const sentEmails = [];
  globalThis.fetch = async (url, options) => {
    assert.equal(url, 'https://api.resend.com/emails');
    sentEmails.push(JSON.parse(options.body));
    return new Response(JSON.stringify({ id: 'email_test' }), {
      status: 200,
      headers: { 'content-type': 'application/json' },
    });
  };
  const session = {
    id: 'cs_correction_1',
    payment_intent: 'pi_correction_1',
    customer_email: 'different-buyer@example.com',
    metadata: { myguest_correction: '1', slug: 'villa-mar' },
  };
  try {
    const first = await handlePaidCorrectionPurchase(session, env);
    assert.equal(first.status, 200);
    const credited = await kv.get('correction:villa-mar', { type: 'json' });
    assert.equal(credited.paid_remaining, 1);
    assert.equal(credited.paid_purchased, 1);
    assert.deepEqual(credited.paid_payment_ids, ['pi_correction_1']);
    assert.equal(sentEmails[0].to, 'owner@example.com');
    assert.notEqual(sentEmails[0].to, session.customer_email);

    const repeat = await handlePaidCorrectionPurchase(session, env);
    assert.equal(repeat.status, 200);
    const afterRepeat = await kv.get('correction:villa-mar', { type: 'json' });
    assert.equal(afterRepeat.paid_remaining, 1);
    assert.equal(sentEmails.length, 1);
  } finally {
    globalThis.fetch = originalFetch;
  }
}

{
  const kv = new MemoryKV({
    'delivery:villa-webhook': JSON.stringify({
      order_id: 'pi_original',
      customer_email: 'owner@example.com',
    }),
    'correction:villa-webhook': JSON.stringify({
      token: 'secure-token',
      customer_email: 'owner@example.com',
      free_total: 2,
      free_used: 2,
    }),
  });
  const env = {
    MYGUEST_KV: kv,
    STRIPE_WEBHOOK_SECRET: 'whsec_test',
    STRIPE_PAYMENT_LINK_ID: 'plink_sale',
    RESEND_API_KEY: 're_test_fake',
    FROM_EMAIL: 'MyGuest <hello@myguestguide.com>',
    MYGUEST_WORKER_URL: 'https://worker.example',
  };
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response(JSON.stringify({ id: 'email_test' }), {
    status: 200,
    headers: { 'content-type': 'application/json' },
  });
  try {
    const correctionEvent = {
      type: 'checkout.session.completed',
      data: {
        object: {
          id: 'cs_webhook',
          payment_intent: 'pi_webhook',
          metadata: { myguest_correction: '1', slug: 'villa-webhook' },
        },
      },
    };
    const response = await workerModule.default.fetch(
      await signedStripeRequest(correctionEvent, env.STRIPE_WEBHOOK_SECRET),
      env,
      {}
    );
    assert.equal(response.status, 200);
    const credited = await kv.get('correction:villa-webhook', { type: 'json' });
    assert.equal(credited.paid_remaining, 1);

    const missingMetadata = structuredClone(correctionEvent);
    missingMetadata.data.object.payment_intent = 'pi_without_metadata';
    missingMetadata.data.object.metadata = {};
    const ignored = await workerModule.default.fetch(
      await signedStripeRequest(missingMetadata, env.STRIPE_WEBHOOK_SECRET),
      env,
      {}
    );
    assert.equal(ignored.status, 200);
    const ignoredBody = await ignored.json();
    assert.equal(ignoredBody.reason, 'other_product');
    const unchanged = await kv.get('correction:villa-webhook', { type: 'json' });
    assert.equal(unchanged.paid_remaining, 1);
  } finally {
    globalThis.fetch = originalFetch;
  }
}

console.log('Contrato de correcciones My Guest: incluidas + pago idempotente, verde.');
