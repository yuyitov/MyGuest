/**
 * FASE 0 — El candado que impide que una pregunta del formulario deje de casar.
 *
 * El bug de PawContact del 2026-07-26 no fue un error de logica: fue que el
 * TITULO de una pregunta de Tally cambio y dejo de normalizar a la clave que lee
 * el worker. Los tests seguian verdes porque ninguno comparaba el formulario
 * VIVO contra lo que el worker lee.
 *
 * Esta prueba lo compara: mete un valor centinela unico en CADA pregunta del
 * formulario vivo (inventario en tests/fixtures/tally_form_questions.json) y
 * afirma que el centinela sale del otro lado, en el payload publico o en el
 * privado. Si una pregunta no llega, la prueba dice cual y con que titulo.
 *
 * Las preguntas que a proposito NO viajan a los payloads estan listadas abajo
 * con su razon. Una pregunta que no llega y no esta en esa lista es un campo
 * perdido, no una excepcion.
 *
 * Corre offline y no toca red: el inventario del formulario esta commiteado.
 * Cuando el formulario de Tally cambie, hay que volver a tomar el snapshot
 * (GET https://api.tally.so/forms/MedpvA/submissions -> questions[]) — y esta
 * prueba es la que avisa si el cambio rompio el mapeo.
 *
 *   node tests/test_form_field_coverage.mjs
 */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

import { loadWorker, REPO_ROOT } from './worker_module.mjs';

const SNAPSHOT = join(REPO_ROOT, 'tests', 'fixtures', 'tally_form_questions.json');

// Preguntas del formulario vivo que a proposito no viajan en los payloads.
const NO_VIAJAN = new Map([
  ['Would you like to add another restaurant?', 'control de logica condicional del formulario'],
  ['Would you like to add one more restaurant?', 'control de logica condicional del formulario'],
  ['add_bar_4', 'control de logica condicional del formulario'],
  ['add_bar_5', 'control de logica condicional del formulario'],
  ['Existing book file', 'gatea la extraccion manual (needs_manual_extraction), no va a la guia'],
  ['Existing book photos', 'gatea la extraccion manual (needs_manual_extraction), no va a la guia'],
  ['Pet Friendly', 'viaja como booleano, no como texto: lo afirma test_intake_end_to_end.mjs'],
]);

function centinela(index) {
  return `CENTINELA${String(index).padStart(3, '0')}`;
}

function hojas(obj, out = []) {
  if (typeof obj === 'string') out.push(obj);
  else if (Array.isArray(obj)) obj.forEach((v) => hojas(v, out));
  else if (obj && typeof obj === 'object') Object.values(obj).forEach((v) => hojas(v, out));
  return out;
}

async function main() {
  const worker = await loadWorker();
  const snapshot = JSON.parse(readFileSync(SNAPSHOT, 'utf8'));
  const preguntas = snapshot.questions;

  assert.ok(preguntas.length > 40, `inventario del formulario sospechosamente corto: ${preguntas.length}`);

  const fields = preguntas.map((q, i) => ({
    key: `question_${q.id}`,
    label: q.title,
    type: q.type,
    value: centinela(i),
  }));

  // Los requeridos necesitan valores validos o el worker rechaza el intake antes
  // de construir los payloads; se les pone el valor real que espera.
  const VALIDOS = {
    Style: 'Coastal',
    'Primary language': 'English',
    property_environment: 'Beach',
  };
  for (const f of fields) {
    if (VALIDOS[f.label]) f.value = VALIDOS[f.label];
  }

  const payload = {
    eventType: 'FORM_RESPONSE',
    data: {
      submissionId: 'COVERAGE01',
      formId: snapshot.form_id,
      fields,
      hiddenFields: { order_id: 'pi_cobertura', customer_email: 'nadie@example.com' },
    },
  };

  const normalized = worker.normalizeTallyPayload(payload);
  const requeridos = worker.validateRequiredPublicFields(normalized.answers);
  assert.ok(requeridos.ok, `el worker rechazaria el formulario vivo: ${requeridos.error}`);

  const slug = worker.makeSlug('Cobertura', normalized.submission_id);
  const comun = { normalized, slug, privateRecordKey: `priv-${slug}`, origin: 'https://example.workers.dev', now: '2026-07-26T00:00:00.000Z' };
  const textos = [
    ...hojas(worker.buildPublicPayload(comun)),
    ...hojas(worker.buildPrivatePayload({ ...comun, guestToken: 'x' })),
  ];

  const perdidas = [];
  for (const [i, q] of preguntas.entries()) {
    if (NO_VIAJAN.has(q.title)) continue;
    if (VALIDOS[q.title]) {
      assert.ok(
        textos.some((t) => t === VALIDOS[q.title]),
        `la pregunta "${q.title}" no llego a ningun payload`,
      );
      continue;
    }
    if (!textos.some((t) => t.includes(centinela(i)))) {
      perdidas.push(`${q.title} (${q.type}, id ${q.id})`);
    }
  }

  assert.deepEqual(
    perdidas,
    [],
    'preguntas del formulario VIVO cuya respuesta no llega a ningun payload — ' +
    'el titulo dejo de casar con la clave que lee el worker:\n  ' + perdidas.join('\n  '),
  );

  // El espejo: claves que el worker lee y el formulario ya no pregunta. No es un
  // error (son alias y compatibilidad con formularios viejos), pero se reporta
  // para que no crezca sin que nadie lo note.
  const huerfanas = [];
  const titulosNormalizados = new Set(preguntas.map((q) => worker.normalizeKey(q.title)));
  const LEIDAS_SIN_PREGUNTA_ESPERADAS = new Set([
    // alias de compatibilidad y de extraccion IA
    'house_access_public', 'house_access_private', 'private_access_notes', 'private_notes',
    'places_to_eat', 'places_to_drink', 'things_to_do', 'local_directory',
    'directions_text', 'host_email', 'door_code', 'building_code', 'property_photos',
  ]);
  const fuente = readFileSync(join(REPO_ROOT, 'worker', 'worker.js'), 'utf8');
  for (const m of fuente.matchAll(/getAnswer\(answers, '([a-z0-9_]+)'\)/g)) {
    const clave = m[1];
    if (titulosNormalizados.has(clave)) continue;
    if (LEIDAS_SIN_PREGUNTA_ESPERADAS.has(clave)) continue;
    if (!huerfanas.includes(clave)) huerfanas.push(clave);
  }

  assert.deepEqual(
    huerfanas,
    [],
    'el worker lee claves que el formulario vivo ya no pregunta (o se agrego una ' +
    'pregunta con otro nombre): ' + huerfanas.join(', '),
  );

  console.log(
    `OK: cobertura del formulario — ${preguntas.length} preguntas vivas, ` +
    `${preguntas.length - NO_VIAJAN.size} llegan a los payloads`,
  );
}

await main();
