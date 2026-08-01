import sys
import json
import os
from html import escape

# Marca legal de demo. No es opcional como los dos imports de abajo: no depende
# de nada externo, y si faltara preferimos que la generacion se caiga a publicar
# una guia demo sin aviso.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _demo_mark import inject_demo_mark

# Optional Google Places lookup — imported lazily so missing file never breaks the build
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _places_lookup import lookup_place as _lookup_place
except Exception:
    def _lookup_place(name, location_hint, api_key):  # type: ignore[misc]
        return {}

# Optional translation — imported lazily so missing OPENAI_API_KEY never breaks the build
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from generate_villa import translate_public_content, flatten_content
    _TRANSLATION_AVAILABLE = True
except Exception:
    _TRANSLATION_AVAILABLE = False
    def translate_public_content(content_flat, target_language):  # type: ignore[misc]
        return content_flat
    def flatten_content(content):  # type: ignore[misc]
        return content

SUPPORTED_LANGUAGES = ["English", "Español", "Français"]
EMPTY_TEXT_VALUES = {"", "-", "n/a", "na", "none", "null", "undefined"}

LANGUAGE_ALIASES = {
    "english": "English",
    "español": "Español",
    "espanol": "Español",
    "spanish": "Español",
    "français": "Français",
    "francais": "Français",
    "french": "Français",
}

PRINT_UI = {
    "English": {
        "html_lang": "en",
        "yes": "Yes",
        "no": "No",
        "eyebrow": "WELCOME",
        "guide_to": "Your Guide to",
        "arrival_script": "Arrival &",
        "arrival_title": "CHECK IN",
        "checkin": "CHECK IN",
        "checkout": "CHECK OUT",
        "access": "Property Access",
        "parking": "Parking",
        "maps": "Open on Maps",
        "house_script": "About The",
        "house_title": "HOUSE",
        "know_script": "Things",
        "know_title": "TO KNOW",
        "amenities": "Amenities",
        "pets": "Pets",
        "rules_script": "House",
        "rules_title": "RULES",
        "before_leave": "Before You Leave",
        "eat_script": "Places",
        "eat_title": "TO EAT",
        "drink_script": "Places",
        "drink_title": "TO DRINK",
        "do_script": "Things",
        "do_title": "TO DO",
        "directory": "Local Directory",
        "thanks_script": "Thank You",
        "thanks_sub": "for choosing",
        "contact": "Contact",
        "emergency": "Emergency",
        "email": "Email",
        "review": "Leave a Review",
        "instagram": "Instagram",
        "footer": "For the complete stay details, open the secure digital guide link provided by your host.",
    },
    "Español": {
        "html_lang": "es",
        "yes": "Sí",
        "no": "No",
        "eyebrow": "BIENVENIDO",
        "guide_to": "Tu Guía para",
        "arrival_script": "Llegada &",
        "arrival_title": "CHECK IN",
        "checkin": "CHECK IN",
        "checkout": "CHECK OUT",
        "access": "Acceso",
        "parking": "Estacionamiento",
        "maps": "Abrir en Mapa",
        "house_script": "Sobre La",
        "house_title": "CASA",
        "know_script": "Cosas que",
        "know_title": "SABER",
        "amenities": "Amenidades",
        "pets": "Mascotas",
        "rules_script": "Reglas de",
        "rules_title": "LA CASA",
        "before_leave": "Antes de Salir",
        "eat_script": "Dónde",
        "eat_title": "COMER",
        "drink_script": "Dónde",
        "drink_title": "TOMAR ALGO",
        "do_script": "Qué",
        "do_title": "HACER",
        "directory": "Directorio Local",
        "thanks_script": "Gracias",
        "thanks_sub": "por elegir",
        "contact": "Contacto",
        "emergency": "Emergencias",
        "email": "Correo",
        "review": "Dejar Reseña",
        "instagram": "Instagram",
        "footer": "Para ver todos los detalles completos de la estancia, abre el link seguro de la guía digital proporcionado por tu anfitrión.",
    },
    "Français": {
        "html_lang": "fr",
        "yes": "Oui",
        "no": "Non",
        "eyebrow": "BIENVENUE",
        "guide_to": "Votre Guide pour",
        "arrival_script": "Arrivée &",
        "arrival_title": "CHECK IN",
        "checkin": "CHECK IN",
        "checkout": "CHECK OUT",
        "access": "Accès",
        "parking": "Stationnement",
        "maps": "Ouvrir sur la Carte",
        "house_script": "À Propos de",
        "house_title": "LA MAISON",
        "know_script": "Ce qu'il faut",
        "know_title": "SAVOIR",
        "amenities": "Équipements",
        "pets": "Animaux",
        "rules_script": "Règles de",
        "rules_title": "LA MAISON",
        "before_leave": "Avant le Départ",
        "eat_script": "Où",
        "eat_title": "MANGER",
        "drink_script": "Où",
        "drink_title": "BOIRE",
        "do_script": "Activités",
        "do_title": "À FAIRE",
        "directory": "Répertoire Local",
        "thanks_script": "Merci",
        "thanks_sub": "pour avoir choisi",
        "contact": "Contact",
        "emergency": "Urgence",
        "email": "Email",
        "review": "Laisser un Avis",
        "instagram": "Instagram",
        "footer": "Pour consulter tous les détails complets du séjour, ouvrez le lien sécurisé du guide numérique fourni par votre hôte.",
    },
}

STYLE_MAP = {
    "Minimalist": {
        "primary": "#8B6F47", "accent": "#D9CEBA", "text": "#3A2A1C",
        "dark": "#3D2A1A", "cover_style": "classic",
    },
    "Coastal": {
        "primary": "#2C7A7B", "accent": "#A8D5D5", "text": "#1F3A3A",
        "dark": "#1A3C3C", "cover_style": "overlay",
    },
    "Classic": {
        "primary": "#2C2C2C", "accent": "#D4CFC9", "text": "#1A1A1A",
        "dark": "#111111", "cover_style": "split",
    },
    "Sunset": {
        "primary": "#E76F51", "accent": "#E9C46A", "text": "#264653",
        "dark": "#1A2E38", "cover_style": "warm",
    },
}

COVER_IMAGES_BY_ENV = {
    "Beach": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1400&q=80",
    "City":  "https://myguestguide.com/assets/covers/city.png",
    "Cozy":  "https://myguestguide.com/assets/covers/cozy.png",
}

ENV_ALIASES = {
    "beach": "Beach", "playa": "Beach", "coastal": "Beach",
    "city": "City", "ciudad": "City", "urban": "City", "urbano": "City",
    "cozy": "Cozy", "cosy": "Cozy", "homey": "Cozy",
    "countryside": "Cozy", "country": "Cozy",
}


def _rewrap_translated(base_content, translated_flat):
    """Put flat translated values back into the nested content structure."""
    import copy
    result = copy.deepcopy(base_content)
    for section_data in result.values():
        if isinstance(section_data, dict):
            for field in list(section_data.keys()):
                if field in translated_flat:
                    section_data[field] = translated_flat[field]
    return result

IMAGES = {
    "welcome":  "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=900&q=80",
    "arrival":  "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=900&q=80",
    "house":    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=900&q=80",
    "rules":    "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=900&q=80",
    "eat":      "https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&w=900&q=80",
    "drink":    "https://images.unsplash.com/photo-1470337458703-46ad1756a187?auto=format&fit=crop&w=900&q=80",
    "do":       "https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=900&q=80",
}

# ── Utilities ──────────────────────────────────────────────────────

def safe_text(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return normalize_text_block(value)
    if isinstance(value, dict):
        return normalize_text_block(value)
    text = str(value).strip()
    return "" if text.lower() in EMPTY_TEXT_VALUES else text


def _clean_seps(text):
    import re as _re
    return _re.sub(r'\s*[�·•]\s*', '\n', text).strip()


def normalize_text_block(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(safe_text(i) for i in value if safe_text(i)).strip()
    if isinstance(value, dict):
        return "\n".join(safe_text(i) for i in value.values() if safe_text(i)).strip()
    text = str(value).strip()
    if not text or text.lower() in EMPTY_TEXT_VALUES:
        return ""
    return _clean_seps(text)


def has_value(v):
    return safe_text(v) != ""


def safe_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    t = str(value).strip().lower()
    if t in {"yes", "true", "sí", "si", "1", "oui"}:
        return True
    if t in {"no", "false", "0", "non"}:
        return False
    return None


def resolve_language(lang):
    clean = safe_text(lang)
    if clean in SUPPORTED_LANGUAGES:
        return clean
    normalized = LANGUAGE_ALIASES.get(clean.lower())
    return normalized if normalized else "English"


def resolve_env(raw):
    t = safe_text(raw).strip().lower()
    normalized = ENV_ALIASES.get(t, t.title())
    return normalized if normalized in COVER_IMAGES_BY_ENV else "Beach"


def h(text):
    return escape(safe_text(text))


def ht(text):
    return escape(normalize_text_block(text)).replace("\n", "<br>")


def split_lines(text, max_items=10):
    t = normalize_text_block(text)
    if not t:
        return []
    return [ln.strip() for ln in t.split("\n") if ln.strip()][:max_items]


def gf(content, block, field):
    return safe_text((content.get(block) or {}).get(field))


def get_numbered_places(content, prefix, link_field, max_items=5):
    recs = content.get("recommendations") or {}
    places = []
    for i in range(1, max_items + 1):
        name = safe_text(recs.get(f"{prefix}_{i}_name"))
        if not name:
            continue
        link = safe_text(recs.get(f"{prefix}_{i}_{link_field}")) or ""
        desc = safe_text(
            recs.get(f"{prefix}_{i}_description") or recs.get(f"{prefix}_{i}_notes")
        ) or ""
        phone = safe_text(recs.get(f"{prefix}_{i}_phone")) or ""
        location = safe_text(recs.get(f"{prefix}_{i}_address")) or ""
        places.append({"name": name, "link": link, "desc": desc, "phone": phone, "location": location})
    return places


def get_restaurants(content):
    places = get_numbered_places(content, "restaurant", "maps_link")
    if places:
        return places
    legacy = gf(content, "recommendations", "places_to_eat")
    return [{"name": "Restaurants", "link": "", "desc": legacy}] if legacy else []


def get_bars(content):
    places = get_numbered_places(content, "bar", "maps_link")
    if places:
        return places
    legacy = gf(content, "recommendations", "places_to_drink")
    return [{"name": "Bars & Drinks", "link": "", "desc": legacy}] if legacy else []


def get_activities(content):
    places = get_numbered_places(content, "activity", "link")
    if places:
        return places
    legacy = gf(content, "recommendations", "things_to_do")
    return [{"name": "Things to Do", "link": "", "desc": legacy}] if legacy else []


# ── HTML helpers ───────────────────────────────────────────────────

def page(inner, extra_class=""):
    cls = ("book-page " + extra_class).strip()
    return f'<div class="{cls}">{inner}</div>\n'


def side_img(src):
    return f'<img class="side-photo" src="{h(src)}" alt="" loading="eager">'


# ── Page builders ──────────────────────────────────────────────────

def build_cover(villa_name, address, ui, cover_img, style):
    img = cover_img
    cover_style = style.get("cover_style", "classic")
    addr_html = f'<div class="cover-address">{h(address)}</div>' if address else ""

    text_block = f"""
<div class="cover-welcome">{h(ui['eyebrow'])}</div>
<span class="cover-script">{h(ui['guide_to'])}</span>
<div class="cover-name">{h(villa_name)}</div>
<div class="cover-rule"></div>
{addr_html}"""

    if cover_style == "overlay":
        body = f"""
<div class="cover-coastal">
  <img class="cover-coastal-photo" src="{h(img)}" alt="" loading="eager">
  <div class="cover-coastal-body">{text_block}</div>
</div>"""
        return page(body, "cover-pg cover-alt-pg")

    elif cover_style == "split":
        body = f"""
<table class="cover-classic"><tr>
  <td class="cover-classic-left">
    {text_block}
  </td>
  <td class="cover-classic-right"><img src="{h(img)}" alt="" loading="eager"></td>
</tr></table>"""
        return page(body, "cover-pg cover-alt-pg")

    elif cover_style == "warm":
        body = f"""
<div class="cover-sunset">
  <img class="cover-sunset-photo" src="{h(img)}" alt="" loading="eager">
  <div class="cover-sunset-overlay"></div>
  <div class="cover-sunset-body">{text_block}</div>
</div>"""
        return page(body, "cover-pg cover-alt-pg")

    else:
        body = f"""
<img class="cover-photo" src="{h(img)}" alt="" loading="eager">
<div class="cover-body">{text_block}</div>"""
        return page(body, "cover-pg")


def build_welcome(content, ui):
    msg = gf(content, "about_house", "welcome_message")
    hosts = gf(content, "about_house", "about_hosts")
    amenities_raw = gf(content, "about_house", "amenities_list")

    if not msg and not hosts:
        return ""

    amenity_items = split_lines(amenities_raw.replace(",", "\n") if amenities_raw else "", 8)
    chips = "".join(f'<span class="amenity-chip">{h(a)}</span>' for a in amenity_items)
    chips_html = f'<div class="amenity-chips">{chips}</div>' if chips else ""

    left = f"""
<div class="welcome-img-wrap">
  <img class="welcome-photo" src="{h(IMAGES['welcome'])}" alt="" loading="eager">
  <span class="welcome-overlay-script">Welcome</span>
</div>"""

    right = f"""
<div class="page-heading">
  <span class="page-script">{h(ui['house_script'])}</span>
  <div class="page-bold">{h(ui['house_title'])}</div>
</div>
{f'<div class="page-text">{ht(msg)}</div>' if msg else ""}
{f'<div class="page-text hosts-block">{ht(hosts)}</div>' if hosts else ""}
{chips_html}"""

    body = f"""
<table class="split-layout"><tr>
  <td class="split-left-cell">{left}</td>
  <td class="split-right-cell">{right}</td>
</tr></table>"""
    return page(body, "welcome-pg")


def build_arrival(content, ui):
    checkin = gf(content, "checkin", "checkin_time")
    checkout = gf(content, "checkin", "checkout_time")
    access = gf(content, "checkin", "house_access_public")
    parking = gf(content, "checkin", "parking_info")
    maps = gf(content, "location_transport", "google_maps_link")
    directions = gf(content, "location_transport", "directions_text")

    if not any([checkin, checkout, access, parking]):
        return ""

    ci_card = f"""
<td class="time-card">
  <span class="time-label">{h(ui['checkin'])}</span>
  <div class="time-value">{h(checkin) if checkin else '—'}</div>
</td>""" if checkin else ""

    co_card = f"""
<td class="time-spacer"></td>
<td class="time-card">
  <span class="time-label">{h(ui['checkout'])}</span>
  <div class="time-value">{h(checkout) if checkout else '—'}</div>
</td>""" if checkout else ""

    time_grid = f'<table class="time-grid"><tr>{ci_card}{co_card}</tr></table>' if (checkin or checkout) else ""

    access_block = f"""
<div class="info-block">
  <div class="info-block-label">{h(ui['access'])}</div>
  <div class="info-block-text">{ht(access)}</div>
</div>""" if access else ""

    parking_block = f"""
<div class="info-block">
  <div class="info-block-label">{h(ui['parking'])}</div>
  <div class="info-block-text">{ht(parking)}</div>
</div>""" if parking else ""

    dir_block = f"""
<div class="info-block">
  <div class="info-block-text">{ht(directions)}</div>
</div>""" if directions else ""

    left = f"""
<div class="page-heading">
  <span class="page-script">{h(ui['arrival_script'])}</span>
  <div class="page-bold">{h(ui['arrival_title'])}</div>
</div>
{time_grid}
{access_block}
{parking_block}
{dir_block}"""

    body = f"""
<table class="split-layout arrival-layout"><tr>
  <td class="arrival-content-cell">{left}</td>
  <td class="arrival-image-cell">{side_img(IMAGES['arrival'])}</td>
</tr></table>"""
    return page(body, "arrival-pg")


def build_house(content, ui):
    amenities = gf(content, "about_house", "amenities_list")
    things = gf(content, "rules_info", "things_to_know")
    pet_raw = (content.get("about_house") or {}).get("pet_friendly")
    pet_rules = gf(content, "about_house", "pet_rules")
    pet = safe_bool(pet_raw)

    if not amenities and not things:
        return ""

    # Left: About the House
    amenity_lines = split_lines(amenities.replace(",", "\n") if amenities else "", 10)
    amenity_html = "".join(f'<div class="amenity-row">{h(a)}</div>' for a in amenity_lines)

    pet_html = ""
    if pet is not None:
        pet_val = ui.get("yes", "Yes") if pet is True else ui.get("no", "No")
        pet_html = f'<div class="info-block"><div class="info-block-label">{h(ui["pets"])}</div><div class="info-block-text">{pet_val}</div></div>'
    if pet_rules:
        pet_html += f'<div class="info-block-text" style="margin-top:4px">{ht(pet_rules)}</div>'

    left = f"""
<div class="page-heading">
  <span class="page-script">{h(ui['house_script'])}</span>
  <div class="page-bold">{h(ui['house_title'])}</div>
</div>
<img class="house-photo" src="{h(IMAGES['house'])}" alt="" loading="eager">
{f'<div class="amenities-list">{amenity_html}</div>' if amenity_html else ""}
{pet_html}"""

    # Right: Things to Know
    know_rows = split_lines(things, 8)
    rows_html = ""
    for row in know_rows:
        if ":" in row:
            parts = row.split(":", 1)
            rows_html += f'<div class="know-row"><span class="know-label">{h(parts[0].strip())}</span><span class="know-text">{h(parts[1].strip())}</span></div>'
        else:
            rows_html += f'<div class="know-row"><span class="know-label-full">{h(row)}</span></div>'

    right = f"""
<div class="page-heading">
  <span class="page-script">{h(ui['know_script'])}</span>
  <div class="page-bold">{h(ui['know_title'])}</div>
</div>
<div class="know-table">{rows_html}</div>
<div id="private-house-print-block-{ui['html_lang']}"></div>"""

    body = f"""
<table class="split-layout house-layout"><tr>
  <td class="house-left-cell">{left}</td>
  <td class="house-right-cell">{right}</td>
</tr></table>"""
    return page(body, "house-pg")


def build_rules(content, ui):
    rules_text = gf(content, "rules_info", "house_rules")
    before = gf(content, "rules_info", "before_you_leave")

    if not rules_text and not before:
        return ""

    rule_lines = split_lines(rules_text, 6)

    def rule_cell(idx, text):
        num = f"{idx:02d}"
        if ":" in text:
            parts = text.split(":", 1)
            title = parts[0].strip().upper()
            desc = parts[1].strip()
        elif " - " in text:
            parts = text.split(" - ", 1)
            title = parts[0].strip().upper()
            desc = parts[1].strip()
        else:
            title = text.upper()
            desc = ""
        return f"""<td class="rule-card">
  <div class="rule-num">{num}</div>
  <div class="rule-title">{h(title)}</div>
  {f'<div class="rule-desc">{h(desc)}</div>' if desc else ""}
</td>"""

    # Paragraph mode: rules came as one continuous block (no meaningful line breaks)
    if len(rule_lines) <= 1:
        rules_html = (
            f'<div style="padding:0 var(--pad) 0.3cm">'
            f'<div class="page-text">{h(rules_text)}</div>'
            f'</div>'
        )
    else:
        # Grid mode: numbered 3-column cards
        grid_rows = ""
        for r in range(0, len(rule_lines), 3):
            chunk = rule_lines[r:r + 3]
            cells = "".join(rule_cell(r + i + 1, chunk[i]) for i in range(len(chunk)))
            while len(chunk) < 3:
                cells += '<td class="rule-card rule-empty"></td>'
                chunk.append("")
            grid_rows += f"<tr>{cells}</tr>"
        rules_html = f'<table class="rules-grid">{grid_rows}</table>'

    before_lines = split_lines(before, 8)
    before_html = ""
    if before_lines:
        items = "".join(f'<div class="checklist-item">{h(l)}</div>' for l in before_lines)
        before_html = f'<div class="before-section"><div class="before-title">{h(ui["before_leave"])}</div><div class="checklist">{items}</div></div>'

    top = f"""
<table class="rules-header-layout"><tr>
  <td class="rules-heading-cell">
    <div class="page-heading">
      <span class="page-script">{h(ui['rules_script'])}</span>
      <div class="page-bold">{h(ui['rules_title'])}</div>
    </div>
  </td>
  <td class="rules-image-cell">{side_img(IMAGES['rules'])}</td>
</tr></table>"""

    body = f"""
{top}
{rules_html}
{before_html}"""
    return page(body, "rules-pg")


def build_recommendations(content, ui, enriched=None):
    restaurants = get_restaurants(content)
    bars = get_bars(content)
    activities = get_activities(content)
    directory = gf(content, "recommendations", "local_directory")

    if not restaurants and not bars and not activities and not directory:
        return ""

    enriched = enriched or {}

    def _maps_address(url):
        """Fallback: extract query string from a Google Maps URL."""
        try:
            from urllib.parse import urlparse, parse_qs, unquote_plus
            parsed = urlparse(url)
            q = parse_qs(parsed.query).get("q", [None])[0]
            if q:
                return unquote_plus(q).strip()
        except Exception:
            pass
        return None

    def _is_maps_url(url):
        return "maps.google" in url or "goo.gl/maps" in url or "maps.app.goo.gl" in url

    def rec_section(script, title, places, img_src):
        if not places:
            return ""
        items = ""
        for p in places[:5]:
            name_html = h(p["name"])
            desc_html = f'<div class="rec-detail">{h(p["desc"])}</div>' if p.get("desc") else ""

            info = enriched.get(p["name"], {})

            # Address: Google Places → form field only (no maps URL extraction)
            address = info.get("address") or p.get("location") or ""

            # Phone: Google Places → form field
            phone = info.get("phone") or p.get("phone") or ""

            # Website: Google Places → activity link (if not a maps URL)
            website = info.get("website") or ""
            if not website and p.get("link") and not _is_maps_url(p["link"]):
                if p["link"].startswith(("http://", "https://")):
                    website = p["link"]

            addr_html    = f'<div class="rec-address">{h(address)}</div>' if address else ""
            phone_html   = f'<div class="rec-phone">{h(phone)}</div>' if phone else ""
            website_html = f'<div class="rec-website">{h(website)}</div>' if website else ""

            items += (
                f'<div class="rec-item">'
                f'<div class="rec-name">{name_html}</div>'
                f'{addr_html}{phone_html}{website_html}{desc_html}'
                f'</div>'
            )
        return f"""
<div class="rec-block">
  <div class="rec-heading">
    <span class="rec-script">{h(script)}</span>
    <span class="rec-bold">{h(title)}</span>
  </div>
  <div class="rec-list">{items}</div>
</div>"""

    left_col = rec_section(ui["eat_script"], ui["eat_title"], restaurants, IMAGES["eat"])
    left_col += rec_section(ui["drink_script"], ui["drink_title"], bars, IMAGES["drink"])

    right_col = rec_section(ui["do_script"], ui["do_title"], activities, IMAGES["do"])
    if directory:
        right_col += f'<div class="rec-block"><div class="rec-heading"><span class="rec-bold">{h(ui["directory"])}</span></div><div class="page-text">{ht(directory)}</div></div>'

    body = f"""
<table class="recs-layout"><tr>
  <td class="recs-col">{left_col}</td>
  <td class="recs-divider"></td>
  <td class="recs-col">{right_col}</td>
</tr></table>"""
    return page(body, "recs-pg")


def build_contact(content, villa_name, ui):
    email = gf(content, "contact_social", "host_email")
    emergency = gf(content, "contact_social", "emergency_contacts")
    review = gf(content, "contact_social", "airbnb_review_link")
    instagram_raw = gf(content, "contact_social", "instagram_handle")

    def contact_row(label, value):
        if not value:
            return ""
        return f'<div class="contact-row"><span class="contact-label">{h(label)}</span><span class="contact-val">{h(value)}</span></div>'

    instagram_display = instagram_raw
    if instagram_raw and not instagram_raw.startswith("@"):
        instagram_display = "@" + instagram_raw.lstrip("https://instagram.com/").lstrip("instagram.com/")

    contact_rows = contact_row(ui["email"], email)
    contact_rows += contact_row(ui["instagram"], instagram_display)
    contact_rows += '<div id="private-phone-contact-block"></div>'

    emergency_rows = f'<div class="emergency-text">{h(emergency)}</div>' if emergency else ""

    contact_block = f"""
<div class="thanks-section">
  <div class="thanks-section-title">{h(ui['contact'])}</div>
  <div class="contact-rows">{contact_rows}</div>
</div>"""

    emergency_block = ""
    if emergency_rows:
        emergency_block = f"""
<div class="thanks-section">
  <div class="thanks-section-title">{h(ui['emergency'])}</div>
  <div class="contact-rows">{emergency_rows}</div>
</div>"""

    body = f"""
<div class="thanks-center">
  <span class="thanks-script">{h(ui['thanks_script'])}</span>
  <div class="thanks-sub">{h(ui['thanks_sub'])} <em>{h(villa_name)}</em></div>
  {contact_block}
  {emergency_block}
  <div class="footer-brand">MyGuest · myguestguide.com</div>
</div>"""
    return page(body, "thanks-pg")


# ── Render ─────────────────────────────────────────────────────────

def render_print_html(payload):
    metadata = payload.get("metadata") or {}
    property_data = payload.get("property") or {}
    content = payload.get("content") or {}

    villa_name = safe_text(property_data.get("property_name")) or "My Villa"
    address = safe_text(property_data.get("property_address"))
    selected_style = safe_text(property_data.get("style")) or "Minimalist"
    primary_language = resolve_language(property_data.get("primary_language"))

    style = STYLE_MAP.get(selected_style, STYLE_MAP["Minimalist"])

    env = resolve_env(property_data.get("property_environment"))
    cover_img = COVER_IMAGES_BY_ENV.get(env, COVER_IMAGES_BY_ENV["Beach"])

    # Enrich places once (before language loop) to avoid 3× API calls
    places_api_key = os.environ.get("GOOGLE_PLACES_API_KEY", "")
    enriched: dict = {}
    if places_api_key:
        all_places = get_restaurants(content) + get_bars(content) + get_activities(content)
        for p in all_places:
            name = p.get("name", "")
            if name and name not in enriched:
                enriched[name] = _lookup_place(name, address or "", places_api_key)

    def _pages_for_lang(lang, translated_content=None):
        ui = PRINT_UI[lang]
        c = translated_content if translated_content is not None else content
        pages = [
            build_cover(villa_name, address, ui, cover_img, style),
            build_welcome(c, ui),
            build_arrival(c, ui),
            build_house(c, ui),
            build_rules(c, ui),
            build_recommendations(c, ui, enriched=enriched),
            build_contact(c, villa_name, ui),
        ]
        return "".join(p for p in pages if p)

    def _lang_divider(label):
        body = (
            f'<div style="display:flex;align-items:center;justify-content:center;'
            f'height:100%;min-height:22cm;text-align:center;">'
            f'<div style="font-family:\'Cormorant Garamond\',serif;font-size:54pt;'
            f'letter-spacing:0.12em;color:#8B6F47;">{h(label)}</div>'
            f'</div>'
        )
        return page(body, "lang-divider-pg")

    sections = []
    for i, lang in enumerate(SUPPORTED_LANGUAGES):
        if i > 0:
            sections.append(_lang_divider(lang))
        if _TRANSLATION_AVAILABLE and lang != primary_language:
            flat = flatten_content(content)
            translated_flat = translate_public_content(flat, lang, source_language=primary_language)
            translated_content = _rewrap_translated(content, translated_flat)
            sections.append(_pages_for_lang(lang, translated_content))
        else:
            sections.append(_pages_for_lang(lang))
    pages_html = "".join(sections)

    ui = PRINT_UI[primary_language]

    _scripts_dir = os.path.dirname(os.path.abspath(__file__))
    _template_path = os.path.join(_scripts_dir, "..", "templates", "print_letter.html")
    with open(_template_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Va sobre la plantilla cruda, antes de meter el contenido: asi las anclas
    # (</title>, <body>, </head>) son las de la plantilla y ningun texto del
    # anfitrion puede confundirlas. El imprimible es trilingue en un solo
    # archivo, asi que la cinta va en el idioma principal, que es el `lang` del
    # documento.
    html = inject_demo_mark(
        html,
        bool(content.get("demo_mode")),
        primary_language,
        head_gap="\n",
    )

    html = html.replace("{{HTML_LANG}}", escape(ui["html_lang"]))
    html = html.replace("{{VILLA_NAME}}", escape(villa_name))
    html = html.replace("{{COLOR_PRIMARY}}", style["primary"])
    html = html.replace("{{COLOR_ACCENT}}", style["accent"])
    html = html.replace("{{COLOR_TEXT}}", style["text"])
    html = html.replace("{{COLOR_DARK}}", style["dark"])
    html = html.replace("{{PAGES_CONTENT}}", pages_html)

    slug = safe_text(metadata.get("slug")) or "demo"
    return slug, html


# Solo los demos oficiales publican print.pdf en public/. Las villas de clientes
# obtienen su printable completo via /print/<slug>?token= (Worker), nunca como
# archivo público.
OFFICIAL_DEMO_SLUGS = {
    "ocean-drive-retreat",
    "the-soho-loft",
    "casa-selva-tulum",
    "le-marais-flat",
}


def try_generate_pdf(html_path, pdf_path):
    try:
        from weasyprint import HTML  # type: ignore
    except Exception:
        return False, "WeasyPrint no está disponible en este entorno."
    try:
        HTML(filename=html_path).write_pdf(pdf_path)
        return True, None
    except Exception as error:
        return False, str(error)


def main():
    try:
        payload = json.loads(sys.argv[1])
    except Exception:
        print("Error al leer JSON")
        sys.exit(1)

    slug, html = render_print_html(payload)

    # Mismo contrato que `villas_root()` de generate_villa.py: por default
    # `public/villas/`, y `MYGUEST_VILLAS_ROOT` lo redirige para que las pruebas
    # regeneren en un temporal sin ensuciar `public/`. El imprimible se quedaba
    # fuera de esa regla y era el unico que escribia en `public/` a la fuerza.
    _villas_root = os.getenv("MYGUEST_VILLAS_ROOT", "").strip()
    if not _villas_root:
        _scripts_dir2 = os.path.dirname(os.path.abspath(__file__))
        _villas_root = os.path.join(_scripts_dir2, "..", "..", "public", "villas")

    output_dir = os.path.join(_villas_root, slug)
    os.makedirs(output_dir, exist_ok=True)

    html_path = os.path.join(output_dir, "print.html")
    pdf_path = os.path.join(output_dir, "print.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated {html_path}")

    if slug not in OFFICIAL_DEMO_SLUGS:
        print(f"print.pdf skipped (non-demo villa): {slug}")
        return

    ok, error = try_generate_pdf(html_path, pdf_path)
    if ok:
        print(f"Generated {pdf_path}")
    else:
        print(f"PDF skipped: {error}")


if __name__ == "__main__":
    main()
