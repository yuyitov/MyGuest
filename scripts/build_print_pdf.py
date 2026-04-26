import sys
import json
import os
from html import escape

SUPPORTED_LANGUAGES = ["English", "Español", "Français"]

UI_STRINGS = {
    "English": {
        "eyebrow": "WELCOME",
        "arrival": "Arrival",
        "about_stay": "About the stay",
        "location_transport": "Location & transport",
        "house_info": "House info",
        "recommendations": "Recommendations",
        "contact": "Contact",
        "checkin": "Check-in",
        "checkout": "Check-out",
        "pet_friendly": "Pet friendly",
        "yes": "Yes",
        "no": "No",
        "open_maps": "Google Maps",
        "leave_review": "Airbnb review",
        "instagram": "Instagram",
        "host_email": "Host email",
        "primary_language": "Primary language",
        "footer": "Public guest version only. Private access details are intentionally excluded.",
        "html_lang": "en",
    },
    "Español": {
        "eyebrow": "BIENVENIDO",
        "arrival": "Llegada",
        "about_stay": "Sobre la estancia",
        "location_transport": "Ubicación y transporte",
        "house_info": "Información de la casa",
        "recommendations": "Recomendaciones",
        "contact": "Contacto",
        "checkin": "Llegada",
        "checkout": "Salida",
        "pet_friendly": "Mascotas permitidas",
        "yes": "Sí",
        "no": "No",
        "open_maps": "Google Maps",
        "leave_review": "Reseña Airbnb",
        "instagram": "Instagram",
        "host_email": "Correo del anfitrión",
        "primary_language": "Idioma principal",
        "footer": "Versión pública para huéspedes. Los datos de acceso privado se excluyen intencionalmente.",
        "html_lang": "es",
    },
    "Français": {
        "eyebrow": "BIENVENUE",
        "arrival": "Arrivée",
        "about_stay": "À propos du séjour",
        "location_transport": "Emplacement et transport",
        "house_info": "Informations sur la maison",
        "recommendations": "Recommandations",
        "contact": "Contact",
        "checkin": "Arrivée",
        "checkout": "Départ",
        "pet_friendly": "Animaux acceptés",
        "yes": "Oui",
        "no": "Non",
        "open_maps": "Google Maps",
        "leave_review": "Avis Airbnb",
        "instagram": "Instagram",
        "host_email": "Email de l’hôte",
        "primary_language": "Langue principale",
        "footer": "Version publique destinée aux invités. Les informations d’accès privé sont volontairement exclues.",
        "html_lang": "fr",
    },
}

STYLE_MAP = {
    "Coastal": {"primary": "#2C7A7B", "accent": "#F4A261", "text": "#1F3A3A"},
    "Minimalist": {"primary": "#8B6F47", "accent": "#D9CEBA", "text": "#3A2A1C"},
    "Classic": {"primary": "#000000", "accent": "#A0A0A0", "text": "#1A1A1A"},
    "Sunset": {"primary": "#E76F51", "accent": "#E9C46A", "text": "#264653"},
}

EMPTY_TEXT_VALUES = {"", "-", "n/a", "na", "none", "null", "undefined"}


def safe_text(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return normalize_text_block(value)
    if isinstance(value, dict):
        return normalize_text_block(value)
    text = str(value).strip()
    if text.lower() in EMPTY_TEXT_VALUES:
        return ""
    return text


def normalize_text_block(value):
    if value is None:
        return ""
    if isinstance(value, list):
        parts = [safe_text(item) for item in value if safe_text(item)]
        return "\n".join(parts).strip()
    if isinstance(value, dict):
        parts = []
        for item in value.values():
            if safe_text(item):
                parts.append(safe_text(item))
        return "\n".join(parts).strip()
    text = str(value).strip()
    return "" if text.lower() in EMPTY_TEXT_VALUES else text


def has_value(value):
    return safe_text(value) != ""


def safe_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"yes", "true", "sí", "si", "1"}:
        return True
    if text in {"no", "false", "0"}:
        return False
    return None


def resolve_language(primary_language):
    clean = safe_text(primary_language)
    return clean if clean in SUPPORTED_LANGUAGES else "English"


def row_html(label, value):
    clean = normalize_text_block(value)
    if not clean:
        return ""
    return (
        '<div class="info-row">'
        f'<span class="info-label">{escape(label)}:</span> '
        f'{escape(clean)}'
        "</div>"
    )


def paragraph_html(value):
    clean = normalize_text_block(value)
    if not clean:
        return ""
    return f'<p class="paragraph">{escape(clean)}</p>'


def link_line_html(label, url):
    clean_url = safe_text(url)
    if not clean_url:
        return ""
    return (
        '<div class="info-row">'
        f'<span class="info-label">{escape(label)}:</span> '
        f'<span>{escape(clean_url)}</span>'
        "</div>"
    )


def section_html(title, body_html):
    if not body_html.strip():
        return ""
    return (
        '<section class="section">'
        f'<h2 class="section-title">{escape(title)}</h2>'
        f"{body_html}"
        "</section>"
    )


def build_sections(content, ui):
    sections = []

    checkin = content.get("checkin", {}) or {}
    checkin_body = ""
    checkin_body += row_html(ui["checkin"], checkin.get("checkin_time"))
    checkin_body += row_html(ui["checkout"], checkin.get("checkout_time"))
    checkin_body += paragraph_html(checkin.get("house_access_public"))
    checkin_body += paragraph_html(checkin.get("parking_info"))
    sections.append(section_html(ui["arrival"], checkin_body))

    about_house = content.get("about_house", {}) or {}
    about_body = ""
    about_body += paragraph_html(about_house.get("welcome_message"))
    about_body += paragraph_html(about_house.get("about_hosts"))
    about_body += paragraph_html(about_house.get("amenities_list"))

    pet_value = safe_bool(about_house.get("pet_friendly"))
    if pet_value is True:
        about_body += row_html(ui["pet_friendly"], ui["yes"])
    elif pet_value is False:
        about_body += row_html(ui["pet_friendly"], ui["no"])

    about_body += paragraph_html(about_house.get("pet_rules"))
    sections.append(section_html(ui["about_stay"], about_body))

    location_transport = content.get("location_transport", {}) or {}
    location_body = ""
    location_body += paragraph_html(location_transport.get("directions_text"))
    location_body += paragraph_html(location_transport.get("transport_options"))
    location_body += link_line_html(ui["open_maps"], location_transport.get("google_maps_link"))
    sections.append(section_html(ui["location_transport"], location_body))

    rules_info = content.get("rules_info", {}) or {}
    rules_body = ""
    rules_body += paragraph_html(rules_info.get("house_rules"))
    rules_body += paragraph_html(rules_info.get("things_to_know"))
    rules_body += paragraph_html(rules_info.get("before_you_leave"))
    sections.append(section_html(ui["house_info"], rules_body))

    recommendations = content.get("recommendations", {}) or {}
    recommendations_body = ""
    recommendations_body += paragraph_html(recommendations.get("places_to_eat"))
    recommendations_body += paragraph_html(recommendations.get("places_to_drink"))
    recommendations_body += paragraph_html(recommendations.get("things_to_do"))
    recommendations_body += paragraph_html(recommendations.get("local_directory"))
    sections.append(section_html(ui["recommendations"], recommendations_body))

    contact_social = content.get("contact_social", {}) or {}
    contact_body = ""
    contact_body += row_html(ui["host_email"], contact_social.get("host_email"))
    contact_body += paragraph_html(contact_social.get("emergency_contacts"))
    contact_body += link_line_html(ui["leave_review"], contact_social.get("airbnb_review_link"))

    instagram = safe_text(contact_social.get("instagram_handle"))
    if instagram:
        instagram_value = instagram if instagram.startswith("@") else f"@{instagram}"
        contact_body += row_html(ui["instagram"], instagram_value)

    sections.append(section_html(ui["contact"], contact_body))
    return "\n".join(section for section in sections if section.strip())


def render_print_html(payload):
    metadata = payload.get("metadata", {}) or {}
    property_data = payload.get("property", {}) or {}
    content = payload.get("content", {}) or {}

    villa_name = safe_text(property_data.get("property_name")) or "My Villa"
    property_address = safe_text(property_data.get("property_address"))
    primary_language = resolve_language(property_data.get("primary_language"))
    ui = UI_STRINGS[primary_language]

    selected_style = safe_text(property_data.get("style")) or "Minimalist"
    style = STYLE_MAP.get(selected_style, STYLE_MAP["Minimalist"])

    with open("templates/print_letter.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{HTML_LANG}}", escape(ui["html_lang"]))
    html = html.replace("{{VILLA_NAME}}", escape(villa_name))
    html = html.replace("{{PROPERTY_ADDRESS}}", escape(property_address))
    html = html.replace("{{PRIMARY_LANGUAGE}}", escape(primary_language))
    html = html.replace("{{PRIMARY_LANGUAGE_LABEL}}", escape(ui["primary_language"]))
    html = html.replace("{{EYEBROW}}", escape(ui["eyebrow"]))
    html = html.replace("{{CONTENT_SECTIONS}}", build_sections(content, ui))
    html = html.replace("{{FOOTER_TEXT}}", escape(ui["footer"]))
    html = html.replace("{{COLOR_PRIMARY}}", style["primary"])
    html = html.replace("{{COLOR_ACCENT}}", style["accent"])
    html = html.replace("{{COLOR_TEXT}}", style["text"])

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

    output_dir = os.path.join("public", "villas", slug)
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
