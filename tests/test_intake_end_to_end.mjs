/**
 * FASE 0 — La prueba que faltaba: intake REAL de punta a punta.
 *
 * Recorre la cadena completa de My Guest con un payload de submission con la
 * forma real del webhook de Tally:
 *
 *   fixture (webhook de Tally)
 *     -> normalizeTallyPayload            (worker.js)
 *     -> buildPublicPayload / buildPrivatePayload
 *     -> generate_villa.py                (generador, proceso real)
 *     -> HTML de la guia
 *     -> injectPrivateDetailsIntoBookHtml (worker.js, servido con token)
 *
 * y AFIRMA que la informacion de la propiedad llega a la guia del huesped:
 * WiFi, check-in/out, accesos y recomendaciones.
 *
 * El bug que esta prueba existe para atrapar: que una pregunta del formulario
 * vivo deje de casar con la clave que lee el worker y su respuesta se caiga en
 * silencio. Eso es lo que paso en PawContact el 2026-07-26 (11 de 17 campos
 * perdidos) y ningun test estructural lo vio.
 *
 * Corre offline: sin OPENAI_API_KEY el generador no traduce (se le pasa
 * OPENAI_TRANSLATION_REQUIRED=false) y escribe en un directorio temporal
 * (MYGUEST_VILLAS_ROOT), nunca en public/.
 *
 *   node tests/test_intake_end_to_end.mjs
 */
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { loadWorker, REPO_ROOT } from './worker_module.mjs';

const FIXTURE = join(REPO_ROOT, 'tests', 'fixtures', 'intake_tally_webhook.json');
const GENERATOR = join(REPO_ROOT, 'books', 'scripts', 'generate_villa.py');

const ORIGIN = 'https://myguest-worker.example.workers.dev';
const NOW = '2026-07-26T12:00:00.000Z';
const TOKEN = 'fixture-token-no-es-real';

// Preguntas del formulario que NO deben llegar a la guia, con su razon.
// Cualquier otra respuesta del fixture que no aparezca en los payloads hace
// fallar la prueba.
const NO_VAN_A_LA_GUIA = new Map([
  ['Would you like to add another restaurant?', 'control de logica condicional'],
  ['Would you like to add one more restaurant?', 'control de logica condicional'],
  ['add_bar_4', 'control de logica condicional'],
  ['add_bar_5', 'control de logica condicional'],
  ['Style', 'elige la paleta, no es contenido: se afirma aparte'],
  ['Primary language', 'elige el idioma primario: se afirma aparte'],
  ['property_environment', 'elige la portada: se afirma aparte'],
  ['Pet Friendly', 'llega como booleano, no como texto: se afirma aparte'],
]);

/** Texto que el anfitrion escribio en cada pregunta, resolviendo las opciones. */
function respuestasDelFixture(payload) {
  return payload.data.fields.map((field) => {
    let value = field.value;

    if (Array.isArray(field.options) && Array.isArray(value)) {
      const textos = value.map((id) => {
        const opcion = field.options.find((o) => o.id === id);
        return opcion ? opcion.text : id;
      });
      value = textos.length === 1 ? textos[0] : textos;
    }

    return { label: field.label, value };
  });
}

/** Todas las cadenas hoja de un objeto, para buscar valores sin depender de la forma. */
function hojas(obj, out = []) {
  if (typeof obj === 'string') out.push(obj);
  else if (Array.isArray(obj)) obj.forEach((v) => hojas(v, out));
  else if (obj && typeof obj === 'object') Object.values(obj).forEach((v) => hojas(v, out));
  return out;
}

function contiene(textos, valor) {
  const buscado = String(valor).trim();
  return textos.some((t) => t.includes(buscado));
}

/** Compara ignorando el escapado de HTML del generador. */
function htmlContiene(html, valor) {
  const plano = html
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#x27;|&#39;/g, "'")
    .replace(/<br\s*\/?>/gi, '\n');
  return plano.includes(String(valor).trim());
}

async function main() {
  const worker = await loadWorker();
  const fixture = JSON.parse(readFileSync(FIXTURE, 'utf8'));

  // ── 1. Extraccion del worker ────────────────────────────────────────────
  const normalized = worker.normalizeTallyPayload(fixture);

  assert.equal(normalized.submission_id, 'TEST0001', 'el worker no reconocio el submission id');

  const requeridos = worker.validateRequiredPublicFields(normalized.answers);
  assert.ok(requeridos.ok, `intake real rechazado por campos requeridos: ${requeridos.error}`);

  const slug = worker.makeSlug(
    worker.getAnswer(normalized.answers, 'property_name'),
    normalized.submission_id,
  );
  assert.equal(slug, 'villa-fixture-intake-test0001');

  const privateRecordKey = `priv-${slug}`;
  const publicPayload = worker.buildPublicPayload({
    normalized, slug, privateRecordKey, origin: ORIGIN, now: NOW,
  });
  const privatePayload = worker.buildPrivatePayload({
    normalized, slug, privateRecordKey, guestToken: TOKEN, origin: ORIGIN, now: NOW,
  });

  // ── 2. Ningun campo del formulario se cae en silencio ───────────────────
  const textosDelPayload = [...hojas(publicPayload), ...hojas(privatePayload)];
  const perdidos = [];

  for (const { label, value } of respuestasDelFixture(fixture)) {
    if (NO_VAN_A_LA_GUIA.has(label)) continue;
    const valores = Array.isArray(value) ? value : [value];
    for (const v of valores) {
      if (!v || !String(v).trim()) continue;
      if (!contiene(textosDelPayload, v)) perdidos.push(label);
    }
  }

  assert.deepEqual(
    perdidos,
    [],
    `el worker tiro respuestas del intake real (la pregunta del formulario no casa ` +
    `con la clave que lee el worker): ${perdidos.join(', ')}`,
  );

  // Los campos que no viajan como texto, afirmados uno por uno.
  assert.equal(publicPayload.property.style, 'Coastal');
  assert.equal(publicPayload.property.primary_language, 'Español');
  assert.equal(publicPayload.property.property_environment, 'Beach');
  assert.equal(publicPayload.content.about_house.pet_friendly, false);

  // Lo sensible va al registro privado y NO al payload publico.
  assert.equal(privatePayload.secrets.wifi_ssid, 'VillaFixture-WiFi');
  assert.equal(privatePayload.secrets.wifi_password, 'Ficticia-4821-Demo');
  assert.equal(privatePayload.secrets.host_phone, '+52 322 000 0000');
  assert.match(privatePayload.secrets.house_access_private, /caja de llaves/);
  assert.equal(privatePayload.secrets._source_lang, 'es');

  const publicoPlano = JSON.stringify(publicPayload);
  for (const secreto of ['VillaFixture-WiFi', 'Ficticia-4821-Demo', '+52 322 000 0000', 'caja de llaves']) {
    assert.ok(
      !publicoPlano.includes(secreto),
      `dato sensible en el payload publico que se manda a GitHub Actions: ${secreto}`,
    );
  }

  // ── 3. El generador real produce la guia ────────────────────────────────
  const outRoot = mkdtempSync(join(tmpdir(), 'myguest-intake-'));
  let html;
  let escribioPasePkpass;
  try {
    const python = process.env.PYTHON || 'python';
    const run = spawnSync(python, [GENERATOR, JSON.stringify(publicPayload)], {
      cwd: REPO_ROOT,
      encoding: 'utf8',
      env: {
        ...process.env,
        MYGUEST_VILLAS_ROOT: outRoot,
        OPENAI_TRANSLATION_REQUIRED: 'false',
        OPENAI_API_KEY: '',
        PYTHONIOENCODING: 'utf-8',
      },
    });

    assert.equal(run.status, 0, `el generador fallo:\n${run.stdout}\n${run.stderr}`);

    const esPath = join(outRoot, slug, 'es.html');
    assert.ok(existsSync(esPath), `el generador no escribio es.html:\n${run.stdout}`);
    html = readFileSync(esPath, 'utf8');
    escribioPasePkpass = existsSync(join(outRoot, slug, 'pass.pkpass'));
  } finally {
    rmSync(outRoot, { recursive: true, force: true });
  }

  // ── 4. Los datos de la propiedad ESTAN en la guia ───────────────────────
  const debeAparecer = {
    'nombre de la propiedad': 'Villa Fixture Intake',
    'direccion': '145 Calle Ficticia, Colonia Inventada, Ciudad Demo',
    'hora de check-in': '11:00 AM',
    'hora de check-out': '10:00 AM',
    'instrucciones publicas de llegada': 'Porton negro justo enfrente de la plaza ficticia',
    'estacionamiento': 'Un lugar de estacionamiento disponible dentro del condominio ficticio.',
    'mensaje de bienvenida': 'Bienvenidos a tu hogar en la playa',
    'amenidades': 'Alberca, gimnasio, Wifi, AC.',
    'reglas de la casa': 'No parties or events.',
    'cosas que saber': 'Use the remote control in the living room.',
    'antes de salir': 'Wash any used dishes.',
    'transporte': 'Sitio de taxis enfrente de la casa',
    'notas finales': 'controlled LIVE test of the MyGuest purchase and delivery flow',
    'restaurante 1': 'La Palapa Ficticia',
    'restaurante 3': 'Trattoria Demo',
    'bar 1': 'Bar Ficticio',
    'bar 2': 'Cerveceria Inventada',
    'actividad 1': 'Tours Ficticios',
    'actividad 3': 'Mercado Artesanal Demo',
    'instagram': '@villa_fixture_demo',
    'link de resena': 'https://example.com/review/villa-fixture',
  };

  const faltantes = Object.entries(debeAparecer)
    .filter(([, valor]) => !htmlContiene(html, valor))
    .map(([que]) => que);

  assert.deepEqual(
    faltantes,
    [],
    `datos de la propiedad que NO llegaron a la guia del huesped: ${faltantes.join(', ')}`,
  );

  // ── 5. Nada sensible en el HTML publico ─────────────────────────────────
  for (const secreto of ['VillaFixture-WiFi', 'Ficticia-4821-Demo', '+52 322 000 0000', 'caja de llaves']) {
    assert.ok(
      !html.includes(secreto),
      `dato sensible publicado en el HTML de GitHub Pages: ${secreto}`,
    );
  }

  // ── 6. Con token, el worker inyecta lo privado en esa misma guia ────────
  const conToken = worker.injectPrivateDetailsIntoBookHtml({
    html,
    slug,
    token: TOKEN,
    secrets: privatePayload.secrets,
    lang: 'es',
  });

  const privadoEsperado = {
    'red WiFi': 'VillaFixture-WiFi',
    'contrasena WiFi': 'Ficticia-4821-Demo',
    'telefono del anfitrion': '+52 322 000 0000',
    'detalles de acceso privado': 'caja de llaves',
    'etiqueta Red WiFi en espanol': 'Red WiFi',
    'etiqueta Contrasena WiFi en espanol': 'Contraseña WiFi',
    'etiqueta Telefono del anfitrion en espanol': 'Teléfono del anfitrión',
  };

  const privadosFaltantes = Object.entries(privadoEsperado)
    .filter(([, valor]) => !htmlContiene(conToken, valor))
    .map(([que]) => que);

  assert.deepEqual(
    privadosFaltantes,
    [],
    `el huesped con link valido NO ve: ${privadosFaltantes.join(', ')}`,
  );

  // El HTML servido con token no se indexa.
  assert.match(conToken, /name="robots"/);

  // ── 7. Boton "Guardar en Contactos": datos publicos si, telefono solo con token ──
  assert.match(html, /id="vcard-btn"/, 'la guia no trae el boton de guardar en contactos');
  assert.match(
    html,
    /data-vcard-name="Villa Fixture Intake"/,
    'el vCard no recibio el nombre de la propiedad',
  );
  assert.ok(
    htmlContiene(html, 'data-vcard-adr="145 Calle Ficticia, Colonia Inventada, Ciudad Demo"'),
    'el vCard no recibio la direccion',
  );
  assert.ok(
    htmlContiene(html, 'data-vcard-social="https://instagram.com/villa_fixture_demo"'),
    'el vCard no recibio el instagram normalizado a URL',
  );
  // En la guia publica el contenedor privado esta VACIO: el boton existe pero el
  // vCard sale sin telefono, que es exactamente lo que debe pasar sin token.
  assert.match(
    html,
    /<div id="private-contact-content"><\/div>/,
    'la guia publica no debe traer nada dentro del contenedor privado de contacto',
  );

  // Con token el telefono existe y esta marcado, que es de donde lo lee el boton.
  assert.match(
    conToken,
    /<div class="private-card" data-private-field="host_phone">/,
    'el worker no marco la tarjeta del telefono: el vCard saldria sin telefono',
  );
  const tarjetaTelefono = conToken.match(
    /data-private-field="host_phone"[\s\S]*?private-card-text">([^<]*)</,
  );
  assert.ok(tarjetaTelefono, 'no se pudo leer el telefono de la tarjeta marcada');
  assert.equal(tarjetaTelefono[1].trim(), '+52 322 000 0000');

  // El boton sobrevive al reemplazo del script que hace el worker al servir con token.
  assert.match(conToken, /initVcard\(\);/, 'initVcard() se perdio en la version servida con token');

  // ── 8. Pases de wallet: APAGADOS, y apagado quiere decir invisible ───────
  // El bloque vive en la plantilla para que prenderlos sea configuracion y no
  // codigo, pero con los flags apagados no puede llegarle NADA al huesped: ni
  // un link, ni un archivo, ni un boton visible.
  assert.match(html, /id="wallet-wrap"/, 'el bloque de wallet se perdio de la plantilla');
  assert.match(
    html,
    /class="wallet-wrap is-hidden"/,
    'el bloque de wallet debe salir oculto cuando no hay pase',
  );
  assert.ok(
    htmlContiene(html, 'id="google-wallet-btn"') && !html.includes('pay.google.com'),
    'con el flag apagado la guia no puede traer un link de Google Wallet',
  );
  assert.ok(
    !html.includes('pass.pkpass'),
    'con el flag apagado la guia no puede apuntar a un pase de Apple',
  );
  assert.equal(
    escribioPasePkpass,
    false,
    'con el flag apagado el generador no debe escribir pass.pkpass',
  );
  assert.match(
    conToken,
    /initWalletButtons\(\);/,
    'initWalletButtons() se perdio en la version servida con token',
  );

  console.log('OK: intake real de punta a punta — el intake llega completo a la guia');
}

await main();
