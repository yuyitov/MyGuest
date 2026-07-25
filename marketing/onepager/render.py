#!/usr/bin/env python3
"""Renderiza el one-pager de ventas a PDF (Letter, 1 pagina).

    python marketing/onepager/render.py

Existe porque la version anterior del PDF se genero SIN dejar fuente en el repo:
cuando el precio paso de $29 a $49 no se pudo editar, hubo que reconstruirlo
entero, y mientras tanto el material de ventas decia un precio que ya no existia.
Con este script y su HTML al lado, el proximo cambio es de un minuto.

Verifica al final que el PDF no traiga precios viejos -- el fallo que lo motivo.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

AQUI = Path(__file__).resolve().parent
HTML = AQUI / "onepager.html"
SALIDA = AQUI.parent / "assets" / "MyGuest_Sales_OnePager.pdf"

# El precio vigente vive en la landing; aqui solo se comprueba que el PDF no
# contradiga. Si cambia, se cambia en onepager.html y se vuelve a correr esto.
PRECIO_VIGENTE = "$49"
PRECIOS_MUERTOS = ("$29",)


def main() -> int:
    from playwright.sync_api import sync_playwright

    if not HTML.exists():
        print(f"  ERROR: no encuentro {HTML}")
        return 1

    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": 816, "height": 1056})
        pag.goto(HTML.as_uri())
        pag.wait_for_load_state("networkidle")
        SALIDA.parent.mkdir(parents=True, exist_ok=True)
        pag.pdf(
            path=str(SALIDA),
            width="8.5in",
            height="11in",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        nav.close()

    kb = SALIDA.stat().st_size // 1024
    print(f"  PDF escrito: {SALIDA}  ({kb} KB)")

    # --- Salvaguarda: que el PDF no repita un precio muerto ---
    try:
        import fitz  # PyMuPDF

        texto = "".join(pag.get_text() for pag in fitz.open(SALIDA))
        malos = [p for p in PRECIOS_MUERTOS if p in texto]
        if malos:
            print(f"  ERROR: el PDF todavia dice {', '.join(malos)}")
            return 1
        if PRECIO_VIGENTE not in texto:
            print(f"  ERROR: el PDF no dice el precio vigente {PRECIO_VIGENTE}")
            return 1
        print(f"  Verificado: dice {PRECIO_VIGENTE} y ningun precio viejo.")
    except ImportError:
        print("  (sin PyMuPDF: no se pudo verificar el precio dentro del PDF)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
