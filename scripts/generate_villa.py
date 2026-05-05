import sys
import json
import os
import re
import socket
import time
from html import escape
from urllib.parse import quote_plus
import urllib.request
import urllib.error

SUPPORTED_LANGUAGES = ["English", "Español", "Français"]

LANGUAGE_FILE_MAP = {
    "English": "en.html",
    "Español": "es.html",
    "Français": "fr.html",
}

UI_STRINGS = {
    "English": {
        "html_lang": "en",
        "yes": "Yes",
        "no": "No",
        "open_maps": "Open Google Maps",
        "google_maps": "Google Maps",
        "open_link": "Open link",
        "call": "Call",
        "about_us": "ABOUT US",
        "pet_friendly": "Pet friendly",
        "leave_review": "Leave a Review",
        "restaurants_meta": "Restaurants · Nearby recommendations",
        "bars_meta": "Bars · Cocktails · Local spots",
        "activities_meta": "Activities · Tours · Local experiences",
    },
    "Español": {
        "html_lang": "es",
        "yes": "Sí",
        "no": "No",
        "open_maps": "Abrir Google Maps",
        "google_maps": "Google Maps",
        "open_link": "Abrir enlace",
        "call": "Llamar",
        "about_us": "SOBRE NOSOTROS",
        "pet_friendly": "Mascotas permitidas",
        "leave_review": "Dejar una reseña",
        "restaurants_meta": "Restaurantes · Recomendaciones cercanas",
        "bars_meta": "Bares · Cocteles · Lugares locales",
        "activities_meta": "Actividades · Tours · Experiencias locales",
    },
    "Français": {
        "html_lang": "fr",
        "yes": "Oui",
        "no": "Non",
        "open_maps": "Ouvrir Google Maps",
        "google_maps": "Google Maps",
        "open_link": "Ouvrir le lien",
        "call": "Appeler",
        "about_us": "À PROPOS DE NOUS",
        "pet_friendly": "Animaux acceptés",
        "leave_review": "Laisser un avis",
        "restaurants_meta": "Restaurants · Recommandations à proximité",
        "bars_meta": "Bars · Cocktails · Adresses locales",
        "activities_meta": "Activités · Tours · Expériences locales",
    },
}

STATIC_TEMPLATE_TRANSLATIONS = {
    "English": {},
    "Español": {
        "WELCOME": "BIENVENIDO",
        "Your Guide": "Tu Guía",
        "TO": "A",
        "A Warm Welcome": "Una Cálida Bienvenida",
        "Everything you need for a perfect stay": "Todo lo que necesitas para una estancia perfecta",
        "Getting There": "Cómo Llegar",
        "Check-in & Check-out": "Llegada y Salida",
        "Check-in/out": "Llegada/Salida",
        "Check-in &": "Llegada y",
        "Check-out": "Salida",
        "Check In": "Llegada",
        "Check Out": "Salida",
        "Access & Parking": "Acceso y Estacionamiento",
        "WiFi": "WiFi",
        "The House": "La Casa",
        "House Rules": "Reglas de la Casa",
        "Things to Know": "Información Importante",
        "Restaurants": "Restaurantes",
        "Bars & Drinks": "Bares y Bebidas",
        "Things to Do": "Qué Hacer",
        "Contact": "Contacto",
        "Emergency": "Emergencia",
        "Back to Menu": "Volver al Menú",
        "Map": "Mapa",
        "Directions": "Indicaciones",
        "Transport": "Transporte",
        "Access": "Acceso",
        "Parking": "Estacionamiento",
        "Amenities": "Amenidades",
        "Rules": "Reglas",
        "Pets": "Mascotas",
        "Good to Know": "Bueno Saber",
        "Before You Leave": "Antes de Salir",
        "Email": "Correo",
        "Instagram": "Instagram",
        "Review": "Reseña",
        "Leave a Review": "Dejar una Reseña",
        "Emergency Contacts": "Contactos de Emergencia",
        "WiFi details are protected and appear only with your secure guest access link.": "Los datos de WiFi están protegidos y solo aparecen con tu enlace seguro de huésped.",
        "Some stay details are protected and only appear with a valid guest access link.": "Algunos detalles de la estancia están protegidos y solo aparecen con un enlace válido de huésped.",
        "Recommendation actions": "Acciones de recomendación",
        "WiFi network": "Red WiFi",
        "WiFi password": "Contraseña WiFi",
        "Door code": "Código de puerta",
        "Access notes": "Notas de acceso",
        "Host phone": "Teléfono del anfitrión",
        "Bars & Drinks": "Bares y Bebidas",
        "Activities": "Actividades",
        "Nearby recommendations": "Recomendaciones cercanas",
        "Local spots": "Lugares locales",
        "Local experiences": "Experiencias locales",
        "Open link": "Abrir enlace",
        "Call": "Llamar",
      },
    
    "Français": {
        "WELCOME": "BIENVENUE",
        "Your Guide": "Votre Guide",
        "TO": "À",
        "A Warm Welcome": "Bienvenue",
        "Everything you need for a perfect stay": "Tout ce dont vous avez besoin pour un séjour parfait",
        "Getting There": "Comment s’y rendre",
        "Check-in & Check-out": "Arrivée et Départ",
        "Check-in/out": "Arrivée/Départ",
        "Check-in &": "Arrivée et",
        "Check-out": "Départ",
        "Check In": "Arrivée",
        "Check Out": "Départ",
        "Access & Parking": "Accès et Stationnement",
        "WiFi": "WiFi",
        "The House": "La Maison",
        "House Rules": "Règles de la Maison",
        "Things to Know": "À savoir",
        "Restaurants": "Restaurants",
        "Bars & Drinks": "Bars et Boissons",
        "Things to Do": "À faire",
        "Contact": "Contact",
        "Emergency": "Urgence",
        "Back to Menu": "Retour au Menu",
        "Map": "Carte",
        "Directions": "Itinéraire",
        "Transport": "Transport",
        "Access": "Accès",
        "Parking": "Stationnement",
        "Amenities": "Équipements",
        "Rules": "Règles",
        "Pets": "Animaux",
        "Good to Know": "Bon à Savoir",
        "Before You Leave": "Avant Votre Départ",
        "Email": "Email",
        "Instagram": "Instagram",
        "Review": "Avis",
        "Leave a Review": "Laisser un Avis",
        "Emergency Contacts": "Contacts d’Urgence",
        "WiFi details are protected and appear only with your secure guest access link.": "Les informations WiFi sont protégées et apparaissent uniquement avec votre lien invité sécurisé.",
        "Some stay details are protected and only appear with a valid guest access link.": "Certains détails du séjour sont protégés et apparaissent uniquement avec un lien invité valide.",
        "Recommendation actions": "Actions de recommandation",
        "WiFi network": "Réseau WiFi",
        "WiFi password": "Mot de passe WiFi",
        "Door code": "Code de porte",
        "Access notes": "Notes d’accès",
        "Host phone": "Téléphone de l’hôte",
        "Bars & Drinks": "Bars et Boissons",
        "Activities": "Activités",
        "Nearby recommendations": "Recommandations à proximité",
        "Local spots": "Adresses locales",
        "Local experiences": "Expériences locales",
        "Open link": "Ouvrir le lien",
        "Call": "Appeler",
    },
}

SHARED_IMAGES = {
    "cover": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "welcome": "https://images.unsplash.com/photo-1583241800698-e8ab01830a22?auto=format&fit=crop&w=1400&q=80",
    "things_to_do": "https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=1400&q=80",
    "places_to_eat": "https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&w=1400&q=80",
    "places_to_drink": "https://images.unsplash.com/photo-1470337458703-46ad1756a187?auto=format&fit=crop&w=1400&q=80",
}

COVER_IMAGES_BY_ENVIRONMENT = {
    "Beach": SHARED_IMAGES["cover"],
    "City": "../../assets/covers/city.png",
    "Cozy": "../../assets/covers/cozy.png",
}

ENVIRONMENT_ALIASES = {
    "beach": "Beach",
    "playa": "Beach",
    "coastal": "Beach",
    "city": "City",
    "ciudad": "City",
    "urban": "City",
    "urbano": "City",
    "cozy": "Cozy",
    "cosy": "Cozy",
    "homey": "Cozy",
    "countryside": "Cozy",
    "country": "Cozy",
}

# 5 imágenes genéricas por categoría para evitar que todas las recomendaciones
# se vean repetidas. Si en el futuro Tally manda restaurant_1_image/photo,
# bar_1_image/photo o activity_1_image/photo, esa imagen específica tiene prioridad.
RECOMMENDATION_IMAGE_POOLS = {
    "places_to_eat": [
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1400&q=80",
    ],
    "places_to_drink": [
        "https://images.unsplash.com/photo-1470337458703-46ad1756a187?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1572116469696-31de0f17cc34?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1527761939622-933c3c17d155?auto=format&fit=crop&w=1400&q=80",
    ],
    "things_to_do": [
        "https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1526772662000-3f88f10405ff?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1400&q=80",
    ],
}

CONTENT_FIELD_MAP = {
    "checkin_time": "checkin",
    "checkout_time": "checkin",
    "house_access_public": "checkin",
    "parking_info": "checkin",
    "welcome_message": "about_house",
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
    "property_environment": "recommendations",
    "host_email": "contact_social",
    "emergency_contacts": "contact_social",
    "airbnb_review_link": "contact_social",
    "instagram_handle": "contact_social",
}

for i in range(1, 6):
    for field in [
        "name",
        "maps_link",
        "phone",
        "phone_number",
        "image",
        "photo",
        "rating",
        "category",
        "address",
        "description",
        "notes",
    ]:
        CONTENT_FIELD_MAP[f"restaurant_{i}_{field}"] = "recommendations"
        CONTENT_FIELD_MAP[f"bar_{i}_{field}"] = "recommendations"

    for field in [
        "name",
        "link",
        "phone",
        "phone_number",
        "image",
        "photo",
        "rating",
        "category",
        "address",
        "description",
        "notes",
    ]:
        CONTENT_FIELD_MAP[f"activity_{i}_{field}"] = "recommendations"

EMPTY_TEXT_VALUES = {"", "-", "n/a", "na", "none", "null", "undefined"}
OPENAI_TRANSLATION_MODEL = (
    os.getenv("OPENAI_MODEL_TRANSLATION")
    or os.getenv("OPENAI_TRANSLATION_MODEL")
    or "gpt-5-nano"
).strip()

OPENAI_TRANSLATION_REQUIRED = (
    os.getenv("OPENAI_TRANSLATION_REQUIRED", "true").strip().lower()
    not in {"0", "false", "no"}
)

TRANSLATABLE_PUBLIC_FIELDS = [
    "welcome_message",
    "about_hosts",
    "directions_text",
    "transport_options",
    "house_access_public",
    "parking_info",
    "amenities_list",
    "house_rules",
    "pet_rules",
    "things_to_know",
    "before_you_leave",
    "emergency_contacts",
    "places_to_eat",
    "places_to_drink",
    "things_to_do",
    "local_directory",
]

for i in range(1, 6):
    TRANSLATABLE_PUBLIC_FIELDS.extend([
        f"restaurant_{i}_category",
        f"bar_{i}_category",
        f"activity_{i}_category",
        f"restaurant_{i}_description",
        f"bar_{i}_description",
        f"activity_{i}_description",
        f"restaurant_{i}_notes",
        f"bar_{i}_notes",
        f"activity_{i}_notes",
    ])

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
    if text in {"yes", "true", "sí", "si", "1", "y", "oui"}:
        return True
    if text in {"no", "false", "0", "n", "non"}:
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


def looks_like_non_translatable_value(text):
    clean = safe_text(text)
    if not clean:
        return True

    lower = clean.lower()

    if lower.startswith(("http://", "https://", "mailto:", "tel:")):
        return True

    if "@" in clean and "." in clean and " " not in clean:
        return True

    if re.fullmatch(r"[\+\d\s\-\(\)]{7,}", clean):
        return True

    if re.fullmatch(r"\d{1,2}:\d{2}\s*(am|pm|AM|PM)?", clean):
        return True

    return False


def extract_openai_response_text(response_json):
    if not isinstance(response_json, dict):
        return ""

    direct_text = response_json.get("output_text")
    if isinstance(direct_text, str) and direct_text.strip():
        return direct_text.strip()

    chunks = []

    def walk(value):
        if isinstance(value, dict):
            text = value.get("text")
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())

            for child in value.values():
                walk(child)

        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(response_json.get("output", []))

    return "\n".join(chunks).strip()


def clean_json_response_text(text):
    clean = safe_text(text)

    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\s*```$", "", clean).strip()

    return clean


def parse_translation_json(text):
    clean = clean_json_response_text(text)

    try:
        parsed = json.loads(clean)
    except Exception:
        start = clean.find("{")
        end = clean.rfind("}")

        if start >= 0 and end > start:
            candidate = clean[start:end + 1]
            parsed = json.loads(candidate)
        else:
            raise ValueError("Could not parse translation JSON.")

    if not isinstance(parsed, dict):
        raise ValueError("Could not parse translation JSON into an object.")

    fields = parsed.get("fields")
    if isinstance(fields, dict):
        return fields

    return parsed


def split_translation_batches(fields_to_translate, max_chars=900):
    batches = []
    current = {}
    current_size = 0

    for key, value in fields_to_translate.items():
        text = safe_text(value)
        item_size = len(key) + len(text)

        if current and current_size + item_size > max_chars:
            batches.append(current)
            current = {}
            current_size = 0

        current[key] = text
        current_size += item_size

    if current:
        batches.append(current)

    return batches


def call_openai_translation_batch(fields_batch, target_language):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        message = "OPENAI_API_KEY not found. Public content translation cannot run."
        if OPENAI_TRANSLATION_REQUIRED:
            raise RuntimeError(message)

        print(message)
        return {}

    instructions = (
        "You are translating public guest-facing content for a vacation rental welcome book. "
        "Return ONLY valid JSON. The JSON must be an object with exactly the same keys provided by the user. "
        "Translate each value into the target language. Preserve meaning, tone, line breaks, and formatting. "
        "Do not add new information. Do not remove information. "
        "Do not translate property names, restaurant names, bar names, activity names, addresses, URLs, emails, phone numbers, times, codes, WiFi names, or passwords. "
        "If a value is already in the target language, keep it natural and only lightly polish if needed. "
        "Do not include markdown. Do not include explanations."
    )

    user_payload = {
        "target_language": target_language,
        "fields": fields_batch,
    }

    request_body = {
        "model": OPENAI_TRANSLATION_MODEL,
        "instructions": instructions,
        "input": json.dumps(user_payload, ensure_ascii=False),
        "max_output_tokens": 8000,
        "store": False,
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    retry_delays = [5, 10, 20]
    response_json = None

    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                raw = response.read().decode("utf-8")
                response_json = json.loads(raw)
            break
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            message = f"OpenAI translation HTTP error: {exc.code} {error_body[:1000]}"
            if OPENAI_TRANSLATION_REQUIRED:
                raise RuntimeError(message)

            print(message)
            return {}
        except (TimeoutError, socket.timeout, urllib.error.URLError) as exc:
            if attempt == 3:
                message = f"OpenAI translation failed after 3 attempts: {exc}"
                if OPENAI_TRANSLATION_REQUIRED:
                    raise RuntimeError(message)

                print(message)
                return {}

            time.sleep(retry_delays[attempt - 1])
        except Exception as exc:
            message = f"OpenAI translation error: {exc}"
            if OPENAI_TRANSLATION_REQUIRED:
                raise RuntimeError(message)

            print(message)
            return {}

    if response_json is None:
        message = "OpenAI translation failed after 3 attempts: Unknown error"
        if OPENAI_TRANSLATION_REQUIRED:
            raise RuntimeError(message)

        print(message)
        return {}

    text = extract_openai_response_text(response_json)

    if not text:
        message = "OpenAI translation returned empty text."
        if OPENAI_TRANSLATION_REQUIRED:
            raise RuntimeError(message)

        print(message)
        return {}

    try:
        translated = parse_translation_json(text)
    except Exception as exc:
        message = f"OpenAI translation JSON parse error: {exc}. Raw text: {text[:1000]}"
        if OPENAI_TRANSLATION_REQUIRED:
            raise RuntimeError(message)

        print(message)
        return {}

    if not isinstance(translated, dict):
        message = "OpenAI translation result was not a JSON object."
        if OPENAI_TRANSLATION_REQUIRED:
            raise RuntimeError(message)

        print(message)
        return {}

    missing_keys = [key for key in fields_batch.keys() if key not in translated]

    if missing_keys:
        message = f"OpenAI translation missing keys: {missing_keys}"
        if OPENAI_TRANSLATION_REQUIRED:
            raise RuntimeError(message)

        print(message)

    cleaned = {}

    for key, original_value in fields_batch.items():
        translated_value = translated.get(key, original_value)
        translated_text = safe_text(translated_value)

        cleaned[key] = translated_text if translated_text else original_value

    return cleaned


def translate_public_content_with_openai(fields_to_translate, target_language):
    if not fields_to_translate:
        return {}

    translated_all = {}

    batches = split_translation_batches(fields_to_translate)

    print(
        f"Translating {len(fields_to_translate)} public fields into {target_language} "
        f"using {OPENAI_TRANSLATION_MODEL} in {len(batches)} batch(es)."
    )

    for index, batch in enumerate(batches, start=1):
        print(f"Translation batch {index}/{len(batches)}: {list(batch.keys())}")

        translated_batch = call_openai_translation_batch(batch, target_language)
        translated_all.update(translated_batch)

    return translated_all


def translate_public_content(content_flat, target_language):
    translated_content = dict(content_flat)

    if target_language == "English":
        return translated_content

    fields_to_translate = {}

    for field_name in TRANSLATABLE_PUBLIC_FIELDS:
        value = content_flat.get(field_name)

        if not has_value(value):
            continue

        text = normalize_text_block(value)

        if looks_like_non_translatable_value(text):
            continue

        fields_to_translate[field_name] = text

    if not fields_to_translate:
        print(f"No public fields to translate for {target_language}.")
        return translated_content

    translated_fields = translate_public_content_with_openai(
        fields_to_translate,
        target_language
    )

    for field_name, translated_value in translated_fields.items():
        if field_name in fields_to_translate and has_value(translated_value):
            translated_content[field_name] = translated_value

    return translated_content



def resolve_language(primary_language):
    clean = safe_text(primary_language)
    return clean if clean in SUPPORTED_LANGUAGES else "English"

def normalize_environment(property_environment):
    clean = safe_text(property_environment)
    if not clean:
        return "Beach"

    normalized = ENVIRONMENT_ALIASES.get(clean.lower())
    if normalized:
        return normalized

    title_case = clean.title()
    return title_case if title_case in COVER_IMAGES_BY_ENVIRONMENT else "Beach"

def find_field_deep(source, field_name):
    if isinstance(source, dict):
        for key, value in source.items():
            if key == field_name:
                return value

            found = find_field_deep(value, field_name)
            if has_value(found):
                return found

    if isinstance(source, list):
        for item in source:
            found = find_field_deep(item, field_name)
            if has_value(found):
                return found

    return ""


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


def build_cover_image_block(content_flat, villa_name, property_environment=""):
    environment = normalize_environment(first_non_empty(property_environment, content_flat.get("property_environment")))
    cover_url = COVER_IMAGES_BY_ENVIRONMENT.get(environment, SHARED_IMAGES["cover"])
    return image_block(cover_url, villa_name, arch=True)


def build_welcome_image_block(content_flat, villa_name):
    return image_block(SHARED_IMAGES["welcome"], villa_name, arch=False)


def build_welcome_message_block(content_flat):
    return html_multiline(content_flat.get("welcome_message"))


def build_about_hosts_block(content_flat, active_language):
    about_hosts = html_multiline(content_flat.get("about_hosts"))
    if not about_hosts:
        return ""

    title = UI_STRINGS.get(active_language, UI_STRINGS["English"])["about_us"]

    return f'''
        <div class="welcome-about">
            <div class="welcome-about-title">{escape(title)}</div>
            <p class="welcome-about-copy">{about_hosts}</p>
        </div>
    '''


def icon_button_svg(kind):
    if kind == "maps":
        return '''
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 21s-6-4.35-6-10a6 6 0 1 1 12 0c0 5.65-6 10-6 10Z"></path>
                <circle cx="12" cy="11" r="2.5" fill="currentColor" stroke="none"></circle>
            </svg>
        '''
    if kind == "email":
        return '''
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="3" y="5" width="18" height="14" rx="2"></rect>
                <path d="M4 7l8 6 8-6"></path>
            </svg>
        '''
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


def ensure_link_or_search(url, name, property_address=""):
    clean_url = safe_text(url)
    if clean_url:
        if clean_url.startswith(("http://", "https://", "mailto:", "tel:")):
            return clean_url
        if "." in clean_url and " " not in clean_url:
            return "https://" + clean_url
    return google_maps_search_url(name, property_address)


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
        description = first_non_empty(
            content_flat.get(f"{prefix}_{index}_description"),
            content_flat.get(f"{prefix}_{index}_notes"),
        )

        if not name:
            continue

        final_link = ensure_link_or_search(link, name, property_address)

        places.append({
            "name": name,
            "link": final_link,
            "phone": phone,
            "image": image,
            "rating": rating,
            "category": category,
            "address": address,
            "description": description,
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

def get_restaurant_places(content_flat, property_address="", active_language="English"):
    places = build_places_from_numbered_fields(content_flat, "restaurant", "maps_link", property_address)
    if places:
        return places
    fallback_name = STATIC_TEMPLATE_TRANSLATIONS.get(active_language, {}).get("Restaurants", "Restaurants")
    return legacy_text_to_single_place(content_flat.get("places_to_eat"), fallback_name, property_address)


def get_bar_places(content_flat, property_address="", active_language="English"):
    places = build_places_from_numbered_fields(content_flat, "bar", "maps_link", property_address)
    if places:
        return places
    fallback_name = STATIC_TEMPLATE_TRANSLATIONS.get(active_language, {}).get("Bars & Drinks", "Bars & Drinks")
    return legacy_text_to_single_place(content_flat.get("places_to_drink"), fallback_name, property_address)


def get_activity_places(content_flat, property_address="", active_language="English"):
    places = build_places_from_numbered_fields(content_flat, "activity", "link", property_address)
    if places:
        return places
    fallback_name = STATIC_TEMPLATE_TRANSLATIONS.get(active_language, {}).get("Things to Do", "Things to Do")
    return legacy_text_to_single_place(content_flat.get("things_to_do"), fallback_name, property_address)



def pick_recommendation_image(default_image_url, image_pool, index):
    if image_pool and isinstance(image_pool, list):
        clean_pool = [safe_text(item) for item in image_pool if safe_text(item)]
        if clean_pool:
            return clean_pool[index % len(clean_pool)]
    return default_image_url


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


def build_recommendation_cards(places, default_image_url, default_meta, primary_action_label, call_label, image_pool=None):
    if not places:
        return ""

    cards = []

    for index, place in enumerate(places):
        name = safe_text(place.get("name"))
        if not name:
            continue

        fallback_image_url = pick_recommendation_image(default_image_url, image_pool, index)
        image_url = safe_text(place.get("image")) or fallback_image_url
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
        actions += recommendation_action_link("phone", call_label, place.get("phone"))

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


def build_places_to_eat_html(content_flat, property_address, active_language):
    ui = UI_STRINGS.get(active_language, UI_STRINGS["English"])
    places = get_restaurant_places(content_flat, property_address, active_language)
    return build_recommendation_cards(
        places,
        SHARED_IMAGES["places_to_eat"],
        ui["restaurants_meta"],
        ui["google_maps"],
        ui["call"],
        RECOMMENDATION_IMAGE_POOLS["places_to_eat"],
    )


def build_places_to_drink_html(content_flat, property_address, active_language):
    ui = UI_STRINGS.get(active_language, UI_STRINGS["English"])
    places = get_bar_places(content_flat, property_address, active_language)
    return build_recommendation_cards(
        places,
        SHARED_IMAGES["places_to_drink"],
        ui["bars_meta"],
        ui["google_maps"],
        ui["call"],
        RECOMMENDATION_IMAGE_POOLS["places_to_drink"],
    )


def build_things_to_do_html(content_flat, property_address, active_language):
    ui = UI_STRINGS.get(active_language, UI_STRINGS["English"])
    places = get_activity_places(content_flat, property_address, active_language)
    return build_recommendation_cards(
        places,
        SHARED_IMAGES["things_to_do"],
        ui["activities_meta"],
        ui["open_link"],
        ui["call"],
        RECOMMENDATION_IMAGE_POOLS["things_to_do"],
    )

def has_recommendation_items(content_flat, field_name, property_address=""):
    if field_name == "places_to_eat":
        return bool(get_restaurant_places(content_flat, property_address, "English"))
    if field_name == "places_to_drink":
        return bool(get_bar_places(content_flat, property_address, "English"))
    if field_name == "things_to_do":
        return bool(get_activity_places(content_flat, property_address, "English"))
    return has_value(content_flat.get(field_name))



def build_editorial_image_block(content_flat, field_name, alt_text, photo_index, property_address=""):
    if not has_recommendation_items(content_flat, field_name, property_address):
        return ""
    image_url = SHARED_IMAGES.get(field_name, SHARED_IMAGES["welcome"])
    return image_block(image_url, alt_text, arch=False)


def build_directions_map_block(content_flat, ui, property_address=""):
    maps_url = safe_text(content_flat.get("google_maps_link"))
    address = safe_text(property_address)

    if not maps_url and not address:
        return ""

    maps_html = ""
    if maps_url:
        maps_html = f'''
            <a href="{escape(maps_url)}" target="_blank" rel="noopener noreferrer">
                {escape(ui["open_maps"])}
            </a>
        '''

    address_html = ""
    if address:
        address_html = f'''
            <div class="private-card">
                <div class="private-card-title">Address</div>
                <div class="private-card-text">{html_multiline(address)}</div>
            </div>
        '''

    return f"{maps_html}{address_html}"


def build_pet_friendly_text(content_flat, ui):
    raw = content_flat.get("pet_friendly")
    bool_value = safe_bool(raw)

    if bool_value is True:
        return escape(ui["yes"])
    if bool_value is False:
        return escape(ui["no"])

    return html_multiline(raw)


def apply_static_template_translations(html, active_language):
    translations = STATIC_TEMPLATE_TRANSLATIONS.get(active_language, {})
    if not translations:
        return html

    parts = re.split(r"(\{\{[A-Z0-9_]+\}\})", html)
    translated_parts = []

    ordered_translations = sorted(translations.items(), key=lambda pair: len(pair[0]), reverse=True)

    for part in parts:
        if part.startswith("{{") and part.endswith("}}"):
            translated_parts.append(part)
            continue

        for source_text, translated_text in ordered_translations:
            part = part.replace(source_text, translated_text)

        translated_parts.append(part)

    return "".join(translated_parts)


def replace_placeholder(html, placeholder, value):
    return html.replace(placeholder, value if value is not None else "")


def strip_unreplaced_placeholders(html):
    return re.sub(r"\{\{[A-Z0-9_]+\}\}", "", html)


def inject_public_qa_overrides(html):
    return html


def render_html_for_language(payload, active_language, output_filename):
    metadata = payload.get("metadata", {}) or {}
    property_data = payload.get("property", {}) or {}
    content = payload.get("content", {}) or {}
    content_flat = flatten_content(content)
    content_flat = translate_public_content(content_flat, active_language)

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

    raw_property_environment = first_non_empty(
        property_data.get("property_environment"),
        content_flat.get("property_environment"),
        payload.get("property_environment"),
        find_field_deep(payload, "property_environment"),
    )

    property_environment = normalize_environment(raw_property_environment)
    print(f"Property environment resolved: {property_environment}")
    
    ui = UI_STRINGS.get(active_language, UI_STRINGS["English"])
    slug = safe_text(metadata.get("slug")) or "demo"
    guest_access_url = ""

    with open("templates/master.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = apply_static_template_translations(html, active_language)

    replacements = {
        "{{HTML_LANG}}": escape(ui["html_lang"]),
        "{{VILLA_NAME}}": escape(villa_name),
        "{{PROPERTY_ADDRESS}}": escape(property_address),
        "{{PROPERTY_ENVIRONMENT}}": escape(property_environment),
        "{{LANGUAGE_BAR}}": build_language_bar(active_language),
        "{{COVER_IMAGE_BLOCK}}": build_cover_image_block(content_flat, villa_name, property_environment),
        "{{WELCOME_IMAGE_BLOCK}}": build_welcome_image_block(content_flat, villa_name),
        "{{WELCOME_MESSAGE_BLOCK}}": build_welcome_message_block(content_flat),
        "{{ABOUT_HOSTS_BLOCK}}": build_about_hosts_block(content_flat, active_language),
        "{{WELCOME_ACTIONS_BLOCK}}": build_welcome_actions_block(content_flat),
        "{{CHECKIN_CHECKOUT_BLOCK}}": "",
        "{{CONTENT_SECTIONS}}": "",
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

        "{{HOUSE_RULES}}": html_multiline(content_flat.get("house_rules")),
        "{{PET_FRIENDLY}}": build_pet_friendly_text(content_flat, ui),
        "{{PET_RULES}}": html_multiline(content_flat.get("pet_rules")),

        "{{DIRECTIONS_MAP_BLOCK}}": build_directions_map_block(content_flat, ui, property_address),
        "{{GOOGLE_MAPS_LINK}}": html_multiline(content_flat.get("google_maps_link")),
        "{{DIRECTIONS_TEXT}}": html_multiline(content_flat.get("directions_text")),
        "{{TRANSPORT_OPTIONS}}": html_multiline(content_flat.get("transport_options")),

        "{{THINGS_TO_KNOW}}": html_multiline(content_flat.get("things_to_know")),
        "{{BEFORE_YOU_LEAVE}}": html_multiline(content_flat.get("before_you_leave")),

        "{{PLACES_TO_EAT}}": build_places_to_eat_html(content_flat, property_address, active_language),
        "{{PLACES_TO_DRINK}}": build_places_to_drink_html(content_flat, property_address, active_language),
        "{{THINGS_TO_DO}}": build_things_to_do_html(content_flat, property_address, active_language),

        "{{THINGS_TO_DO_IMAGE_BLOCK}}": build_editorial_image_block(content_flat, "things_to_do", "Things to Do", 1, property_address),
        "{{PLACES_TO_EAT_IMAGE_BLOCK}}": build_editorial_image_block(content_flat, "places_to_eat", "Restaurants", 2, property_address),
        "{{PLACES_TO_DRINK_IMAGE_BLOCK}}": build_editorial_image_block(content_flat, "places_to_drink", "Bars & Drinks", 3, property_address),

        "{{EMERGENCY_CONTACTS}}": html_multiline(content_flat.get("emergency_contacts")),
        "{{LOCAL_DIRECTORY}}": html_multiline(content_flat.get("local_directory")),
        "{{AIRBNB_REVIEW_LINK}}": escape(safe_text(content_flat.get("airbnb_review_link"))),
        "{{HOST_EMAIL}}": html_multiline(content_flat.get("host_email")),
        "{{INSTAGRAM_HANDLE}}": html_multiline(content_flat.get("instagram_handle")),

        "{{PRIVATE_LABEL_WIFI_NETWORK}}": escape(STATIC_TEMPLATE_TRANSLATIONS.get(active_language, {}).get("WiFi network", "WiFi network")),
        "{{PRIVATE_LABEL_WIFI_PASSWORD}}": escape(STATIC_TEMPLATE_TRANSLATIONS.get(active_language, {}).get("WiFi password", "WiFi password")),
        "{{PRIVATE_LABEL_DOOR_CODE}}": escape(STATIC_TEMPLATE_TRANSLATIONS.get(active_language, {}).get("Door code", "Door code")),
        "{{PRIVATE_LABEL_ACCESS_NOTES}}": escape(STATIC_TEMPLATE_TRANSLATIONS.get(active_language, {}).get("Access notes", "Access notes")),
        "{{PRIVATE_LABEL_HOST_PHONE}}": escape(STATIC_TEMPLATE_TRANSLATIONS.get(active_language, {}).get("Host phone", "Host phone")),
    }

    for placeholder, value in replacements.items():
        html = replace_placeholder(html, placeholder, value)

    html = strip_unreplaced_placeholders(html)
    html = inject_public_qa_overrides(html)

    output_dir = os.path.join("public", "villas", slug)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated public/villas/{slug}/{output_filename}")


def generate():
    try:
        payload = json.loads(sys.argv[1])
    except Exception as exc:
        print(f"Error al leer JSON: {exc}")
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
