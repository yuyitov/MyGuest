import sys
import json
import os
from html import escape


SUPPORTED_LANGUAGES = ["English", "Español", "Français"]


UI_STRINGS = {
    "English": {
        "arrival": "Arrival",
        "about_stay": "About the stay",
        "location_transport": "Location & transport",
        "house_info": "House info",
        "recommendations": "Recommendations",
        "contact": "Contact",
        "checkin": "Check In",
        "checkout": "Check Out",
        "pet_friendly": "Pet friendly",
        "yes": "Yes",
        "no": "No",
        "open_maps": "Open Google Maps",
        "leave_review": "Leave an Airbnb review",
        "instagram": "Instagram",
        "host_email": "Host email",
        "warm_welcome": "A Warm Welcome",
        "welcome_fallback": "We’re delighted to welcome you to your stay in Puerto Vallarta. Here you’ll find the essentials for a smooth arrival and a comfortable stay. We hope this guide helps you settle in and enjoy every moment of your visit.",
        "with_love": "With love",
        "enjoy_your_stay": "ENJOY YOUR STAY",
        "welcome_cover": "WELCOME",
        "your_guide": "Your Guide",
        "to": "TO",
        "html_lang": "en",
    },
    "Español": {
        "arrival": "Llegada",
        "about_stay": "Sobre la estancia",
        "location_transport": "Ubicación y transporte",
        "house_info": "Información de la casa",
        "recommendations": "Recomendaciones",
        "contact": "Contacto",
        "checkin": "Check In",
        "checkout": "Check Out",
        "pet_friendly": "Pet friendly",
        "yes": "Sí",
        "no": "No",
        "open_maps": "Abrir Google Maps",
        "leave_review": "Dejar reseña en Airbnb",
        "instagram": "Instagram",
        "host_email": "Correo del anfitrión",
        "warm_welcome": "Una Cálida Bienvenida",
        "welcome_fallback": "Nos da mucho gusto darte la bienvenida a tu estancia en Puerto Vallarta. Aquí encontrarás lo esencial para una llegada fluida y una estancia cómoda. Esperamos que esta guía te ayude a instalarte y disfrutar cada momento de tu visita.",
        "with_love": "Con cariño",
        "enjoy_your_stay": "DISFRUTA TU ESTANCIA",
        "welcome_cover": "BIENVENIDO",
        "your_guide": "Tu Guía",
        "to": "EN",
        "html_lang": "es",
    },
    "Français": {
        "arrival": "Arrivée",
        "about_stay": "À propos du séjour",
        "location_transport": "Emplacement et transport",
        "house_info": "Informations sur la maison",
        "recommendations": "Recommandations",
        "contact": "Contact",
        "checkin": "Check In",
        "checkout": "Check Out",
        "pet_friendly": "Animaux acceptés",
        "yes": "Oui",
        "no": "Non",
        "open_maps": "Ouvrir Google Maps",
        "leave_review": "Laisser un avis Airbnb",
        "instagram": "Instagram",
        "host_email": "Email de l’hôte",
        "warm_welcome": "Un Chaleureux Accueil",
        "welcome_fallback": "Nous sommes ravis de vous accueillir pour votre séjour à Puerto Vallarta. Vous trouverez ici l’essentiel pour une arrivée fluide et un séjour confortable. Nous espérons que ce guide vous aidera à vous installer et à profiter pleinement de votre visite.",
        "with_love": "Avec amour",
        "enjoy_your_stay": "PROFITEZ DE VOTRE SÉJOUR",
        "welcome_cover": "BIENVENUE",
        "your_guide": "Votre Guide",
        "to": "À",
        "html_lang": "fr",
    },
}


FALLBACK_COVER_IMAGE = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80"
FALLBACK_WELCOME_IMAGE = "https://images.unsplash.com/photo-1583241800698-e8ab01830a22?auto=format&fit=crop&w=1400&q=80"


def safe_text(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return ""
    text = str(value).strip()
    if text.lower() in {"", "-", "n/a", "na", "none"}:
        return ""
    return text


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


def paragraph_html(value):
    if not has_value(value):
        return ""
    return f'<p class="paragraph">{escape(safe_text(value))}</p>'


def row_html(label, value):
    if not has_value(value):
        return ""
    return f"""
        <div class="info-row">
            <div class="info-label">{escape(label)}</div>
            <div class="info-value">{escape(safe_text(value))}</div>
        </div>
    """


def section_html(title, body_html):
    if not body_html.strip():
        return ""
    return f"""
        <section class="card">
            <h2 class="section-title">{escape(title)}</h2>
            {body_html}
        </section>
    """


def link_button_html(label, url):
    clean_url = safe_text(url)
    if not clean_url:
        return ""
    return f'<a href="{escape(clean_url)}" class="btn" target="_blank" rel="noopener noreferrer">{escape(label)}</a>'


def resolve_language(primary_language):
    clean = safe_text(primary_language)
    return clean if clean in SUPPORTED_LANGUAGES else "English"


def build_language_bar(primary_language):
    chips = []
    for lang in SUPPORTED_LANGUAGES:
        css_class = "language-chip active" if lang == primary_language else "language-chip"
        chips.append(f'<div class="{css_class}">{escape(lang)}</div>')
    return "\n".join(chips)


def normalize_photo_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        photos = []
        for item in value:
            if isinstance(item, dict):
                candidate = (
                    item.get("url")
                    or item.get("src")
                    or item.get("fileUrl")
                    or item.get("downloadUrl")
                    or item.get("cdnUrl")
                )
                if has_value(candidate):
                    photos.append(safe_text(candidate))
            elif has_value(item):
                photos.append(safe_text(item))
        return photos

    if isinstance(value, dict):
        candidate = (
            value.get("url")
            or value.get("src")
            or value.get("fileUrl")
            or value.get("downloadUrl")
            or value.get("cdnUrl")
        )
        return [safe_text(candidate)] if has_value(candidate) else []

    if has_value(value):
        return [safe_text(value)]

    return []


def first_public_photo(content):
    return normalize_photo_list(content.get("property_photos"))[:1]


def image_block(url, alt_text, arch=False):
    clean_url = safe_text(url)
    if not clean_url:
        return ""
    wrapper_class = "cover-image-arch" if arch else ""
    if arch:
        return f'''
            <div class="{wrapper_class}">
                <img src="{escape(clean_url)}" alt="{escape(alt_text)}">
            </div>
        '''
    return f'<img src="{escape(clean_url)}" alt="{escape(alt_text)}">'


def build_cover_image_block(content, villa_name):
    photos = first_public_photo(content)
    if photos:
        return image_block(photos[0], villa_name, arch=True)
    return image_block(FALLBACK_COVER_IMAGE, villa_name, arch=True)


def build_welcome_image_block(content, villa_name):
    photos = first_public_photo(content)
    if photos:
        return image_block(photos[0], villa_name, arch=False)
    return image_block(FALLBACK_WELCOME_IMAGE, villa_name, arch=False)


def build_welcome_message_block(content, ui):
    welcome_message = safe_text(content.get("welcome_message"))
    final_message = welcome_message if welcome_message else ui["welcome_fallback"]
    return escape(final_message)


def icon_button_svg(kind):
    if kind == "maps":
        return """
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 21s-6-4.35-6-10a6 6 0 1 1 12 0c0 5.65-6 10-6 10Z"></path>
                <circle cx="12" cy="11" r="2.5" fill="currentColor" stroke="none"></circle>
            </svg>
        """
    if kind == "email":
        return """
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="3" y="5" width="18" height="14" rx="2"></rect>
                <path d="M4 7l8 6 8-6"></path>
            </svg>
        """
    return ""


def build_welcome_actions_block(content):
    actions = []

    maps_url = safe_text(content.get("google_maps_link"))
    if maps_url:
        actions.append(f'''
            <a class="welcome-action" href="{escape(maps_url)}" target="_blank" rel="noopener noreferrer" aria-label="Google Maps">
                {icon_button_svg("maps")}
            </a>
        ''')

    host_email = safe_text(content.get("host_email"))
    if host_email:
        actions.append(f'''
            <a class="welcome-action" href="mailto:{escape(host_email)}" aria-label="Email">
                {icon_button_svg("email")}
            </a>
        ''')

    return "\n".join(actions)


def build_checkin_checkout_block(content, ui):
    cards = []

    checkin_time = safe_text(content.get("checkin_time"))
    if checkin_time:
        cards.append(f"""
            <div class="arrival-card">
                <div class="arrival-label">{escape(ui["checkin"])}</div>
                <div class="arrival-time">{escape(checkin_time)}</div>
            </div>
        """)

    checkout_time = safe_text(content.get("checkout_time"))
    if checkout_time:
        cards.append(f"""
            <div class="arrival-card">
                <div class="arrival-label">{escape(ui["checkout"])}</div>
                <div class="arrival-time">{escape(checkout_time)}</div>
            </div>
        """)

    return "\n".join(cards)


def build_content_sections(content, ui):
    sections = []

    arrival_body = ""
    arrival_body += paragraph_html(content.get("house_access_public"))
    arrival_body += paragraph_html(content.get("parking_info"))
    sections.append(section_html(ui["arrival"], arrival_body))

    about_body = ""
    about_body += paragraph_html(content.get("about_hosts"))
    about_body += paragraph_html(content.get("amenities_list"))
    pet_value = safe_bool(content.get("pet_friendly"))
    if pet_value is True:
        about_body += row_html(ui["pet_friendly"], ui["yes"])
    elif pet_value is False:
        about_body += row_html(ui["pet_friendly"], ui["no"])
    about_body += paragraph_html(content.get("pet_rules"))
    sections.append(section_html(ui["about_stay"], about_body))

    location_body = ""
    location_body += paragraph_html(content.get("directions_text"))
    location_body += paragraph_html(content.get("transport_options"))
    location_body += link_button_html(ui["open_maps"], content.get("google_maps_link"))
    sections.append(section_html(ui["location_transport"], location_body))

    rules_body = ""
    rules_body += paragraph_html(content.get("house_rules"))
    rules_body += paragraph_html(content.get("things_to_know"))
    rules_body += paragraph_html(content.get("before_you_leave"))
    sections.append(section_html(ui["house_info"], rules_body))

    recommendations_body = ""
    recommendations_body += paragraph_html(content.get("places_to_eat"))
    recommendations_body += paragraph_html(content.get("places_to_drink"))
    recommendations_body += paragraph_html(content.get("things_to_do"))
    recommendations_body += paragraph_html(content.get("local_directory"))
    sections.append(section_html(ui["recommendations"], recommendations_body))

    contact_body = ""
    contact_body += row_html(ui["host_email"], content.get("host_email"))
    contact_body += paragraph_html(content.get("emergency_contacts"))
    contact_body += link_button_html(ui["leave_review"], content.get("airbnb_review_link"))

    instagram = safe_text(content.get("instagram_handle"))
    if instagram:
        instagram_url = f"https://instagram.com/{instagram[1:]}" if instagram.startswith("@") else f"https://instagram.com/{instagram}"
        contact_body += link_button_html(ui["instagram"], instagram_url)

    sections.append(section_html(ui["contact"], contact_body))

    return "\n".join(section for section in sections if section.strip())


def generate():
    try:
        payload = json.loads(sys.argv[1])
    except Exception:
        print("Error al leer JSON")
        return

    metadata = payload.get("metadata", {}) or {}
    property_data = payload.get("property", {}) or {}
    content = payload.get("content", {}) or {}

    styles = {
        "Coastal": {"primary": "#2C7A7B", "accent": "#F4A261", "bg": "#F0F9FF", "text": "#2D3748"},
        "Minimalist": {"primary": "#8B6F47", "accent": "#D9CEBA", "bg": "#F9F6F0", "text": "#2E2218"},
        "Classic": {"primary": "#000000", "accent": "#A0A0A0", "bg": "#FFFFFF", "text": "#1A1A1A"},
        "Sunset": {"primary": "#E76F51", "accent": "#E9C46A", "bg": "#FFF5F2", "text": "#264653"}
    }

    selected_style = safe_text(property_data.get("style")) or "Minimalist"
    style = styles.get(selected_style, styles["Minimalist"])

    villa_name = safe_text(property_data.get("property_name")) or "My Villa"
    property_address = safe_text(property_data.get("property_address"))
    primary_language = resolve_language(property_data.get("primary_language"))
    ui = UI_STRINGS[primary_language]
    slug = safe_text(metadata.get("slug")) or "demo"

    with open("templates/master.html", "r", encoding="utf-8") as f:
        html = f.read()

    language_bar_html = build_language_bar(primary_language)
    cover_image_block = build_cover_image_block(content, villa_name)
    welcome_image_block = build_welcome_image_block(content, villa_name)
    welcome_message_block = build_welcome_message_block(content, ui)
    welcome_actions_block = build_welcome_actions_block(content)
    checkin_checkout_block = build_checkin_checkout_block(content, ui)
    sections_html = build_content_sections(content, ui)

    html = html.replace("{{HTML_LANG}}", escape(ui["html_lang"]))
    html = html.replace("{{VILLA_NAME}}", escape(villa_name))
    html = html.replace("{{PROPERTY_ADDRESS}}", escape(property_address))
    html = html.replace("{{LANGUAGE_BAR}}", language_bar_html)
    html = html.replace("{{COVER_IMAGE_BLOCK}}", cover_image_block)
    html = html.replace("{{WELCOME_IMAGE_BLOCK}}", welcome_image_block)
    html = html.replace("{{WELCOME_MESSAGE_BLOCK}}", welcome_message_block)
    html = html.replace("{{WELCOME_ACTIONS_BLOCK}}", welcome_actions_block)
    html = html.replace("{{CHECKIN_CHECKOUT_BLOCK}}", checkin_checkout_block)
    html = html.replace("{{CONTENT_SECTIONS}}", sections_html)
    html = html.replace("{{COLOR_PRIMARY}}", style["primary"])
    html = html.replace("{{COLOR_ACCENT}}", style["accent"])
    html = html.replace("{{COLOR_BG}}", style["bg"])
    html = html.replace("{{COLOR_TEXT}}", style["text"])

    output_dir = os.path.join("public", "villas", slug)
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated public/villas/{slug}/index.html")


if __name__ == "__main__":
    generate()
