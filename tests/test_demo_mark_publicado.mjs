/**
 * Candado sobre las 20 paginas demo YA PUBLICADAS en `public/villas/`.
 *
 * Las 4 guias demo muestran propiedades ficticias. Cada una publica 5 archivos
 * (en, es, fr, index, print) y los 20 deben declararlo: `robots noindex` para
 * que no entren a los buscadores, y la cinta visible para que nadie confunda la
 * muestra con la guia de un alojamiento real.
 *
 * Existe porque esa marca se puso a mano una vez y una regeneracion la borro.
 * Ahora la produce el generador (`books/scripts/_demo_mark.py`, probado en
 * `books/scripts/test_demo_mark.py`); esto mide el resultado publicado, para
 * que si alguien la vuelve a borrar se ponga rojo solo.
 */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

import { REPO_ROOT } from './worker_module.mjs';

const DEMOS = [
  'ocean-drive-retreat',
  'the-soho-loft',
  'casa-selva-tulum',
  'le-marais-flat',
];

const ROBOTS = '<meta name="robots" content="noindex, nofollow">';

// Texto legal de la cinta, por pagina. `index.html` es copia de la pagina
// principal y el imprimible es trilingue en un solo archivo: los 4 demos tienen
// English como idioma principal, asi que ambos llevan el texto en ingles.
const CINTA = {
  en: 'DEMO · Sample guide with a fictional property. Not a real booking.',
  es: 'DEMO · Guía de muestra con una propiedad ficticia. No es una reserva real.',
  fr: 'DÉMO · Livret d’exemple avec un logement fictif. Ce n’est pas une vraie réservation.',
};

const PAGINAS = {
  'en.html': CINTA.en,
  'es.html': CINTA.es,
  'fr.html': CINTA.fr,
  'index.html': CINTA.en,
  'print.html': CINTA.en,
};

function assertPaginaMarcada(html, texto, donde) {
  assert.ok(html.includes(ROBOTS), `${donde}: falta el meta robots noindex.`);
  assert.ok(
    html.indexOf(ROBOTS) < html.indexOf('</head>'),
    `${donde}: el meta robots quedo fuera del <head>.`,
  );
  assert.ok(
    html.includes(`<div class="mg-demo-ribbon" role="note">${texto}</div>`),
    `${donde}: falta la cinta de demo con su texto exacto.`,
  );
  assert.ok(
    html.includes('.mg-demo-ribbon {'),
    `${donde}: falta el CSS de la cinta (saldria invisible).`,
  );
}

let revisadas = 0;
for (const slug of DEMOS) {
  for (const [pagina, texto] of Object.entries(PAGINAS)) {
    const ruta = join(REPO_ROOT, 'public', 'villas', slug, pagina);
    assertPaginaMarcada(readFileSync(ruta, 'utf8'), texto, `${slug}/${pagina}`);
    revisadas += 1;
  }
}
assert.equal(revisadas, 20, 'Se esperaban 20 paginas demo publicadas.');

// Mutaciones: si borrar cualquiera de las tres piezas dejara la prueba en
// verde, esto no estaria midiendo nada.
const muestra = readFileSync(
  join(REPO_ROOT, 'public', 'villas', 'ocean-drive-retreat', 'en.html'),
  'utf8',
);
for (const [nombre, roto] of Object.entries({
  'sin meta robots': muestra.replace(ROBOTS, ''),
  'sin cinta': muestra.replace(`>${CINTA.en}</div>`, '></div>'),
  // replaceAll: la clase aparece dos veces (la regla y el @media print).
  'sin CSS de la cinta': muestra.replaceAll('.mg-demo-ribbon {', '.mg-nada {'),
})) {
  assert.throws(
    () => assertPaginaMarcada(roto, CINTA.en, nombre),
    `La mutacion "${nombre}" deberia poner la prueba en rojo.`,
  );
}

console.log('OK: las 20 paginas demo publicadas traen noindex + cinta de demo.');
