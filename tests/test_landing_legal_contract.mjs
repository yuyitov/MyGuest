/**
 * Contrato comercial: la FAQ visible debe repetir la política de reembolsos
 * vigente en los documentos legales trilingües.
 */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

import { REPO_ROOT } from './worker_module.mjs';

function assertLandingRefundPolicy(source) {
  assert.match(source, /7 calendar days after delivery/, 'La FAQ EN debe indicar 7 días tras la entrega.');
  assert.match(source, /7 días naturales posteriores a la entrega/, 'La FAQ ES debe indicar 7 días tras la entrega.');
  assert.match(source, /7 jours calendaires suivant la livraison/, 'La FAQ FR debe indicar 7 días tras la entrega.');
  assert.doesNotMatch(source, /48 hours|48 horas|48 heures/, 'La política antigua de 48 horas no puede reaparecer.');
}

const landing = readFileSync(join(REPO_ROOT, 'public', 'index.html'), 'utf8');
assertLandingRefundPolicy(landing);

// Mutaciones: esta prueba debe caer si desaparece el plazo correcto o vuelve
// la promesa antigua a cualquiera de los tres idiomas.
assert.throws(() => assertLandingRefundPolicy(landing.replace('7 calendar days after delivery', '48 hours after delivery')));
assert.throws(() => assertLandingRefundPolicy(landing.replace('7 días naturales posteriores a la entrega', '48 horas posteriores a la entrega')));
assert.throws(() => assertLandingRefundPolicy(landing.replace('7 jours calendaires suivant la livraison', '48 heures suivant la livraison')));

console.log('OK: FAQ de reembolsos consistente en EN/ES/FR y protegida contra regresiones.');
