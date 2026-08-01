"""Marca legal de las guias demo: `<meta robots noindex>` + cinta visible.

Las 4 guias demo publican propiedades FICTICIAS. Sin esta marca quedan
indexables y sin aviso: indistinguibles de la guia de un cliente que pago.

Hasta ahora la marca vivia SOLO en el HTML ya publicado, puesta a mano por el
commit `8433e82`. Cada regeneracion la borraba y habia que reinyectarla a mano
(paso en el LOTE B). Aqui la produce el generador a partir de `demo_mode`, que
ya viajaba en el payload de los demos (`_generate_demo*.py`) y que el generador
ya leia para inyectar los datos privados ficticios.

Simetria que importa igual: una guia REAL (sin `demo_mode`) no recibe ni el
noindex ni la cinta — seria sacar de Google la guia por la que alguien pago.

El bloque que emite esta funcion es identico byte por byte al que hoy esta
publicado, para que regenerar los 4 demos no mueva las 20 paginas.
"""

ROBOTS_META = '<meta name="robots" content="noindex, nofollow">'

RIBBON_CLASS = "mg-demo-ribbon"

# Textos aprobados de la cinta, por idioma. No se traducen al vuelo: son texto
# legal y viajan tal cual.
RIBBON_TEXTS = {
    "English": (
        "DEMO · Sample guide with a fictional property. Not a real booking."
    ),
    "Español": (
        "DEMO · Guía de muestra con una propiedad ficticia. "
        "No es una reserva real."
    ),
    "Français": (
        "DÉMO · Livret d’exemple avec un logement fictif. "
        "Ce n’est pas une vraie réservation."
    ),
}

# El comentario del CSS menciona <body> y <head> a proposito: explica por que la
# cinta va fija abajo. Por eso el orden de inyeccion de abajo no es negociable
# (la cinta entra en <body> ANTES de que este bloque meta esos literales).
RIBBON_STYLE = """<style>
/* Marca de demo (auditoria de consistencia, divergencia 18): estas 4 guias son
   muestras con propiedades ficticias y estaban publicadas sin distinguirse de
   una guia real de cliente. Va FIJA abajo y no sticky arriba: estas paginas
   tienen overflow en <body>, asi que un sticky se despega al desplazarse, y
   arriba taparia la barra de idioma. El noindex del <head> las saca de los
   buscadores; en impresion no aparece. */
.mg-demo-ribbon {
  position: fixed; left: 50%; transform: translateX(-50%);
  bottom: 14px; z-index: 99999; max-width: calc(100vw - 24px);
  background: rgba(32, 32, 32, .92); color: #fff;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
  font-size: 11.5px; font-weight: 700; letter-spacing: .03em;
  text-align: center; padding: 7px 14px; border-radius: 999px;
  box-shadow: 0 6px 20px rgba(0,0,0,.22); pointer-events: none;
}
@media print { .mg-demo-ribbon { display: none; } }
</style>"""


def ribbon_html(language):
    """La cinta visible en el idioma de la pagina (English si no hay texto)."""
    text = RIBBON_TEXTS.get(language, RIBBON_TEXTS["English"])
    return f'<div class="{RIBBON_CLASS}" role="note">{text}</div>'


def _replace_once(html, anchor, replacement):
    """Reemplaza `anchor` exigiendo que aparezca exactamente una vez.

    Si la plantilla cambia y el ancla desaparece o se duplica, la generacion se
    cae aqui con un mensaje claro. Un `str.replace` silencioso dejaria salir la
    guia demo sin marca, que es justo el defecto que esto viene a cerrar.
    """
    encontradas = html.count(anchor)
    if encontradas != 1:
        raise ValueError(
            f"marca de demo: se esperaba 1 ancla {anchor!r} en la plantilla, "
            f"hay {encontradas}. La marca de demo no se pudo inyectar."
        )
    return html.replace(anchor, replacement, 1)


def inject_demo_mark(html, demo_mode, language, head_gap="\n\n"):
    """Agrega noindex + cinta al HTML si la guia es demo; si no, lo deja igual.

    `head_gap` reproduce el espaciado que ya tiene cada salida publicada:
    "\\n\\n" en `master.html` (el bloque va tras el script de analytics) y "\\n"
    en `print_letter.html`. Existe solo para que regenerar no mueva bytes que
    nadie pidio mover.
    """
    if not demo_mode:
        return html

    html = _replace_once(html, "</title>", "</title>\n    " + ROBOTS_META)
    html = _replace_once(html, "<body>", "<body>\n" + ribbon_html(language))
    html = _replace_once(html, "</head>", head_gap + RIBBON_STYLE + "\n</head>")
    return html
