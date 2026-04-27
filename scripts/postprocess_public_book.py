import json
import re
import sys
from html import escape
from pathlib import Path

CSS_MARKER = "/* MyGuest Bloque 12 approved screens */"
WELCOME_IMG = "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&q=80"

EMPTY_TEXT_VALUES = {"", "-", "n/a", "na", "none", "null", "undefined"}
CONTENT_FIELD_MAP = {
    "checkin_time": "checkin",
    "checkout_time": "checkin",
    "house_access_public": "checkin",
    "parking_info": "checkin",
    "google_maps_link": "location_transport",
    "directions_text": "location_transport",
    "transport_options": "location_transport",
    "amenities_list": "about_house",
    "house_rules": "rules_info",
    "pet_friendly": "rules_info",
    "pet_rules": "rules_info",
    "things_to_know": "rules_info",
}

CSS = f"""
{CSS_MARKER}
:root {{
  --myguest-deep-text:#3A2A1C;
  --myguest-muted-text:#5B4635;
  --myguest-icon:#7A624C;
  --myguest-tile:#F4EEE6;
  --myguest-border:#DDCFC0;
  --myguest-screen-h:calc(100svh - 92px);
}}
body,.welcome-message,.menu-label,.paragraph,.info-value,.info-row,.card,.section-title,.arrival-time,.arrival-detail-text,.list-item-text,.rule-text,.arrival-approved-text {{ color:var(--myguest-deep-text)!important; }}
.screen:not(.cover-screen) {{ min-height:var(--myguest-screen-h)!important; }}
.welcome-card .arrival-grid,.welcome-card .welcome-divider,.welcome-card .welcome-actions,.welcome-card .welcome-signoff,.welcome-card .welcome-eyebrow {{ display:none!important; }}
.welcome-card {{ padding-top:clamp(20px,5vw,28px)!important;padding-bottom:clamp(20px,5vw,28px)!important; }}
.welcome-image {{ display:block!important;min-height:190px!important;max-height:260px!important;background:linear-gradient(180deg,#F7F0E8,#E7D8C7)!important;border-radius:8px!important; }}
.welcome-image img {{ display:block!important;width:100%!important;height:clamp(190px,36svh,260px)!important;object-fit:cover!important;border-radius:8px!important; }}
.menu-screen-approved {{ min-height:var(--myguest-screen-h)!important;background:radial-gradient(circle at 85% 6%, rgba(216,206,186,.36), transparent 34%),linear-gradient(180deg,rgba(255,255,255,.78),rgba(255,250,244,.92))!important;border:1px solid rgba(138,112,74,.14)!important;border-radius:34px!important;box-shadow:0 18px 42px rgba(58,42,28,.08)!important;padding:18px 16px 22px!important; }}
.menu-screen-approved .menu-kicker {{ font-family:'Cormorant Garamond',serif!important;font-size:clamp(14px,3.6vw,18px)!important;line-height:1!important;letter-spacing:.34em!important;text-transform:uppercase!important;color:var(--primary)!important;text-align:center!important;margin-bottom:2px!important;opacity:.9!important; }}
.menu-screen-approved .menu-script-title {{ font-family:'Great Vibes',cursive!important;font-size:clamp(54px,16vw,76px)!important;line-height:.9!important;color:var(--primary)!important;text-align:center!important;margin:0 0 8px!important;font-weight:400!important; }}
.menu-screen-approved .menu-subtitle {{ font-family:'Cormorant Garamond',serif!important;font-size:clamp(18px,5vw,25px)!important;line-height:1.12!important;letter-spacing:.08em!important;color:var(--primary)!important;text-align:center!important;text-transform:none!important;margin:0 auto 18px!important;max-width:92%!important; }}
.menu-grid-approved {{ display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;column-gap:10px!important;row-gap:12px!important;align-items:stretch!important; }}
.menu-screen-approved .menu-link {{ display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:flex-start!important;min-width:0!important;text-decoration:none!important;color:var(--text)!important;-webkit-tap-highlight-color:transparent!important; }}
.menu-screen-approved .menu-tile {{ width:100%!important;aspect-ratio:1.05/.88!important;border-radius:21px!important;background:linear-gradient(180deg,rgba(255,255,255,.94),rgba(252,247,240,.92))!important;border:1px solid rgba(138,112,74,.20)!important;box-shadow:0 9px 22px rgba(58,42,28,.07),inset 0 1px 0 rgba(255,255,255,.9)!important;display:flex!important;align-items:center!important;justify-content:center!important;margin-bottom:6px!important; }}
.menu-screen-approved .menu-icon {{ width:clamp(31px,9vw,42px)!important;height:clamp(31px,9vw,42px)!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;color:var(--primary)!important; }}
.menu-screen-approved .menu-icon svg,.arrival-approved-icon svg,.arrival-approved-back svg,.arrival-approved-map svg {{ width:100%!important;height:100%!important;stroke:currentColor!important;fill:none!important;stroke-width:1.75!important;stroke-linecap:round!important;stroke-linejoin:round!important; }}
.menu-screen-approved .menu-label {{ font-family:'Cormorant Garamond',serif!important;font-size:clamp(14px,3.7vw,17px)!important;line-height:1.05!important;color:var(--myguest-deep-text)!important;font-weight:500!important;text-align:center!important;min-height:32px!important;display:flex!important;align-items:flex-start!important;justify-content:center!important; }}
.menu-screen-approved .menu-item-wide-left {{ grid-column:1 / 2!important;transform:translateX(56%)!important; }}
.menu-screen-approved .menu-item-wide-right {{ grid-column:3 / 4!important;transform:translateX(-56%)!important; }}
.arrival-screen-approved {{ position:relative!important;min-height:var(--myguest-screen-h)!important;background:radial-gradient(circle at 88% 6%,rgba(216,206,186,.32),transparent 35%),linear-gradient(180deg,rgba(255,255,255,.82),rgba(255,250,244,.94))!important;border:1px solid rgba(138,112,74,.14)!important;border-radius:34px!important;box-shadow:0 18px 42px rgba(58,42,28,.08)!important;padding:18px 16px 22px!important; }}
.arrival-approved-back {{ display:inline-flex!important;align-items:center!important;gap:7px!important;padding:11px 16px!important;border-radius:999px!important;background:rgba(244,238,230,.95)!important;border:1px solid rgba(138,112,74,.14)!important;box-shadow:0 9px 22px rgba(58,42,28,.06)!important;color:var(--myguest-deep-text)!important;text-decoration:none!important;font-family:'Montserrat',sans-serif!important;font-size:15px!important;font-weight:500!important; }}
.arrival-approved-back svg {{ width:20px!important;height:20px!important; }}
.arrival-approved-ornament {{ width:42px!important;height:42px!important;margin:4px auto 4px!important;color:var(--primary)!important;opacity:.86!important; }}
.arrival-approved-title {{ font-family:'Cormorant Garamond',serif!important;font-size:clamp(58px,17vw,82px)!important;line-height:.86!important;color:var(--myguest-deep-text)!important;text-align:center!important;font-weight:500!important;margin:0 0 10px!important;letter-spacing:0!important;text-transform:none!important; }}
.arrival-approved-subtitle {{ font-family:'Montserrat',sans-serif!important;font-size:clamp(15px,4.2vw,18px)!important;line-height:1.35!important;text-align:center!important;color:var(--myguest-deep-text)!important;margin:0 auto 22px!important;max-width:92%!important; }}
.arrival-approved-time-grid {{ display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:12px!important;margin-bottom:14px!important; }}
.arrival-approved-time-card {{ background:linear-gradient(180deg,rgba(255,255,255,.94),rgba(252,247,240,.92))!important;border:1px solid rgba(138,112,74,.18)!important;border-radius:24px!important;box-shadow:0 10px 24px rgba(58,42,28,.07)!important;min-height:164px!important;padding:18px 10px 16px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;text-align:center!important; }}
.arrival-approved-time-card .arrival-approved-icon {{ width:64px!important;height:64px!important;border-radius:999px!important;background:#F4EEE6!important;color:var(--myguest-deep-text)!important;display:flex!important;align-items:center!important;justify-content:center!important;margin-bottom:14px!important;padding:16px!important; }}
.arrival-approved-label {{ font-family:'Montserrat',sans-serif!important;font-size:13px!important;font-weight:600!important;line-height:1!important;letter-spacing:.08em!important;text-transform:uppercase!important;color:var(--myguest-deep-text)!important;margin-bottom:14px!important; }}
.arrival-approved-time {{ font-family:'Cormorant Garamond',serif!important;font-size:clamp(42px,12vw,60px)!important;line-height:.9!important;color:var(--myguest-deep-text)!important;font-weight:500!important; }}
.arrival-approved-info-card {{ display:grid!important;grid-template-columns:78px 1fr!important;gap:15px!important;align-items:center!important;background:linear-gradient(180deg,rgba(255,255,255,.94),rgba(252,247,240,.92))!important;border:1px solid rgba(138,112,74,.18)!important;border-radius:24px!important;box-shadow:0 10px 24px rgba(58,42,28,.07)!important;padding:16px!important;margin-bottom:14px!important; }}
.arrival-approved-info-card .arrival-approved-icon {{ width:62px!important;height:62px!important;border-radius:999px!important;background:#F4EEE6!important;color:var(--myguest-deep-text)!important;display:flex!important;align-items:center!important;justify-content:center!important;padding:15px!important; }}
.arrival-approved-heading {{ font-family:'Montserrat',sans-serif!important;font-size:clamp(18px,5vw,23px)!important;line-height:1.12!important;font-weight:600!important;color:var(--myguest-deep-text)!important;margin-bottom:8px!important; }}
.arrival-approved-text {{ font-family:'Montserrat',sans-serif!important;font-size:clamp(14px,3.9vw,16px)!important;line-height:1.5!important;font-weight:400!important;color:var(--myguest-deep-text)!important; }}
.arrival-approved-map {{ width:100%!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:15px!important;min-height:68px!important;padding:18px 20px!important;border-radius:22px!important;background:rgba(255,250,244,.70)!important;border:1.5px solid var(--primary)!important;color:var(--primary)!important;text-decoration:none!important;font-family:'Montserrat',sans-serif!important;font-size:clamp(18px,5vw,24px)!important;font-weight:500!important;box-shadow:0 10px 24px rgba(58,42,28,.06)!important; }}
.arrival-approved-map svg {{ width:30px!important;height:30px!important; }}
@media (max-width:380px) {{
  .menu-screen-approved,.arrival-screen-approved {{ padding:16px 12px 20px!important; }}
  .menu-grid-approved {{ column-gap:8px!important;row-gap:10px!important; }}
  .menu-screen-approved .menu-tile {{ border-radius:18px!important;margin-bottom:5px!important; }}
  .menu-screen-approved .menu-label {{ font-size:clamp(12px,3.5vw,15px)!important;min-height:30px!important; }}
  .menu-screen-approved .menu-script-title {{ font-size:clamp(48px,15vw,66px)!important; }}
  .arrival-approved-time-grid {{ gap:9px!important; }}
  .arrival-approved-time-card {{ min-height:145px!important;border-radius:21px!important; }}
  .arrival-approved-info-card {{ grid-template-columns:64px 1fr!important;gap:12px!important;padding:14px!important; }}
  .arrival-approved-info-card .arrival-approved-icon {{ width:54px!important;height:54px!important; }}
}}
"""

ICONS = {
    "arrival": '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="20"></circle><path d="M32 18v15l10 6"></path></svg>',
    "location": '<svg viewBox="0 0 64 64"><path d="M32 56s18-14 18-32a18 18 0 1 0-36 0c0 18 18 32 18 32Z"></path><circle cx="32" cy="24" r="6"></circle></svg>',
    "wifi": '<svg viewBox="0 0 64 64"><path d="M14 28a28 28 0 0 1 36 0"></path><path d="M22 38a16 16 0 0 1 20 0"></path><path d="M30 48a4 4 0 0 1 4 0"></path><circle cx="32" cy="52" r="2.5"></circle></svg>',
    "house_guide": '<svg viewBox="0 0 64 64"><path d="M12 31 32 14l20 17"></path><path d="M18 29v23h28V29"></path><path d="M27 52V39h10v13"></path></svg>',
    "house_rules": '<svg viewBox="0 0 64 64"><path d="M20 10h20l8 8v36H20Z"></path><path d="M40 10v10h8"></path><path d="M26 28h16"></path><path d="M26 36h16"></path><path d="M26 44h10"></path></svg>',
    "things_to_know": '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="22"></circle><path d="M32 29v16"></path><circle cx="32" cy="20" r="2.5"></circle></svg>',
    "things_to_do": '<svg viewBox="0 0 64 64"><circle cx="32" cy="30" r="10"></circle><path d="M32 8v8"></path><path d="M32 44v8"></path><path d="M10 30h8"></path><path d="M46 30h8"></path><path d="M17 15l6 6"></path><path d="M47 15l-6 6"></path><path d="M18 52c7-8 21-8 28 0"></path></svg>',
    "places_to_eat": '<svg viewBox="0 0 64 64"><path d="M22 10v22"></path><path d="M15 10v18c0 5 3 8 7 8s7-3 7-8V10"></path><path d="M22 36v18"></path><path d="M43 10c7 8 7 20 0 27v17"></path></svg>',
    "places_to_drink": '<svg viewBox="0 0 64 64"><path d="M20 12h24l-4 22a8 8 0 0 1-16 0Z"></path><path d="M32 42v12"></path><path d="M24 54h16"></path><path d="M42 17l7-5"></path></svg>',
    "local_directory": '<svg viewBox="0 0 64 64"><rect x="18" y="12" width="30" height="40" rx="4"></rect><path d="M14 20h8"></path><path d="M14 30h8"></path><path d="M14 40h8"></path><circle cx="33" cy="28" r="6"></circle><path d="M24 44c4-7 14-7 18 0"></path></svg>',
    "emergency": '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="22"></circle><path d="M32 20v24"></path><path d="M20 32h24"></path></svg>',
    "contact": '<svg viewBox="0 0 64 64"><rect x="12" y="18" width="40" height="28" rx="4"></rect><path d="M14 21l18 15 18-15"></path></svg>',
    "before_leave": '<svg viewBox="0 0 64 64"><rect x="16" y="24" width="32" height="26" rx="4"></rect><path d="M24 24v-8h16v8"></path><path d="M16 34h32"></path></svg>',
    "review": '<svg viewBox="0 0 64 64"><path d="M14 16h36v26H29L17 52V42h-3Z"></path><path d="M32 23l3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1Z"></path></svg>',
    "door": '<svg viewBox="0 0 64 64"><path d="M22 54V14h22v40"></path><path d="M18 54h30"></path><circle cx="38" cy="34" r="2"></circle><path d="M26 18h8"></path></svg>',
    "car": '<svg viewBox="0 0 64 64"><path d="M16 36l4-12h24l4 12"></path><rect x="13" y="34" width="38" height="14" rx="5"></rect><circle cx="22" cy="48" r="3"></circle><circle cx="42" cy="48" r="3"></circle><path d="M20 24h24"></path></svg>',
    "map": '<svg viewBox="0 0 64 64"><path d="M32 56s18-14 18-32a18 18 0 1 0-36 0c0 18 18 32 18 32Z"></path><circle cx="32" cy="24" r="6"></circle></svg>',
    "bag": '<svg viewBox="0 0 64 64"><path d="M22 25v-7c0-6 4-10 10-10s10 4 10 10v7"></path><rect x="16" y="25" width="32" height="28" rx="5"></rect><path d="M22 33h20"></path></svg>',
    "arrow": '<svg viewBox="0 0 64 64"><path d="M38 18 24 32l14 14"></path></svg>',
}

MENU_LABELS = {
    "en": {"kicker":"Your Guide","title":"Your Guide","subtitle":"Everything you need for a perfect stay","arrival":"Arrival","location":"Location","wifi":"WiFi","house_guide":"House Guide","house_rules":"House Rules","things_to_know":"Things to Know","things_to_do":"Things to Do","places_to_eat":"Places to Eat","places_to_drink":"Places to Drink","local_directory":"Local Directory","emergency":"Emergency","contact":"Contact Me","before_leave":"Before You Leave","review":"Review"},
    "es": {"kicker":"Tu Guía","title":"Tu Guía","subtitle":"Todo lo que necesitas para una estancia perfecta","arrival":"Llegada","location":"Ubicación","wifi":"WiFi","house_guide":"Guía de la Casa","house_rules":"Reglas de la Casa","things_to_know":"Información Importante","things_to_do":"Qué Hacer","places_to_eat":"Dónde Comer","places_to_drink":"Dónde Tomar Algo","local_directory":"Directorio Local","emergency":"Emergencias","contact":"Contáctame","before_leave":"Antes de Salir","review":"Reseña"},
    "fr": {"kicker":"Votre Guide","title":"Votre Guide","subtitle":"Tout ce dont vous avez besoin pour un séjour parfait","arrival":"Arrivée","location":"Emplacement","wifi":"WiFi","house_guide":"Guide de la Maison","house_rules":"Règles de la Maison","things_to_know":"À Savoir","things_to_do":"Activités","places_to_eat":"Où Manger","places_to_drink":"Où Boire","local_directory":"Répertoire Local","emergency":"Urgence","contact":"Me Contacter","before_leave":"Avant le Départ","review":"Avis"},
}

ARRIVAL_LABELS = {
    "en": {"menu":"Menu","title":"Arrival","subtitle":"Everything you need before you arrive","checkin":"Check-in","checkout":"Check-out","access":"Public Access Info","parking":"Parking","maps":"Open Maps"},
    "es": {"menu":"Menú","title":"Llegada","subtitle":"Todo lo que necesitas antes de llegar","checkin":"Llegada","checkout":"Salida","access":"Acceso Público","parking":"Estacionamiento","maps":"Abrir Mapa"},
    "fr": {"menu":"Menu","title":"Arrivée","subtitle":"Tout ce dont vous avez besoin avant votre arrivée","checkin":"Arrivée","checkout":"Départ","access":"Accès Public","parking":"Stationnement","maps":"Ouvrir la Carte"},
}

LOCATION_LABELS = {
    "en": {"menu":"Menu","title":"Location","subtitle":"Find your way","address":"Address","maps":"Open Maps","directions":"Directions","transport":"Getting Around"},
    "es": {"menu":"Menú","title":"Ubicación","subtitle":"Encuentra cómo llegar","address":"Dirección","maps":"Abrir Mapa","directions":"Cómo Llegar","transport":"Cómo Moverse"},
    "fr": {"menu":"Menu","title":"Emplacement","subtitle":"Trouvez votre chemin","address":"Adresse","maps":"Ouvrir la Carte","directions":"Itinéraire","transport":"Se Déplacer"},
}

INFO_LABELS = {
    "en": {
        "menu":"Menu",
        "wifi_title":"WiFi",
        "wifi_subtitle":"Secure access",
        "wifi_heading":"Private WiFi Access",
        "wifi_text":"WiFi details are available through the private guest access.",
        "wifi_button":"Open Private Access",
        "guide_title":"House Guide",
        "guide_subtitle":"How to enjoy the home",
        "amenities":"Amenities",
        "rules_title":"House Rules",
        "rules_subtitle":"Please review before your stay",
        "rules":"House Rules",
        "pets":"Pets",
        "know_title":"Things to Know",
        "know_subtitle":"Helpful tips for your stay",
        "know":"Things to Know",
    },
    "es": {
        "menu":"Menú",
        "wifi_title":"WiFi",
        "wifi_subtitle":"Acceso seguro",
        "wifi_heading":"Acceso Privado al WiFi",
        "wifi_text":"Los datos del WiFi están disponibles en el acceso privado para huéspedes.",
        "wifi_button":"Abrir Acceso Privado",
        "guide_title":"Guía de la Casa",
        "guide_subtitle":"Cómo disfrutar la propiedad",
        "amenities":"Amenidades",
        "rules_title":"Reglas de la Casa",
        "rules_subtitle":"Revísalas antes de tu estancia",
        "rules":"Reglas de la Casa",
        "pets":"Mascotas",
        "know_title":"Información Importante",
        "know_subtitle":"Tips útiles para tu estancia",
        "know":"Información Importante",
    },
    "fr": {
        "menu":"Menu",
        "wifi_title":"WiFi",
        "wifi_subtitle":"Accès sécurisé",
        "wifi_heading":"Accès WiFi Privé",
        "wifi_text":"Les informations WiFi sont disponibles via l’accès privé invité.",
        "wifi_button":"Ouvrir l’Accès Privé",
        "guide_title":"Guide de la Maison",
        "guide_subtitle":"Comment profiter de la maison",
        "amenities":"Équipements",
        "rules_title":"Règles de la Maison",
        "rules_subtitle":"Veuillez les lire avant votre séjour",
        "rules":"Règles de la Maison",
        "pets":"Animaux",
        "know_title":"À Savoir",
        "know_subtitle":"Conseils utiles pour votre séjour",
        "know":"À Savoir",
    },
}

MENU_ITEMS = [("arrival","#arrival-screen",""),("location","#location-screen",""),("wifi","#wifi-screen",""),("house_guide","#house-guide-screen",""),("house_rules","#house-rules-screen",""),("things_to_know","#things-to-know-screen",""),("things_to_do","#things-to-do-screen",""),("places_to_eat","#places-to-eat-screen",""),("places_to_drink","#places-to-drink-screen",""),("local_directory","#local-directory-screen",""),("emergency","#emergency-screen",""),("contact","#contact-screen",""),("before_leave","#before-you-leave-screen","menu-item-wide-left"),("review","#review-screen","menu-item-wide-right")]


def safe_text(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(safe_text(item) for item in value if safe_text(item)).strip()
    if isinstance(value, dict):
        return "\n".join(safe_text(item) for item in value.values() if safe_text(item)).strip()
    text = str(value).strip()
    return "" if text.lower() in EMPTY_TEXT_VALUES else text


def html_text(value):
    return escape(safe_text(value)).replace("\n", "<br>")


def get_content(payload, field):
    content = payload.get("content", {}) or {}
    block_name = CONTENT_FIELD_MAP.get(field)
    if block_name and isinstance(content.get(block_name), dict):
        value = content.get(block_name, {}).get(field)
        if safe_text(value):
            return value
    return content.get(field)


def get_lang(html: str) -> str:
    match = re.search(r'<html[^>]*lang="([^"]+)"', html, flags=re.IGNORECASE)
    raw = (match.group(1).lower() if match else "en")
    if raw.startswith("es"):
        return "es"
    if raw.startswith("fr"):
        return "fr"
    return "en"


def menu_item_html(key, href, extra_class, labels):
    return f'<a class="menu-item menu-link {extra_class}" href="{href}"><span class="menu-tile"><span class="menu-icon" aria-hidden="true">{ICONS[key]}</span></span><span class="menu-label">{labels[key]}</span></a>'


def build_menu(html):
    labels = MENU_LABELS[get_lang(html)]
    items = "\n".join(menu_item_html(k, h, c, labels) for k, h, c in MENU_ITEMS)
    return f'<section id="menu-sheet" class="screen menu-card menu-screen-approved"><div class="menu-kicker">{labels["kicker"]}</div><h2 class="menu-script-title">{labels["title"]}</h2><p class="menu-subtitle">{labels["subtitle"]}</p><div class="menu-grid menu-grid-approved">{items}</div></section>'


def arrival_time_card(label, value, icon):
    if not safe_text(value):
        return ""
    return f'<div class="arrival-approved-time-card"><div class="arrival-approved-icon" aria-hidden="true">{ICONS[icon]}</div><div class="arrival-approved-label">{escape(label)}</div><div class="arrival-approved-time">{escape(safe_text(value))}</div></div>'


def arrival_info_card(title, text, icon):
    if not safe_text(text):
        return ""
    return f'<div class="arrival-approved-info-card"><div class="arrival-approved-icon" aria-hidden="true">{ICONS[icon]}</div><div><div class="arrival-approved-heading">{escape(title)}</div><div class="arrival-approved-text">{html_text(text)}</div></div></div>'


def build_arrival(html, payload):
    labels = ARRIVAL_LABELS[get_lang(html)]
    checkin = get_content(payload, "checkin_time")
    checkout = get_content(payload, "checkout_time")
    access = get_content(payload, "house_access_public")
    parking = get_content(payload, "parking_info")
    maps = safe_text(get_content(payload, "google_maps_link"))
    cards = arrival_time_card(labels["checkin"], checkin, "door") + arrival_time_card(labels["checkout"], checkout, "bag")
    grid = f'<div class="arrival-approved-time-grid">{cards}</div>' if cards else ""
    details = arrival_info_card(labels["access"], access, "door") + arrival_info_card(labels["parking"], parking, "car")
    maps_btn = ""
    if maps.startswith(("http://", "https://")):
        maps_btn = f'<a class="arrival-approved-map" href="{escape(maps)}" target="_blank" rel="noopener noreferrer"><span aria-hidden="true">{ICONS["map"]}</span><span>{escape(labels["maps"])}</span></a>'
    return f'<section id="arrival-screen" class="screen arrival-screen-approved"><a class="arrival-approved-back" href="#menu-sheet"><span aria-hidden="true">{ICONS["arrow"]}</span><span>{escape(labels["menu"])}</span></a><div class="arrival-approved-ornament" aria-hidden="true">{ICONS["door"]}</div><h2 class="arrival-approved-title">{escape(labels["title"])}</h2><p class="arrival-approved-subtitle">{escape(labels["subtitle"])}</p>{grid}{details}{maps_btn}</section>'

def location_info_card(title, text, icon):
    if not safe_text(text):
        return ""
    return f'<div class="arrival-approved-info-card"><div class="arrival-approved-icon" aria-hidden="true">{ICONS[icon]}</div><div><div class="arrival-approved-heading">{escape(title)}</div><div class="arrival-approved-text">{html_text(text)}</div></div></div>'


def build_location(html, payload):
    labels = LOCATION_LABELS[get_lang(html)]
    address = safe_text(payload.get("property", {}).get("property_address"))
    maps = safe_text(get_content(payload, "google_maps_link"))
    directions = get_content(payload, "directions_text")
    transport = get_content(payload, "transport_options")

    address_card = location_info_card(labels["address"], address, "location")
    directions_card = location_info_card(labels["directions"], directions, "map")
    transport_card = location_info_card(labels["transport"], transport, "car")

    maps_btn = ""
    if maps.startswith(("http://", "https://")):
        maps_btn = f'<a class="arrival-approved-map" href="{escape(maps)}" target="_blank" rel="noopener noreferrer"><span aria-hidden="true">{ICONS["map"]}</span><span>{escape(labels["maps"])}</span></a>'

    return f'<section id="location-screen" class="screen arrival-screen-approved"><a class="arrival-approved-back" href="#menu-sheet"><span aria-hidden="true">{ICONS["arrow"]}</span><span>{escape(labels["menu"])}</span></a><div class="arrival-approved-ornament" aria-hidden="true">{ICONS["location"]}</div><h2 class="arrival-approved-title">{escape(labels["title"])}</h2><p class="arrival-approved-subtitle">{escape(labels["subtitle"])}</p>{address_card}{maps_btn}{directions_card}{transport_card}</section>'

def replace_location(html, payload):
    new_section = build_location(html, payload)
    patterns = [
        r'<section[^>]*id="location-screen"[\s\S]*?</section>',
        r'<section\s+class="screen info-sheet"[\s\S]*?<h2[^>]*>\s*(Location|Ubicación|Emplacement)\s*</h2>[\s\S]*?</section>',
    ]
    for pattern in patterns:
        html, count = re.subn(pattern, new_section, html, count=1, flags=re.IGNORECASE)
        if count:
            return html

    print("Warning: location screen not found; location screen inserted after arrival")
    anchor = r'(<section[^>]*id="arrival-screen"[\s\S]*?</section>)'
    html, count = re.subn(anchor, r'\1' + new_section, html, count=1, flags=re.IGNORECASE)

    if count:
        return html

    return html + new_section

def info_card(title, text, icon):
    if not safe_text(text):
        return ""
    return f'<div class="arrival-approved-info-card"><div class="arrival-approved-icon" aria-hidden="true">{ICONS[icon]}</div><div><div class="arrival-approved-heading">{escape(title)}</div><div class="arrival-approved-text">{html_text(text)}</div></div></div>'


def build_wifi(html, payload):
    labels = INFO_LABELS[get_lang(html)]
    slug = safe_text(payload.get("metadata", {}).get("slug"))
    private_url = f"/guest/{slug}" if slug else "#"
    return f'<section id="wifi-screen" class="screen arrival-screen-approved"><a class="arrival-approved-back" href="#menu-sheet"><span aria-hidden="true">{ICONS["arrow"]}</span><span>{escape(labels["menu"])}</span></a><div class="arrival-approved-ornament" aria-hidden="true">{ICONS["wifi"]}</div><h2 class="arrival-approved-title">{escape(labels["wifi_title"])}</h2><p class="arrival-approved-subtitle">{escape(labels["wifi_subtitle"])}</p>{info_card(labels["wifi_heading"], labels["wifi_text"], "wifi")}<a class="arrival-approved-map" href="{escape(private_url)}"><span aria-hidden="true">{ICONS["wifi"]}</span><span>{escape(labels["wifi_button"])}</span></a></section>'


def build_house_guide(html, payload):
    labels = INFO_LABELS[get_lang(html)]
    amenities = get_content(payload, "amenities_list")
    cards = info_card(labels["amenities"], amenities, "house_guide")
    if not cards:
        return ""
    return f'<section id="house-guide-screen" class="screen arrival-screen-approved"><a class="arrival-approved-back" href="#menu-sheet"><span aria-hidden="true">{ICONS["arrow"]}</span><span>{escape(labels["menu"])}</span></a><div class="arrival-approved-ornament" aria-hidden="true">{ICONS["house_guide"]}</div><h2 class="arrival-approved-title">{escape(labels["guide_title"])}</h2><p class="arrival-approved-subtitle">{escape(labels["guide_subtitle"])}</p>{cards}</section>'


def build_house_rules(html, payload):
    labels = INFO_LABELS[get_lang(html)]
    rules = get_content(payload, "house_rules")
    pet_rules = get_content(payload, "pet_rules")
    cards = info_card(labels["rules"], rules, "house_rules")
    cards += info_card(labels["pets"], pet_rules, "house_rules")
    if not cards:
        return ""
    return f'<section id="house-rules-screen" class="screen arrival-screen-approved"><a class="arrival-approved-back" href="#menu-sheet"><span aria-hidden="true">{ICONS["arrow"]}</span><span>{escape(labels["menu"])}</span></a><div class="arrival-approved-ornament" aria-hidden="true">{ICONS["house_rules"]}</div><h2 class="arrival-approved-title">{escape(labels["rules_title"])}</h2><p class="arrival-approved-subtitle">{escape(labels["rules_subtitle"])}</p>{cards}</section>'


def build_things_to_know(html, payload):
    labels = INFO_LABELS[get_lang(html)]
    things = get_content(payload, "things_to_know")
    cards = info_card(labels["know"], things, "things_to_know")
    if not cards:
        return ""
    return f'<section id="things-to-know-screen" class="screen arrival-screen-approved"><a class="arrival-approved-back" href="#menu-sheet"><span aria-hidden="true">{ICONS["arrow"]}</span><span>{escape(labels["menu"])}</span></a><div class="arrival-approved-ornament" aria-hidden="true">{ICONS["things_to_know"]}</div><h2 class="arrival-approved-title">{escape(labels["know_title"])}</h2><p class="arrival-approved-subtitle">{escape(labels["know_subtitle"])}</p>{cards}</section>'


def replace_or_insert_screen(html, screen_id, new_section, insert_after_id):
    if not new_section:
        return html
    pattern = rf'<section[^>]*id="{screen_id}"[\s\S]*?</section>'
    html, count = re.subn(pattern, new_section, html, count=1, flags=re.IGNORECASE)
    if count:
        return html

    anchor = rf'(<section[^>]*id="{insert_after_id}"[\s\S]*?</section>)'
    html, count = re.subn(anchor, r'\1' + new_section, html, count=1, flags=re.IGNORECASE)
    if count:
        return html

    return html + new_section

def replace_info_screens(html, payload):
    html = replace_or_insert_screen(html, "wifi-screen", build_wifi(html, payload), "location-screen")
    html = replace_or_insert_screen(html, "house-guide-screen", build_house_guide(html, payload), "wifi-screen")
    html = replace_or_insert_screen(html, "house-rules-screen", build_house_rules(html, payload), "house-guide-screen")
    html = replace_or_insert_screen(html, "things-to-know-screen", build_things_to_know(html, payload), "house-rules-screen")
    return html

def replace_menu(html):
    pattern = r'<section\s+id="menu-sheet"\s+class="screen menu-card"[\s\S]*?</section>'
    return re.sub(pattern, build_menu(html), html, count=1)

def replace_arrival(html, payload):
    new_section = build_arrival(html, payload)
    # The current 4th screen generated by the old template is Amenities/House Guide.
    patterns = [
        r'<section[^>]*id="amenities-screen"[\s\S]*?</section>',
        r'<section\s+class="screen list-sheet"[\s\S]*?<h2[^>]*>\s*(Amenities|Amenidades|Équipements)\s*</h2>[\s\S]*?</section>',
        r'<section\s+class="screen info-sheet"[\s\S]*?<h2[^>]*>\s*(Amenities|Amenidades|Équipements)\s*</h2>[\s\S]*?</section>',
    ]
    for pattern in patterns:
        html, count = re.subn(pattern, new_section, html, count=1, flags=re.IGNORECASE)
        if count:
            return html
    # Fallback: insert after menu if old amenities selector changes.
    print("Warning: amenities screen not found; arrival screen inserted after menu")
    return html.replace('</section>', '</section>' + new_section, 2)


def patch_welcome_image(html):
    replacement = f'<div class="welcome-image"><img src="{WELCOME_IMG}" alt="Welcome" loading="eager"></div>'
    return re.sub(r'<div\s+class="welcome-image">[\s\S]*?</div>', replacement, html, count=1)


def inject_css(html):
    if CSS_MARKER in html:
        return html
    if "</style>" not in html:
        print("Warning: </style> not found; CSS was not injected")
        return html
    return html.replace("</style>", CSS + "\n</style>", 1)

def inject(html, payload):
    html = replace_menu(html)
    html = replace_arrival(html, payload)
    html = replace_location(html, payload)
    html = replace_info_screens(html, payload)
    html = patch_welcome_image(html)
    html = inject_css(html)
    return html

def main():
    payload = json.loads(sys.argv[1])
    slug = payload.get("metadata", {}).get("slug") or "demo"
    villa_dir = Path("public") / "villas" / slug
    if not villa_dir.exists():
        raise SystemExit(f"Villa directory not found: {villa_dir}")
    for file in villa_dir.glob("*.html"):
        file.write_text(inject(file.read_text(encoding="utf-8"), payload), encoding="utf-8")
        print(f"Postprocessed {file}")


if __name__ == "__main__":
    main()
