/**
 * Carga worker/worker.js TAL CUAL y expone sus funciones internas para poder
 * probarlas.
 *
 * El worker no exporta sus helpers (solo `export default { fetch }`), y no se le
 * agregan exports para no tener que redesplegarlo por una prueba. En su lugar se
 * copia el archivo a un temporal con una linea `export { ... }` al final: la
 * prueba corre sobre el MISMO codigo que esta en produccion, byte a byte, no
 * sobre una copia mantenida a mano.
 */
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const TESTS_DIR = dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = join(TESTS_DIR, '..');
export const WORKER_PATH = join(REPO_ROOT, 'worker', 'worker.js');

const EXPOSED = [
  'normalizeTallyPayload',
  'buildPublicPayload',
  'buildPrivatePayload',
  'validateRequiredPublicFields',
  'makeSlug',
  'getAnswer',
  'normalizeKey',
  'cleanValue',
  'injectPrivateDetailsIntoBookHtml',
  'injectPrivateDetailsIntoPrintHtml',
  'buildPrivateBookBlocks',
  'correctionPageHtml',
  'correctionQuota',
  'consumeCorrectionQuota',
  'handleBuyCorrection',
  'handlePaidCorrectionPurchase',
  'isPaidCorrectionSession',
  'paidCorrectionPageHtml',
];

export async function loadWorker() {
  const source = readFileSync(WORKER_PATH, 'utf8');
  const dir = mkdtempSync(join(tmpdir(), 'myguest-worker-'));
  const shim = join(dir, 'worker.under-test.mjs');
  writeFileSync(shim, `${source}\n\nexport { ${EXPOSED.join(', ')} };\n`, 'utf8');
  return import(pathToFileURL(shim).href);
}
