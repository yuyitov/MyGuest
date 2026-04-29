import sys
import json
import os
import re
from html import escape
from urllib.parse import quote_plus


SUPPORTED_LANGUAGES = ["English", "Español", "Français"]

LANGUAGE_FILE_MAP = {
    "English": "en.html",
    "Español": "es.html",
    "Français": "fr.html",
}

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
        "checkin": "Llegada",
        "checkout": "Salida",
        "pet_friendly": "Mascotas permitidas",
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
        "checkin": "Arrivée",
        "checkout": "Départ",
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

STATIC_TEMPLATE_TRANSLATIONS = {
    "English": {},
    "Español": {
        "WELCOME": "BIENVENIDO",
        "Your Guide": "Tu Guía",
        "TO": "A",
        "ENJOY YOUR STAY": "DISFRUTA TU ESTANCIA",
        "A Warm Welcome": "Una Cálida Bienvenida",
        "Everything you need for a perfect stay": "Todo lo que necesitas para una estancia perfecta",
        "Arrival": "Llegada",
        "Location": "Ubicación",
        "House Guide": "Guía de la Casa",
        "Contact Me": "Contáctame",
        "Enjoy": "Disfruta",
        "Everything at your fingertips": "Todo al alcance de tu mano",
        "Check In/Out": "Llegada / Salida",
        "Check In": "Llegada",
        "Check Out": "Salida",
        "Amenities": "Amenidades",
        "Directions": "Cómo Llegar",
        "WiFi": "WiFi",
        "Transport": "Transporte",
        "Things to Know": "Información Importante",
        "Things to Do": "Qué Hacer",
        "Places to Eat": "Dónde Comer",
        "Places to Drink": "Dónde Tomar Algo",
        "House Rules": "Reglas de la Casa",
        "Emergency": "Emergencias",
        "Local Directory": "Directorio Local",
        "Review": "Reseña",
        "Before You Leave": "Antes de Salir",
        "Contact": "Contacto",
        "Arrival Info": "Información de Llegada",
        "House Access": "Acceso a la Casa",
        "Parking": "Estacionamiento",
        "Back to Menu": "Volver al Menú",
        "Included": "Incluido",
        "Map": "Mapa",
        "Getting Around": "Cómo Moverse",
        "Good to Know": "Bueno Saber",
        "Email": "Correo",
        "Leave a Review": "Dejar una Reseña",
        "WiFi details are protected and require guest PIN access.": "Los datos de WiFi están protegidos y requieren acceso con PIN de huésped.",
        "Please use your secure guest access to view the network name and password.": "Usa tu acceso seguro de huésped para ver el nombre de la red y la contraseña.",
        "Helpful details to make your stay smoother, easier, and more comfortable from the moment you arrive.": "Detalles útiles para que tu estancia sea más fácil, cómoda y agradable desde tu llegada.",
        "If you enjoyed your stay, we’d truly appreciate your review. Your feedback helps future guests and means a lot to us.": "Si disfrutaste tu estancia, agradeceríamos mucho tu reseña. Tus comentarios ayudan a futuros huéspedes y significan mucho para nosotros.",
        "If you need special accommodations for your check-in or check-out time, please don’t hesitate to reach out to us, and we’ll do our best to make arrangements that suit your schedule.": "Si necesitas apoyo especial con tu hora de llegada o salida, contáctanos y haremos lo posible por ayudarte.",
        "This welcome book shows public guest information only.": "Este welcome book muestra únicamente información pública para huéspedes.",
    },
    "Français": {
        "WELCOME": "BIENVENUE",
        "Your Guide": "Votre Guide",
        "TO": "À",
        "ENJOY YOUR STAY": "PROFITEZ DE VOTRE SÉJOUR",
        "A Warm Welcome": "Bienvenue",
        "Everything you need for a perfect stay": "Tout ce dont vous avez besoin pour un séjour parfait",
        "Arrival": "Arrivée",
        "Location": "Emplacement",
        "House Guide": "Guide de la Maison",
        "Contact Me": "Me Contacter",
        "Enjoy": "Profitez",
        "Everything at your fingertips": "Tout à portée de main",
        "Check In/Out": "Arrivée / Départ",
        "Check In": "Arrivée",
        "Check Out": "Départ",
        "Amenities": "Équipements",
        "Directions": "Itinéraire",
        "WiFi": "WiFi",
        "Transport": "Transport",
        "Things to Know": "Informations Utiles",
        "Things to Do": "Activités",
        "Places to Eat": "Où Manger",
        "Places to Drink": "Où Boire",
        "House Rules": "Règles de la Maison",
        "Emergency": "Urgence",
        "Local Directory": "Répertoire Local",
        "Review": "Avis",
        "Before You Leave": "Avant Votre Départ",
        "Contact": "Contact",
        "Arrival Info": "Informations d’Arrivée",
        "House Access": "Accès à la Maison",
        "Parking": "Stationnement",
        "Back to Menu": "Retour au Menu",
        "Included": "Inclus",
        "Map": "Carte",
        "Getting Around": "Se Déplacer",
        "Good to Know": "Bon à Savoir",
        "Email": "Email",
        "Leave a Review": "Laisser un Avis",
        "WiFi details are protected and require guest PIN access.": "Les informations WiFi sont protégées et nécessitent un accès invité avec code PIN.",
        "Please use your secure guest access to view the network name and password.": "Veuillez utiliser votre accès invité sécurisé pour voir le nom du réseau et le mot de passe.",
        "Helpful details to make your stay smoother, easier, and more comfortable from the moment you arrive.": "Des informations utiles pour rendre votre séjour plus simple, agréable et confortable dès votre arrivée.",
        "If you enjoyed your stay, we’d truly appreciate your review. Your feedback helps future guests and means a lot to us.": "Si vous avez apprécié votre séjour, nous vous serions très reconnaissants de laisser un avis. Vos commentaires aident les futurs invités et comptent beaucoup pour nous.",
        "If you need special accommodations for your check-in or check-out time, please don’t hesitate to reach out to us, and we’ll do our best to make arrangements that suit your schedule.": "Si vous avez besoin d’un arrangement spécial pour votre arrivée ou votre départ, contactez-nous et nous ferons de notre mieux pour vous aider.",
        "This welcome book shows public guest information only.": "Ce welcome book affiche uniquement les informations publiques destinées aux invités.",
    },
}

SHARED_IMAGES = {
    "cover": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "welcome": "https://images.unsplash.com/photo-1583241800698-e8ab01830a22?auto=format&fit=crop&w=1400&q=80",
    "things_to_do": "https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=1400&q=80",
    "places_to_eat": "https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&w=1400&q=80",
    "places_to_drink": "https://images.unsplash.com/photo-1470337458703-46ad1756a187?auto=format&fit=crop&w=1400&q=80",
}

CONTENT_FIELD_MAP = {
    "checkin_time": "checkin",
    "checkout_time": "checkin",
    "house_access_public": "checkin",
    "parking_info": "checkin",

    "welcome_message": "about_house",
    "about_hosts": "about_house",
    "amenities_list": "about_house",
    "property_photos": "about_house",
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

    "restaurant_1_name": "recommendations",
    "restaurant_1_maps_link": "recommendations",
    "restaurant_2_name": "recommendations",
    "restaurant_2_maps_link": "recommendations",
    "restaurant_3_name": "recommendations",
    "restaurant_3_maps_link": "recommendations",
    "restaurant_4_name": "recommendations",
    "restaurant_4_maps_link": "recommendations",
    "restaurant_5_name": "recommendations",
    "restaurant_5_maps_link": "recommendations",

    "bar_1_name": "recommendations",
    "bar_1_maps_link": "recommendations",
    "bar_2_name": "recommendations",
    "bar_2_maps_link": "recommendations",
    "bar_3_name": "recommendations",
    "bar_3_maps_link": "recommendations",
    "bar_4_name": "recommendations",
    "bar_4_maps_link": "recommendations",
    "bar_5_name": "recommendations",
    "bar_5_maps_link": "recommendations",

    "activity_1_name": "recommendations",
    "activity_1_link": "recommendations",
    "activity_2_name": "recommendations",
    "activity_2_link": "recommendations",
    "activity_3_name": "recommendations",
    "activity_3_link": "recommendations",
    "activity_4_name": "recommendations",
    "activity_4_link": "recommendations",
    "activity_5_name": "recommendations",
    "activity_5_link": "recommendations",

    "local_directory": "recommendations",

    "host_email": "contact_social",
    "emergency_contacts": "contact_social",
    "airbnb_review_link": "contact_social",
    "instagram_handle": "contact_social",
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
    text = str(value).strip()
    return "" if text.lower() in EMPTY_TEXT_VALUES else text


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
    if not clean_url or not clean_url.startswith(("http://", "https://", "mailto:")):
        return ""
    return f'<a href="{escape(clean_url)}" class="btn" target="_blank" rel="noopener noreferrer">{escape(label)}</a>'


def resolve_language(primary_language):
    clean = safe_text(primary_language)
    return clean if clean in SUPPORTED_LANGUAGES else "English"


def build_language_bar(active_language):
    chips = []
    for lang in SUPPORTED_LANGUAGES:
        css_class = "language-chip active" if lang == active_language else "language-chip"
        href = LANGUAGE_FILE_MAP.get(lang, "index.html")
        chips.append(f'<a class="{css_class}" href="{escape(href)}">{escape(lang)}</a>')
    return "\n".join(chips)


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
    return image_block(SHARED_IMAGES["cover"], villa_name, arch=True)


def build_welcome_image_block(content_flat, villa_name):
    return image_block(SHARED_IMAGES["welcome"], villa_name, arch=False)


def build_editorial_image_block(content_flat, field_name, alt_text, photo_index, property_address=""):
    if not has_recommendation_items(content_flat, field_name, property_address):
        return ""
    image_url = SHARED_IMAGES.get(field_name, SHARED_IMAGES["welcome"])
    return image_block(image_url, alt_text, arch=False)


def build_welcome_message_block(content_flat):
    return html_multiline(content_flat.get("welcome_message"))


def build_about_hosts_block(content_flat, active_language):
    about_hosts = html_multiline(content_flat.get("about_hosts"))

    if not about_hosts:
        return ""

    labels = {
        "English": "ABOUT US",
        "Español": "SOBRE NOSOTROS",
        "Français": "À PROPOS DE NOUS",
    }

    title = labels.get(active_language, labels["English"])

    return f"""
        <div class="welcome-about">
            <div class="welcome-about-title">{escape(title)}</div>
            <p class="welcome-about-copy">{about_hosts}</p>
        </div>
    """


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


def first_non_empty(*values):
    for value in values:
        clean = safe_text(value)
        if clean:
            return clean
    return ""


def google_maps_search_url(name, property_address=""):
    query_parts = [safe_text(name), safe_text(property_address)]
    query = " ".join(part for part in query_parts if part)
    if not query:
        return ""
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}"


def build_places_from_numbered_fields(content_flat, prefix, link_suffix, property_address="", max_items=5):
    places = []

    for index in range(1, max_items + 1):
        name = safe_text(content_flat.get(f"{prefix}_{index}_name"))
        link = safe_text(content_flat.get(f"{prefix}_{index}_{link_suffix}"))
        phone = first_non_empty(
            content_flat.get(f"{prefix}_{index}_phone"),
            content_flat.get(f"{prefix}_{index}_phone_number"),
        )
        image = first_non_empty(
            content_flat.get(f"{prefix}_{index}_image"),
            content_flat.get(f"{prefix}_{index}_photo"),
        )
        rating = safe_text(content_flat.get(f"{prefix}_{index}_rating"))
        category = safe_text(content_flat.get(f"{prefix}_{index}_category"))
        address = safe_text(content_flat.get(f"{prefix}_{index}_address"))

        if not name:
            continue

        if not link:
            link = google_maps_search_url(name, property_address)

        places.append({
            "name": name,
            "link": link,
            "phone": phone,
            "image": image,
            "rating": rating,
            "category": category,
            "address": address,
        })

    return places


def legacy_text_to_single_place(value, fallback_name, property_address=""):
    text = normalize_text_block(value)
    if not text:
        return []

    return [{
        "name": fallback_name,
        "link": google_maps_search_url(fallback_name, property_address),
        "phone": "",
        "image": "",
        "rating": "",
        "category": "",
        "address": "",
        "description": text,
    }]


def get_restaurant_places(content_flat, property_address=""):
    places = build_places_from_numbered_fields(content_flat, "restaurant", "maps_link", property_address)
    if places:
        return places
    return legacy_text_to_single_place(content_flat.get("places_to_eat"), "Restaurants", property_address)


def get_bar_places(content_flat, property_address=""):
    places = build_places_from_numbered_fields(content_flat, "bar", "maps_link", property_address)
    if places:
        return places
    return legacy_text_to_single_place(content_flat.get("places_to_drink"), "Bars & Drinks", property_address)


def get_activity_places(content_flat, property_address=""):
    places = build_places_from_numbered_fields(content_flat, "activity", "link", property_address)
    if places:
        return places
    return legacy_text_to_single_place(content_flat.get("things_to_do"), "Things to Do", property_address)


def recommendation_action_link(kind, label, url):
    clean_url = safe_text(url)
    if not clean_url:
        return ""

    if kind == "phone":
        href = clean_url if clean_url.startswith("tel:") else f"tel:{clean_url}"
    else:
        href = clean_url

    if not href.startswith(("http://", "https://", "tel:", "mailto:")):
        return ""

    if kind == "phone":
        svg = '<svg viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2A19.8 19.8 0 0 1 3 5.18 2 2 0 0 1 5 3h3a2 2 0 0 1 2 1.72c.12.9.33 1.77.62 2.6a2 2 0 0 1-.45 2.11L9 10.6a16 16 0 0 0 4.4 4.4l1.17-1.17a2 2 0 0 1 2.11-.45c.83.29 1.7.5 2.6.62A2 2 0 0 1 22 16.92Z"></path></svg>'
    else:
        svg = '<svg viewBox="0 0 24 24"><path d="M12 21s-6-4.35-6-10a6 6 0 1 1 12 0c0 5.65-6 10-6 10Z"></path><circle cx="12" cy="11" r="2.5"></circle></svg>'

    return f'''
        <a class="recommendation-action-pill" href="{escape(href)}" target="_blank" rel="noopener noreferrer">
            {svg}
            {escape(label)}
        </a>
    '''


def build_recommendation_cards(places, default_image_url, default_meta, primary_action_label="Google Maps"):
    if not places:
        return ""

    cards = []
    for place in places:
        name = safe_text(place.get("name"))
        if not name:
            continue

        image_url = safe_text(place.get("image")) or default_image_url
        rating = safe_text(place.get("rating"))
        rating_display = escape(rating) if rating else "★★★★★"
        category = safe_text(place.get("category"))
        address = safe_text(place.get("address"))
        meta_parts = [part for part in [category, address] if part]
        meta = " · ".join(meta_parts) if meta_parts else default_meta
        description = safe_text(place.get("description"))

        copy_parts = []
        if description:
            copy_parts.append(escape(description).replace("\n", "<br>"))
        if address and not description:
            copy_parts.append(escape(address))

        copy_html = "<br>".join(copy_parts)
        if copy_html:
            copy_html = f'<div class="recommendation-listing-copy">{copy_html}</div>'

        actions = recommendation_action_link("maps", primary_action_label, place.get("link"))
        actions += recommendation_action_link("phone", "Call", place.get("phone"))

        cards.append(f'''
            <article class="recommendation-listing-card">
                <div class="recommendation-listing-image">
                    {image_block(image_url, name, arch=False)}
                </div>
                <div class="recommendation-listing-body">
                    <div class="recommendation-listing-topline">
                        <h3 class="recommendation-listing-name">{escape(name)}</h3>
                        <span class="recommendation-rating">{rating_display}</span>
                    </div>
                    <div class="recommendation-meta">{escape(meta)}</div>
                    {copy_html}
                    <div class="recommendation-action-row" aria-label="Recommendation actions">
                        {actions}
                    </div>
                </div>
            </article>
        ''')

    return "\n".join(cards)


def build_places_to_eat_html(content_flat, property_address=""):
    places = get_restaurant_places(content_flat, property_address)
    return build_recommendation_cards(
        places,
        SHARED_IMAGES["places_to_eat"],
        "Restaurants · Nearby recommendations",
        "Google Maps",
    )


def build_places_to_drink_html(content_flat, property_address=""):
    places = get_bar_places(content_flat, property_address)
    return build_recommendation_cards(
        places,
        SHARED_IMAGES["places_to_drink"],
        "Bars · Cocktails · Local spots",
        "Google Maps",
    )


def build_things_to_do_html(content_flat, property_address=""):
    places = get_activity_places(content_flat, property_address)
    return build_recommendation_cards(
        places,
        SHARED_IMAGES["things_to_do"],
        "Activities · Tours · Local experiences",
        "Open link",
    )


def has_recommendation_items(content_flat, field_name, property_address=""):
    if field_name == "places_to_eat":
        return bool(get_restaurant_places(content_flat, property_address))
    if field_name == "places_to_drink":
        return bool(get_bar_places(content_flat, property_address))
    if field_name == "things_to_do":
        return bool(get_activity_places(content_flat, property_address))
    return has_value(content_flat.get(field_name))


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


def apply_static_template_translations(html, active_language):
    translations = STATIC_TEMPLATE_TRANSLATIONS.get(active_language, {})
    if not translations:
        return html

    parts = re.split(r"(\{\{[A-Z0-9_]+\}\})", html)
    translated_parts = []
    for part in parts:
        if part.startswith("{{") and part.endswith("}}"):
            translated_parts.append(part)
            continue
        for source_text, translated_text in translations.items():
            part = part.replace(source_text, translated_text)
        translated_parts.append(part)
    return "".join(translated_parts)


def replace_placeholder(html, placeholder, value):
    return html.replace(placeholder, value if value is not None else "")


def inject_public_qa_overrides(html):
    # Desactivado en Bloque 12 para que Pantalla 1 y Pantalla 2 usen
    # únicamente el diseño aprobado en templates/master.html.
    return html


def render_html_for_language(payload, active_language, output_filename):
    metadata = payload.get("metadata", {}) or {}
    property_data = payload.get("property", {}) or {}
    content = payload.get("content", {}) or {}
    content_flat = flatten_content(content)

    styles = {
        "Coastal": {"primary": "#2C7A7B", "accent": "#F4A261", "bg": "#F0F9FF", "text": "#1F3A3A"},
        "Minimalist": {"primary": "#8B6F47", "accent": "#D9CEBA", "bg": "#F9F6F0", "text": "#3A2A1C"},
        "Classic": {"primary": "#000000", "accent": "#A0A0A0", "bg": "#FFFFFF", "text": "#1A1A1A"},
        "Sunset": {"primary": "#E76F51", "accent": "#E9C46A", "bg": "#FFF5F2", "text": "#264653"},
    }

    selected_style = safe_text(property_data.get("style")) or "Minimalist"
    style = styles.get(selected_style, styles["Minimalist"])

    villa_name = safe_text(property_data.get("property_name")) or "My Villa"
    property_address = safe_text(property_data.get("property_address"))
    ui = UI_STRINGS[active_language]
    slug = safe_text(metadata.get("slug")) or "demo"
    guest_access_url = safe_text(metadata.get("guest_access_url")) or safe_text(payload.get("guest_access_url"))
    with open("templates/master.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = apply_static_template_translations(html, active_language)

    replacements = {
        "{{HTML_LANG}}": escape(ui["html_lang"]),
        "{{VILLA_NAME}}": escape(villa_name),
        "{{PROPERTY_ADDRESS}}": escape(property_address),
        "{{LANGUAGE_BAR}}": build_language_bar(active_language),
        "{{COVER_IMAGE_BLOCK}}": build_cover_image_block(content_flat, villa_name),
        "{{WELCOME_IMAGE_BLOCK}}": build_welcome_image_block(content_flat, villa_name),
        "{{WELCOME_MESSAGE_BLOCK}}": build_welcome_message_block(content_flat),
        "{{ABOUT_HOSTS_BLOCK}}": build_about_hosts_block(content_flat, active_language),
        "{{WELCOME_ACTIONS_BLOCK}}": build_welcome_actions_block(content_flat),
        "{{CHECKIN_CHECKOUT_BLOCK}}": build_checkin_checkout_block(content_flat, ui),
        "{{CONTENT_SECTIONS}}": build_content_sections(content_flat, ui),
        "{{GENERATED_PRIVATE_URL}}": escape(guest_access_url),
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
        "{{THINGS_TO_DO}}": build_things_to_do_html(content_flat, property_address),
        "{{PLACES_TO_EAT}}": build_places_to_eat_html(content_flat, property_address),
        "{{PLACES_TO_DRINK}}": build_places_to_drink_html(content_flat, property_address),
        "{{THINGS_TO_DO_IMAGE_BLOCK}}": build_editorial_image_block(content_flat, "things_to_do", "Things to Do", 1, property_address),
        "{{PLACES_TO_EAT_IMAGE_BLOCK}}": build_editorial_image_block(content_flat, "places_to_eat", "Places to Eat", 2, property_address),
        "{{PLACES_TO_DRINK_IMAGE_BLOCK}}": build_editorial_image_block(content_flat, "places_to_drink", "Places to Drink", 3, property_address),
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

    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated public/villas/{slug}/{output_filename}")


def generate():
    try:
        payload = json.loads(sys.argv[1])
    except Exception:
        print("Error al leer JSON")
        return

    property_data = payload.get("property", {}) or {}
    primary_language = resolve_language(property_data.get("primary_language"))
    primary_filename = LANGUAGE_FILE_MAP.get(primary_language, "en.html")

    for language, filename in LANGUAGE_FILE_MAP.items():
        render_html_for_language(payload, language, filename)

    metadata = payload.get("metadata", {}) or {}
    slug = safe_text(metadata.get("slug")) or "demo"
    output_dir = os.path.join("public", "villas", slug)

    primary_path = os.path.join(output_dir, primary_filename)
    index_path = os.path.join(output_dir, "index.html")

    with open(primary_path, "r", encoding="utf-8") as source:
        index_html = source.read()

    with open(index_path, "w", encoding="utf-8") as target:
        target.write(index_html)

    print(f"Generated public/villas/{slug}/index.html from {primary_filename}")


if __name__ == "__main__":
    generate()
