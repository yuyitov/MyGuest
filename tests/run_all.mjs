/**
 * Corre la suite de My Guest. Todo offline: no toca red, no escribe en public/.
 *
 *   npm test        (o)   node tests/run_all.mjs
 */
import { spawnSync } from 'node:child_process';
import { join } from 'node:path';

import { REPO_ROOT } from './worker_module.mjs';

const python = process.env.PYTHON || 'python';

const SUITE = [
  ['node', [join('tests', 'test_intake_end_to_end.mjs')]],
  ['node', [join('tests', 'test_form_field_coverage.mjs')]],
  ['node', [join('tests', 'test_corrections_contract.mjs')]],
  ['node', [join('tests', 'test_landing_legal_contract.mjs')]],
  ['node', [join('tests', 'test_demo_mark_publicado.mjs')]],
  [python, [join('books', 'scripts', 'test_parse_translation_json.py')]],
  [python, ['-m', 'pytest', '-q', join('books', 'scripts')]],
];

let fallos = 0;

for (const [cmd, args] of SUITE) {
  const etiqueta = `${cmd} ${args.join(' ')}`;
  const run = spawnSync(cmd, args, {
    cwd: REPO_ROOT,
    stdio: 'inherit',
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
  });

  if (run.status !== 0) {
    fallos += 1;
    console.error(`FALLO: ${etiqueta}`);
  }
}

if (fallos) {
  console.error(`\n${fallos} prueba(s) en rojo.`);
  process.exit(1);
}

console.log('\nSuite de My Guest en verde.');
