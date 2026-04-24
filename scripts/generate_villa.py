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
        "html_lang": "fr",
    },
}


FALLBACK_COVER_IMAGE = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80"
FALLBACK_WELCOME_IMAGE = "https://images.unsplash.com/photo-1583241800698-e8ab01830a22?auto=format&fit=crop&w=1400&q=80"

CONTENT_FIELD_MAP = {
    "checkin_time": "checkin",
    "checkout_time": "checkin",
    "house_access_public": "checkin",
    "parking_info": "checkin",

    "about_hosts": "about_house",
    "amenities_list": "about_house",
    "pet_friendly": "about_house",
    "pet_rules": "about_house",

    "google_maps_link": "location_transport",
    "directions_text": "location_transport",
    "transport_options": "location_transport",

    "house_rules": "rules_info",
    "things_to_know": "rules_info",
    "before_you_leave": "rules_info",

    "places_to_eat": "recommendations",
    "places_to_drink": "recommendations",
    "things_to_do": "recommendations",
    "local_directory": "recommendations",

    "host_email": "contact_social",
    "emergency_contacts": "contact_social",
    "airbnb_review_link": "contact_social",
    "instagram_handle": "contact_social",
}


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


def normalize_text_block(value):
    if value is None:
        return ""
    if isinstance(value, list):
        parts = [safe_text(item) for item in value if has_value(item)]
        return "\n".join(parts).strip()
    if isinstance(value, dict):
        parts = []
        for item in value.values():
            if has_value(item):
                parts.append(safe_text(item))
        return "\n".join(parts).strip()
    return safe_text(value)


def html_multiline(value):
    text = normalize_text_block(value)
    if not text:
        return ""
    return escape(text).replace("\n", "<br>")


def paragraph_html(value):
    block = html_multiline(value)
    if not block:
        return ""
    return f'<p class="paragraph">{block}</p>'


def row_html(label, value):
    block = html_multiline(value)
    if not block:
        return ""
    return f"""
        <div class="info-row">
            <div class="info-label">{escape(label)}</div>
            <div class="info-value">{block}</div>
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


def is_public_image_url(url):
    clean = safe_text(url)
    if not clean:
        return False
    return clean.startswith("http://") or clean.startswith("https://")


def public_photos(content_flat):
    photos = normalize_photo_list(content_flat.get("property_photos"))
    return [photo for photo in photos if is_public_image_url(photo)]


def first_public_photo(content_flat):
    photos = public_photos(content_flat)
    return photos[0] if photos else ""


def nth_public_photo(content_flat, index=0):
    photos = public_photos(content_flat)
    if index < len(photos):
        return photos[index]
    return photos[0] if photos else ""


def image_block(url, alt_text, arch=False):
    clean_url = safe_text(url)
    if not clean_url:
        return ""
    if arch:
        return f'''
            <div class="cover-image-arch">
                <img src="{escape(clean_url)}" alt="{escape(alt_text)}">
            </div>
        '''
    return f'<img src="{escape(clean_url)}" alt="{escape(alt_text)}">'


def flatten_content(content):
    if not isinstance(content, dict):
        return {}

    flat = {}

    for key, value in content.items():
        if key not in CONTENT_FIELD_MAP and not isinstance(value, dict):
            flat[key] = value

    for field_name, block_name in CONTENT_FIELD_MAP.items():
        block = content.get(block_name, {})
        if isinstance(block, dict) and field_name in block:
            flat[field_name] = block.get(field_name)
        elif field_name in content:
            flat[field_name] = content.get(field_name)

    return flat


def build_cover_image_block(content_flat, villa_name):
    photo = first_public_photo(content_flat)
    if photo:
        return image_block(photo, villa_name, arch=True)
    return image_block(FALLBACK_COVER_IMAGE, villa_name, arch=True)


def build_welcome_image_block(content_flat, villa_name):
    photo = first_public_photo(content_flat)
    if photo:
        return image_block(photo, villa_name, arch=False)
    return image_block(FALLBACK_WELCOME_IMAGE, villa_name, arch=False)


def build_editorial_image_block(content_flat, field_name, alt_text, photo_index):
    photo = nth_public_photo(content_flat, photo_index)
    if photo:
        return image_block(photo, alt_text, arch=False)

    field_text = normalize_text_block(content_flat.get(field_name))
    if field_text:
        return f'<div style="width:100%;height:220px;display:flex;align-items:center;justify-content:center;padding:24px;text-align:center;color:#8b6f47;font-family:\'Cormorant Garamond\',serif;font-size:30px;line-height:1.1;">{escape(alt_text)}</div>'

    return ""


def build_welcome_message_block(content_flat):
    return html_multiline(content_flat.get("welcome_message"))


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


def build_welcome_actions_block(content_flat):
    actions = []

    maps_url = safe_text(content_flat.get("google_maps_link"))
    if maps_url:
        actions.append(f'''
            <a class="welcome-action" href="{escape(maps_url)}" target="_blank" rel="noopener noreferrer" aria-label="Google Maps">
                {icon_button_svg("maps")}
            </a>
        ''')

    host_email = safe_text(content_flat.get("host_email"))
    if host_email:
        actions.append(f'''
            <a class="welcome-action" href="mailto:{escape(host_email)}" aria-label="Email">
                {icon_button_svg("email")}
            </a>
        ''')

    return "\n".join(actions)


def build_checkin_checkout_block(content_flat, ui):
    cards = []

    checkin_time = safe_text(content_flat.get("checkin_time"))
    if checkin_time:
        cards.append(f"""
            <div class="arrival-card">
                <div class="arrival-label">{escape(ui["checkin"])}</div>
                <div class="arrival-time">{escape(checkin_time)}</div>
            </div>
        """)

    checkout_time = safe_text(content_flat.get("checkout_time"))
    if checkout_time:
        cards.append(f"""
            <div class="arrival-card">
                <div class="arrival-label">{escape(ui["checkout"])}</div>
                <div class="arrival-time">{escape(checkout_time)}</div>
            </div>
        """)

    return "\n".join(cards)


def build_content_sections(content_flat, ui):
    sections = []

    arrival_body = ""
    arrival_body += paragraph_html(content_flat.get("house_access_public"))
    arrival_body += paragraph_html(content_flat.get("parking_info"))
    sections.append(section_html(ui["arrival"], arrival_body))

    about_body = ""
    about_body += paragraph_html(content_flat.get("about_hosts"))
    about_body += paragraph_html(content_flat.get("amenities_list"))
    pet_value = safe_bool(content_flat.get("pet_friendly"))
    if pet_value is True:
        about_body += row_html(ui["pet_friendly"], ui["yes"])
    elif pet_value is False:
        about_body += row_html(ui["pet_friendly"], ui["no"])
    about_body += paragraph_html(content_flat.get("pet_rules"))
    sections.append(section_html(ui["about_stay"], about_body))

    location_body = ""
    location_body += paragraph_html(content_flat.get("directions_text"))
    location_body += paragraph_html(content_flat.get("transport_options"))
    location_body += link_button_html(ui["open_maps"], content_flat.get("google_maps_link"))
    sections.append(section_html(ui["location_transport"], location_body))

    rules_body = ""
    rules_body += paragraph_html(content_flat.get("house_rules"))
    rules_body += paragraph_html(content_flat.get("things_to_know"))
    rules_body += paragraph_html(content_flat.get("before_you_leave"))
    sections.append(section_html(ui["house_info"], rules_body))

    recommendations_body = ""
    recommendations_body += paragraph_html(content_flat.get("places_to_eat"))
    recommendations_body += paragraph_html(content_flat.get("places_to_drink"))
    recommendations_body += paragraph_html(content_flat.get("things_to_do"))
    recommendations_body += paragraph_html(content_flat.get("local_directory"))
    sections.append(section_html(ui["recommendations"], recommendations_body))

    contact_body = ""
    contact_body += row_html(ui["host_email"], content_flat.get("host_email"))
    contact_body += paragraph_html(content_flat.get("emergency_contacts"))
    contact_body += link_button_html(ui["leave_review"], content_flat.get("airbnb_review_link"))

    instagram = safe_text(content_flat.get("instagram_handle"))
    if instagram:
        instagram_url = f"https://instagram.com/{instagram[1:]}" if instagram.startswith("@") else f"https://instagram.com/{instagram}"
        contact_body += link_button_html(ui["instagram"], instagram_url)

    sections.append(section_html(ui["contact"], contact_body))

    return "\n".join(section for section in sections if section.strip())


def build_directions_map_block(content_flat, ui):
    maps_url = safe_text(content_flat.get("google_maps_link"))
    if not maps_url:
        return ""

    return f'''
        <a href="{escape(maps_url)}" target="_blank" rel="noopener noreferrer"
           style="display:flex;align-items:center;justify-content:center;width:100%;height:210px;padding:24px;text-align:center;text-decoration:none;color:#6e5230;font-family:'Cormorant Garamond',serif;font-size:30px;line-height:1.1;background:#fbf7f2;">
            {escape(ui["open_maps"])}
        </a>
    '''


def replace_placeholder(html, placeholder, value):
    return html.replace(placeholder, value if value is not None else "")


def generate():
    try:
        payload = json.loads(sys.argv[1])
    except Exception:
        print("Error al leer JSON")
        return

    metadata = payload.get("metadata", {}) or {}
    property_data = payload.get("property", {}) or {}
    content = payload.get("content", {}) or {}
    content_flat = flatten_content(content)

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
    cover_image_block = build_cover_image_block(content_flat, villa_name)
    welcome_image_block = build_welcome_image_block(content_flat, villa_name)
    welcome_message_block = build_welcome_message_block(content_flat)
    welcome_actions_block = build_welcome_actions_block(content_flat)
    checkin_checkout_block = build_checkin_checkout_block(content_flat, ui)
    sections_html = build_content_sections(content_flat, ui)

    replacements = {
        "{{HTML_LANG}}": escape(ui["html_lang"]),
        "{{VILLA_NAME}}": escape(villa_name),
        "{{PROPERTY_ADDRESS}}": escape(property_address),
        "{{LANGUAGE_BAR}}": language_bar_html,
        "{{COVER_IMAGE_BLOCK}}": cover_image_block,
        "{{WELCOME_IMAGE_BLOCK}}": welcome_image_block,
        "{{WELCOME_MESSAGE_BLOCK}}": welcome_message_block,
        "{{WELCOME_ACTIONS_BLOCK}}": welcome_actions_block,
        "{{CHECKIN_CHECKOUT_BLOCK}}": checkin_checkout_block,
        "{{CONTENT_SECTIONS}}": sections_html,
        "{{COLOR_PRIMARY}}": style["primary"],
        "{{COLOR_ACCENT}}": style["accent"],
        "{{COLOR_BG}}": style["bg"],
        "{{COLOR_TEXT}}": style["text"],

        "{{CHECKIN_TIME_DISPLAY}}": escape(safe_text(content_flat.get("checkin_time"))),
        "{{CHECKOUT_TIME_DISPLAY}}": escape(safe_text(content_flat.get("checkout_time"))),
        "{{HOUSE_ACCESS_PUBLIC}}": html_multiline(content_flat.get("house_access_public")),
        "{{PARKING_INFO}}": html_multiline(content_flat.get("parking_info")),

        "{{AMENITIES_LIST}}": html_multiline(content_flat.get("amenities_list")),
        "{{DIRECTIONS_MAP_BLOCK}}": build_directions_map_block(content_flat, ui),
        "{{GOOGLE_MAPS_LINK}}": html_multiline(content_flat.get("google_maps_link")),
        "{{DIRECTIONS_TEXT}}": html_multiline(content_flat.get("directions_text")),
        "{{TRANSPORT_OPTIONS}}": html_multiline(content_flat.get("transport_options")),

        "{{THINGS_TO_KNOW}}": html_multiline(content_flat.get("things_to_know")),
        "{{THINGS_TO_DO}}": html_multiline(content_flat.get("things_to_do")),
        "{{PLACES_TO_EAT}}": html_multiline(content_flat.get("places_to_eat")),
        "{{PLACES_TO_DRINK}}": html_multiline(content_flat.get("places_to_drink")),

        "{{THINGS_TO_DO_IMAGE_BLOCK}}": build_editorial_image_block(content_flat, "things_to_do", "Things to Do", 1),
        "{{PLACES_TO_EAT_IMAGE_BLOCK}}": build_editorial_image_block(content_flat, "places_to_eat", "Places to Eat", 2),
        "{{PLACES_TO_DRINK_IMAGE_BLOCK}}": build_editorial_image_block(content_flat, "places_to_drink", "Places to Drink", 3),

        "{{HOUSE_RULES}}": html_multiline(content_flat.get("house_rules")),
        "{{EMERGENCY_CONTACTS}}": html_multiline(content_flat.get("emergency_contacts")),
        "{{LOCAL_DIRECTORY}}": html_multiline(content_flat.get("local_directory")),
        "{{AIRBNB_REVIEW_LINK}}": escape(safe_text(content_flat.get("airbnb_review_link"))),
        "{{BEFORE_YOU_LEAVE}}": html_multiline(content_flat.get("before_you_leave")),
        "{{HOST_EMAIL}}": html_multiline(content_flat.get("host_email")),
        "{{INSTAGRAM_HANDLE}}": html_multiline(content_flat.get("instagram_handle")),
    }

    for placeholder, value in replacements.items():
        html = replace_placeholder(html, placeholder, value)

    output_dir = os.path.join("public", "villas", slug)
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated public/villas/{slug}/index.html")


if __name__ == "__main__":
    generate()
