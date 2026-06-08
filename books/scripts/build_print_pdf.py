import sys
import json
import os
from html import escape

SUPPORTED_LANGUAGES = ["English", "Español", "Français"]
EMPTY_TEXT_VALUES = {"", "-", "n/a", "na", "none", "null", "undefined"}

PRINT_UI = {
    "English": {
        "html_lang": "en",
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
    "City":  "../../assets/covers/city.png",
    "Cozy":  "../../assets/covers/cozy.png",
}

ENV_ALIASES = {
    "beach": "Beach", "playa": "Beach", "coastal": "Beach",
    "city": "City", "ciudad": "City", "urban": "City", "urbano": "City",
    "cozy": "Cozy", "cosy": "Cozy", "homey": "Cozy",
    "countryside": "Cozy", "country": "Cozy",
}

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
    return clean if clean in SUPPORTED_LANGUAGES else "English"


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
        location = safe_text(recs.get(f"{prefix}_{i}_location")) or ""
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
        pet_val = ("Yes" if pet is True else "No")
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
<div id="private-house-print-block"></div>"""

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

    # Build rows of 3
    grid_rows = ""
    for r in range(0, len(rule_lines), 3):
        chunk = rule_lines[r:r + 3]
        cells = "".join(rule_cell(r + i + 1, chunk[i]) for i in range(len(chunk)))
        # pad to 3 cells
        while len(chunk) < 3:
            cells += '<td class="rule-card rule-empty"></td>'
            chunk.append("")
        grid_rows += f"<tr>{cells}</tr>"

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
<table class="rules-grid">{grid_rows}</table>
{before_html}"""
    return page(body, "rules-pg")


def build_recommendations(content, ui):
    restaurants = get_restaurants(content)
    bars = get_bars(content)
    activities = get_activities(content)
    directory = gf(content, "recommendations", "local_directory")

    if not restaurants and not bars and not activities and not directory:
        return ""

    def _maps_address(url):
        """Extract location from a Google Maps URL for print."""
        try:
            from urllib.parse import urlparse, parse_qs, unquote_plus
            parsed = urlparse(url)
            q = parse_qs(parsed.query).get("q", [None])[0]
            if q:
                return unquote_plus(q).strip()
        except Exception:
            pass
        return None

    def rec_section(script, title, places, img_src):
        if not places:
            return ""
        items = ""
        for p in places[:5]:
            name_html = h(p["name"])
            desc_html = f'<div class="rec-detail">{h(p["desc"])}</div>' if p.get("desc") else ""
            addr_html = ""
            website_html = ""
            if p.get("link") and p["link"].startswith(("http://", "https://")):
                addr = _maps_address(p["link"])
                if addr:
                    addr_html = f'<div class="rec-address">{h(addr)}</div>'
                else:
                    from urllib.parse import urlparse as _up
                    _parsed = _up(p["link"])
                    _display = _parsed.netloc.lstrip("www.") + _parsed.path.rstrip("/")
                    if _display:
                        website_html = f'<div class="rec-website">{h(_display)}</div>'
            if not addr_html and p.get("location"):
                addr_html = f'<div class="rec-address">{h(p["location"])}</div>'
            phone_html = f'<div class="rec-phone">{h(p["phone"])}</div>' if p.get("phone") else ""
            items += f'<div class="rec-item"><div class="rec-name">{name_html}</div>{addr_html}{website_html}{phone_html}{desc_html}</div>'
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

    emergency_rows = f'<div class="emergency-text">{h(emergency)}</div>' if emergency else ""

    contact_block = ""
    if contact_rows:
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
  <div class="footer-note">{h(ui['footer'])}</div>
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
    ui = PRINT_UI[primary_language]

    env = resolve_env(property_data.get("property_environment"))
    cover_img = COVER_IMAGES_BY_ENV.get(env, COVER_IMAGES_BY_ENV["Beach"])

    pages = [
        build_cover(villa_name, address, ui, cover_img, style),
        build_welcome(content, ui),
        build_arrival(content, ui),
        build_house(content, ui),
        build_rules(content, ui),
        build_recommendations(content, ui),
        build_contact(content, villa_name, ui),
    ]
    pages_html = "".join(p for p in pages if p)

    _scripts_dir = os.path.dirname(os.path.abspath(__file__))
    _template_path = os.path.join(_scripts_dir, "..", "templates", "print_letter.html")
    with open(_template_path, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{HTML_LANG}}", escape(ui["html_lang"]))
    html = html.replace("{{VILLA_NAME}}", escape(villa_name))
    html = html.replace("{{COLOR_PRIMARY}}", style["primary"])
    html = html.replace("{{COLOR_ACCENT}}", style["accent"])
    html = html.replace("{{COLOR_TEXT}}", style["text"])
    html = html.replace("{{COLOR_DARK}}", style["dark"])
    html = html.replace("{{PAGES_CONTENT}}", pages_html)

    slug = safe_text(metadata.get("slug")) or "demo"
    return slug, html


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

    _scripts_dir2 = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.join(_scripts_dir2, "..", "..")
    output_dir = os.path.join(_project_root, "public", "villas", slug)
    os.makedirs(output_dir, exist_ok=True)

    html_path = os.path.join(output_dir, "print.html")
    pdf_path = os.path.join(output_dir, "print.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated {html_path}")

    ok, error = try_generate_pdf(html_path, pdf_path)
    if ok:
        print(f"Generated {pdf_path}")
    else:
        print(f"PDF skipped: {error}")


if __name__ == "__main__":
    main()
