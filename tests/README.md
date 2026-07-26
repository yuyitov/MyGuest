# Pruebas de My Guest

```bash
npm test
```

Corre offline: no toca red, no llama a OpenAI y **nunca escribe en `public/`**
(el generador respeta `MYGUEST_VILLAS_ROOT`, que la prueba apunta a un temporal).

## Qué hay aquí

| Archivo | Qué afirma |
|---|---|
| `test_intake_end_to_end.mjs` | La cadena completa con un payload de intake con la forma real del webhook de Tally: extracción del worker → `generate_villa.py` → HTML → inyección privada del worker. Afirma que WiFi, check-in/out, accesos, recomendaciones y notas del anfitrión **llegan a la guía del huésped**, que lo sensible **no** queda en el HTML público, y que el botón "Guardar en Contactos" recibe sus datos. |
| `test_form_field_coverage.mjs` | Cada pregunta del formulario **vivo** de Tally llega a algún payload. Es el candado contra el bug que rompió PawContact: un título de pregunta cambia, deja de casar con la clave que lee el worker, y la respuesta se cae en silencio con los tests en verde. |
| `../books/scripts/test_wallet_passes.py` | Los pases de wallet. Con los flags apagados no se firma, no se escribe y no se publica nada; con el flag prendido el pase que sale es válido y verificable (firma RS256 de Google verificada con openssl, `.pkpass` con su manifest SHA-1 y su PKCS#7); en ningún caso viaja un secreto ni el token dentro del pase; y una credencial rota se lleva el botón, no la guía. Las llaves y certificados son **de mentira y se generan al vuelo** en un temporal: no hay material criptográfico en el repo. |
| `../books/scripts/test_parse_translation_json.py` | Parseo de la respuesta de traducción. |
| `worker_module.mjs` | Carga `worker/worker.js` tal cual y expone sus funciones internas, sin agregarle exports (así no hay que redesplegar el worker por una prueba). |

## Fixtures

- **`fixtures/intake_tally_webhook.json`** — payload de intake. La estructura
  (ids de pregunta, títulos, tipos y uuids de opción) viene de la submission
  **real** `X5YjRRd` del formulario vivo `MedpvA` (la prueba LIVE controlada G-06
  del 2026-07-02). **Todo dato sensible es ficticio**, por la regla dura del
  repo: WiFi, códigos, teléfono del anfitrión y detalles privados de acceso están
  inventados. El propio archivo lo explica en su `_readme`.

- **`fixtures/tally_form_questions.json`** — inventario de las preguntas del
  formulario vivo: solo ids, tipos y títulos. Cero respuestas, cero datos de
  clientes.

### Cuando cambie el formulario de Tally

Hay que volver a tomar el snapshot del inventario:

```bash
curl -s -H "Authorization: Bearer $TALLY_API_KEY" \
  "https://api.tally.so/forms/MedpvA/submissions?limit=1" | \
  python -c "import json,sys;d=json.load(sys.stdin);print(json.dumps([{'id':q['id'],'type':q['type'],'title':q['title']} for q in d['questions'] if not q.get('isDeleted') and q['type']!='HIDDEN_FIELDS'],ensure_ascii=False,indent=2))"
```

Y pegarlo en `questions` de `tally_form_questions.json`, actualizando
`snapshot_date`. Si el cambio rompió el mapeo, `test_form_field_coverage.mjs` lo
dice con el título exacto de la pregunta que dejó de llegar.
