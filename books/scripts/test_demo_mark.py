"""Candado de la marca legal de las guias demo.

Las 4 guias demo publican propiedades FICTICIAS. La marca que lo declara —el
`<meta robots noindex>` y la cinta visible `mg-demo-ribbon`— vivia SOLO en el
HTML ya publicado, puesta a mano. Cada regeneracion la borraba: paso en el
LOTE B, se noto y se reinyecto a mano, pero el defecto seguia vivo y la
siguiente regeneracion lo repetia.

Lo que estas pruebas afirman, en orden de importancia:

1. Regenerar los 4 demos deja las 20 paginas CON marca, sin tocar nada a mano.
   La regeneracion es la prueba.
2. Simetria: el mismo payload SIN `demo_mode` sale sin noindex y sin cinta.
   Marcar la guia de un cliente que pago seria sacarla de Google.
3. La afirmacion mide: si se rompe cualquiera de las tres piezas en la salida
   real del generador, la prueba se pone roja.
4. Si una plantilla cambia y el ancla de inyeccion desaparece, la generacion se
   cae con un mensaje claro en vez de publicar una guia demo sin aviso.

El candado sobre las paginas ya PUBLICADAS vive aparte, en
`tests/test_demo_mark_publicado.mjs`.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _demo_mark import (
    RIBBON_TEXTS,
    ROBOTS_META,
    inject_demo_mark,
    ribbon_html,
)

# Los 4 demos oficiales y el script que los regenera.
DEMOS = {
    "_generate_demo.py": "ocean-drive-retreat",
    "_generate_demo_classic.py": "le-marais-flat",
    "_generate_demo_cozy.py": "casa-selva-tulum",
    "_generate_demo_city.py": "the-soho-loft",
}

# Las 5 paginas por villa y el idioma de la cinta de cada una. `index.html` es
# copia de la pagina principal y el imprimible es trilingue en un solo archivo
# con `lang` del idioma principal: los 4 demos son English.
PAGINAS = {
    "en.html": "English",
    "es.html": "Español",
    "fr.html": "Français",
    "index.html": "English",
    "print.html": "English",
}


def afirma_marca(html, idioma, donde=""):
    """La pagina trae las tres piezas de la marca, en su lugar."""
    assert ROBOTS_META in html, f"{donde}: falta el meta robots noindex."
    assert html.index(ROBOTS_META) < html.index("</head>"), (
        f"{donde}: el meta robots quedo fuera del <head>."
    )

    cinta = ribbon_html(idioma)
    assert cinta in html, f"{donde}: falta la cinta de demo en {idioma}."
    assert "<body>\n" + cinta in html, (
        f"{donde}: la cinta no abre el <body>."
    )
    assert ".mg-demo-ribbon {" in html, f"{donde}: falta el CSS de la cinta."


def afirma_sin_marca(html, donde=""):
    """Una guia real no lleva ni noindex ni cinta."""
    assert "noindex" not in html, f"{donde}: una guia real NO puede traer noindex."
    assert "mg-demo-ribbon" not in html, f"{donde}: una guia real NO lleva cinta."


def _entorno(villas_root, **extra):
    env = dict(os.environ)
    env["MYGUEST_VILLAS_ROOT"] = str(villas_root)
    env["PYTHONIOENCODING"] = "utf-8"
    # Determinismo y cero red: los demos traen sus traducciones embebidas.
    env.pop("OPENAI_API_KEY", None)
    env.update(extra)
    return env


def _corre(args, env):
    r = subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert r.returncode == 0, f"{args[0]} fallo:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    return r


@pytest.fixture(scope="module")
def demos_regenerados(tmp_path_factory):
    """Regenera los 4 demos en un temporal. Nunca escribe en `public/`."""
    destino = tmp_path_factory.mktemp("villas")
    env = _entorno(destino)
    for script in DEMOS:
        _corre([str(SCRIPT_DIR / script)], env)
    return destino


# --- 1. La regeneracion es la prueba -----------------------------------------

def test_regenerar_los_4_demos_deja_las_20_paginas_marcadas(demos_regenerados):
    revisadas = 0
    for slug in DEMOS.values():
        for pagina, idioma in PAGINAS.items():
            ruta = demos_regenerados / slug / pagina
            assert ruta.exists(), f"{slug}/{pagina} no se genero."
            afirma_marca(ruta.read_text(encoding="utf-8"), idioma, f"{slug}/{pagina}")
            revisadas += 1
    assert revisadas == 20


# --- 3. La afirmacion mide (mutacion B sobre la salida real) ------------------

def test_romper_la_marca_en_la_salida_real_pone_la_prueba_en_rojo(demos_regenerados):
    """Si la prueba siguiera verde con la marca rota, no estaria midiendo nada."""
    html = (demos_regenerados / "ocean-drive-retreat" / "en.html").read_text(
        encoding="utf-8"
    )
    afirma_marca(html, "English")  # verde antes de mutar

    mutaciones = {
        "sin meta robots": html.replace(ROBOTS_META, ""),
        "sin cinta": html.replace(ribbon_html("English"), ""),
        "sin CSS de la cinta": html.replace(".mg-demo-ribbon {", ".mg-nada {"),
        "cinta fuera del body": html.replace(
            "<body>\n" + ribbon_html("English"), "<body>"
        ),
    }
    for nombre, roto in mutaciones.items():
        with pytest.raises(AssertionError):
            afirma_marca(roto, "English", nombre)


def test_cada_idioma_lleva_su_texto_y_no_el_de_otro(demos_regenerados):
    for pagina, idioma in PAGINAS.items():
        html = (demos_regenerados / "casa-selva-tulum" / pagina).read_text(
            encoding="utf-8"
        )
        assert RIBBON_TEXTS[idioma] in html, f"{pagina}: texto de cinta equivocado."
        for otro, texto in RIBBON_TEXTS.items():
            if otro != idioma:
                assert texto not in html, f"{pagina}: se colo la cinta en {otro}."


# --- 2. Simetria: una guia real no se marca (mutacion A) ---------------------

PAYLOAD_BASE = {
    "metadata": {"slug": "candado-guia-real"},
    "property": {
        "property_name": "Casa Candado",
        "property_address": "1 Test Street, Test City",
        "style": "Minimalist",
        "property_environment": "City",
        "primary_language": "English",
    },
    "content": {
        "about_house": {"welcome_message": "Welcome."},
        "checkin": {"checkin_time": "3:00 PM", "checkout_time": "11:00 AM"},
        "contact_social": {"host_email": "hola@example.com"},
    },
}


def _genera(payload, destino):
    """Corre el mismo camino que el generador real: guia web + imprimible."""
    env = _entorno(destino, OPENAI_TRANSLATION_REQUIRED="false")
    crudo = json.dumps(payload)
    _corre([str(SCRIPT_DIR / "generate_villa.py"), crudo], env)
    _corre([str(SCRIPT_DIR / "build_print_pdf.py"), crudo], env)
    return destino / payload["metadata"]["slug"]


def test_el_mismo_payload_con_y_sin_demo_mode(tmp_path):
    """Un solo flag separa la guia de muestra de la guia por la que se pago."""
    real = json.loads(json.dumps(PAYLOAD_BASE))
    demo = json.loads(json.dumps(PAYLOAD_BASE))
    demo["content"]["demo_mode"] = True

    salida_real = _genera(real, tmp_path / "real")
    salida_demo = _genera(demo, tmp_path / "demo")

    for pagina, idioma in PAGINAS.items():
        afirma_sin_marca(
            (salida_real / pagina).read_text(encoding="utf-8"), f"real/{pagina}"
        )
        afirma_marca(
            (salida_demo / pagina).read_text(encoding="utf-8"),
            idioma,
            f"demo/{pagina}",
        )


# --- 4. Un ancla rota se cae fuerte, no en silencio ---------------------------

PLANTILLA_MINIMA = (
    "<html><head><title>T</title></head>\n<body>\n<p>x</p>\n</body></html>"
)


def test_sin_demo_mode_la_funcion_no_toca_el_html():
    assert inject_demo_mark(PLANTILLA_MINIMA, False, "English") == PLANTILLA_MINIMA
    assert inject_demo_mark(PLANTILLA_MINIMA, None, "Español") == PLANTILLA_MINIMA


def test_con_demo_mode_la_funcion_pone_las_tres_piezas():
    for idioma in RIBBON_TEXTS:
        afirma_marca(inject_demo_mark(PLANTILLA_MINIMA, True, idioma), idioma, idioma)


def test_ancla_perdida_o_duplicada_tumba_la_generacion():
    for roto in (
        PLANTILLA_MINIMA.replace("</title>", ""),
        PLANTILLA_MINIMA.replace("<body>", ""),
        PLANTILLA_MINIMA.replace("</head>", ""),
        PLANTILLA_MINIMA.replace("<body>", "<body><body>"),
    ):
        with pytest.raises(ValueError, match="marca de demo"):
            inject_demo_mark(roto, True, "English")


def test_el_idioma_desconocido_cae_al_texto_en_ingles():
    marcado = inject_demo_mark(PLANTILLA_MINIMA, True, "Klingon")
    assert RIBBON_TEXTS["English"] in marcado
