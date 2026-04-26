import json
import re
import sys
from pathlib import Path

CSS_MARKER = "/* MyGuest Bloque 12 approved premium menu */"
WELCOME_IMG = "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&q=80"

APPROVED_MENU_CSS = f"""
{CSS_MARKER}
:root {{
  --myguest-deep-text:#3A2A1C;
  --myguest-muted-text:#5B4635;
  --myguest-icon:#7A624C;
  --myguest-tile:#F4EEE6;
  --myguest-border:#DDCFC0;
  --myguest-screen-h:calc(100svh - 92px);
}}
body,.welcome-message,.menu-label,.paragraph,.info-value,.info-row,.card,.section-title,.arrival-time,.arrival-detail-text,.list-item-text,.rule-text {{
  color:var(--myguest-deep-text)!important;
}}
.screen:not(.cover-screen) {{
  min-height:var(--myguest-screen-h)!important;
}}
.welcome-card .arrival-grid,.welcome-card .welcome-divider,.welcome-card .welcome-actions,.welcome-card .welcome-signoff,.welcome-card .welcome-eyebrow {{
  display:none!important;
}}
.welcome-card {{
  padding-top:clamp(20px,5vw,28px)!important;
  padding-bottom:clamp(20px,5vw,28px)!important;
}}
.welcome-image {{
  display:block!important;
  min-height:190px!important;
  max-height:260px!important;
  background:linear-gradient(180deg,#F7F0E8,#E7D8C7)!important;
  border-radius:8px!important;
}}
.welcome-image img {{
  display:block!important;
  width:100%!important;
  height:clamp(190px,36svh,260px)!important;
  object-fit:cover!important;
  border-radius:8px!important;
}}
.menu-screen-approved {{
  min-height:var(--myguest-screen-h)!important;
  background:radial-gradient(circle at 85% 6%, rgba(216,206,186,.36), transparent 34%),linear-gradient(180deg,rgba(255,255,255,.78),rgba(255,250,244,.92))!important;
  border:1px solid rgba(138,112,74,.14)!important;
  border-radius:34px!important;
  box-shadow:0 18px 42px rgba(58,42,28,.08)!important;
  padding:18px 16px 22px!important;
}}
.menu-screen-approved .menu-kicker {{
  font-family:'Cormorant Garamond',serif!important;
  font-size:clamp(14px,3.6vw,18px)!important;
  line-height:1!important;
  letter-spacing:.34em!important;
  text-transform:uppercase!important;
  color:var(--primary)!important;
  text-align:center!important;
  margin-bottom:2px!important;
  opacity:.9!important;
}}
.menu-screen-approved .menu-script-title {{
  font-family:'Great Vibes',cursive!important;
  font-size:clamp(54px,16vw,76px)!important;
  line-height:.9!important;
  color:var(--primary)!important;
  text-align:center!important;
  margin:0 0 8px!important;
  font-weight:400!important;
}}
.menu-screen-approved .menu-subtitle {{
  font-family:'Cormorant Garamond',serif!important;
  font-size:clamp(18px,5vw,25px)!important;
  line-height:1.12!important;
  letter-spacing:.08em!important;
  color:var(--primary)!important;
  text-align:center!important;
  text-transform:none!important;
  margin:0 auto 18px!important;
  max-width:92%!important;
}}
.menu-grid-approved {{
  display:grid!important;
  grid-template-columns:repeat(3,minmax(0,1fr))!important;
  column-gap:10px!important;
  row-gap:12px!important;
  align-items:stretch!important;
}}
.menu-screen-approved .menu-link {{
  display:flex!important;
  flex-direction:column!important;
  align-items:center!important;
  justify-content:flex-start!important;
  min-width:0!important;
  text-decoration:none!important;
  color:var(--text)!important;
  -webkit-tap-highlight-color:transparent!important;
}}
.menu-screen-approved .menu-tile {{
  width:100%!important;
  aspect-ratio:1.05/.88!important;
  border-radius:21px!important;
  background:linear-gradient(180deg,rgba(255,255,255,.94),rgba(252,247,240,.92))!important;
  border:1px solid rgba(138,112,74,.20)!important;
  box-shadow:0 9px 22px rgba(58,42,28,.07),inset 0 1px 0 rgba(255,255,255,.9)!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  margin-bottom:6px!important;
}}
.menu-screen-approved .menu-icon {{
  width:clamp(31px,9vw,42px)!important;
  height:clamp(31px,9vw,42px)!important;
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  color:var(--primary)!important;
}}
.menu-screen-approved .menu-icon svg {{
  width:100%!important;
  height:100%!important;
  stroke:currentColor!important;
  fill:none!important;
  stroke-width:1.75!important;
  stroke-linecap:round!important;
  stroke-linejoin:round!important;
}}
.menu-screen-approved .menu-label {{
  font-family:'Cormorant Garamond',serif!important;
  font-size:clamp(14px,3.7vw,17px)!important;
  line-height:1.05!important;
  color:var(--myguest-deep-text)!important;
  font-weight:500!important;
  text-align:center!important;
  min-height:32px!important;
  display:flex!important;
  align-items:flex-start!important;
  justify-content:center!important;
}}
.menu-screen-approved .menu-item-wide-left {{
  grid-column:1 / 2!important;
  transform:translateX(56%)!important;
}}
.menu-screen-approved .menu-item-wide-right {{
  grid-column:3 / 4!important;
  transform:translateX(-56%)!important;
}}
@media (max-width:380px) {{
  .menu-screen-approved {{ padding:16px 12px 20px!important; }}
  .menu-grid-approved {{ column-gap:8px!important;row-gap:10px!important; }}
  .menu-screen-approved .menu-tile {{ border-radius:18px!important;margin-bottom:5px!important; }}
  .menu-screen-approved .menu-label {{ font-size:clamp(12px,3.5vw,15px)!important;min-height:30px!important; }}
  .menu-screen-approved .menu-script-title {{ font-size:clamp(48px,15vw,66px)!important; }}
  .menu-screen-approved .menu-subtitle {{ margin-bottom:14px!important; }}
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
}

MENU_LABELS = {
    "en": {
        "kicker": "Your Guide",
        "title": "Your Guide",
        "subtitle": "Everything you need for a perfect stay",
        "arrival": "Arrival",
        "location": "Location",
        "wifi": "WiFi",
        "house_guide": "House Guide",
        "house_rules": "House Rules",
        "things_to_know": "Things to Know",
        "things_to_do": "Things to Do",
        "places_to_eat": "Places to Eat",
        "places_to_drink": "Places to Drink",
        "local_directory": "Local Directory",
        "emergency": "Emergency",
        "contact": "Contact Me",
        "before_leave": "Before You Leave",
        "review": "Review",
    },
    "es": {
        "kicker": "Tu Guía",
        "title": "Tu Guía",
        "subtitle": "Todo lo que necesitas para una estancia perfecta",
        "arrival": "Llegada",
        "location": "Ubicación",
        "wifi": "WiFi",
        "house_guide": "Guía de la Casa",
        "house_rules": "Reglas de la Casa",
        "things_to_know": "Información Importante",
        "things_to_do": "Qué Hacer",
        "places_to_eat": "Dónde Comer",
        "places_to_drink": "Dónde Tomar Algo",
        "local_directory": "Directorio Local",
        "emergency": "Emergencias",
        "contact": "Contáctame",
        "before_leave": "Antes de Salir",
        "review": "Reseña",
    },
    "fr": {
        "kicker": "Votre Guide",
        "title": "Votre Guide",
        "subtitle": "Tout ce dont vous avez besoin pour un séjour parfait",
        "arrival": "Arrivée",
        "location": "Emplacement",
        "wifi": "WiFi",
        "house_guide": "Guide de la Maison",
        "house_rules": "Règles de la Maison",
        "things_to_know": "À Savoir",
        "things_to_do": "Activités",
        "places_to_eat": "Où Manger",
        "places_to_drink": "Où Boire",
        "local_directory": "Répertoire Local",
        "emergency": "Urgence",
        "contact": "Me Contacter",
        "before_leave": "Avant le Départ",
        "review": "Avis",
    },
}

MENU_ITEMS = [
    ("arrival", "#arrival-screen", ""),
    ("location", "#location-screen", ""),
    ("wifi", "#wifi-screen", ""),
    ("house_guide", "#house-guide-screen", ""),
    ("house_rules", "#house-rules-screen", ""),
    ("things_to_know", "#things-to-know-screen", ""),
    ("things_to_do", "#things-to-do-screen", ""),
    ("places_to_eat", "#places-to-eat-screen", ""),
    ("places_to_drink", "#places-to-drink-screen", ""),
    ("local_directory", "#local-directory-screen", ""),
    ("emergency", "#emergency-screen", ""),
    ("contact", "#contact-screen", ""),
    ("before_leave", "#before-you-leave-screen", "menu-item-wide-left"),
    ("review", "#review-screen", "menu-item-wide-right"),
]


def get_lang(html: str) -> str:
    match = re.search(r'<html[^>]*lang="([^"]+)"', html, flags=re.IGNORECASE)
    raw = (match.group(1).lower() if match else "en")
    if raw.startswith("es"):
        return "es"
    if raw.startswith("fr"):
        return "fr"
    return "en"


def menu_item_html(key: str, href: str, extra_class: str, labels: dict) -> str:
    return f'''
        <a class="menu-item menu-link {extra_class}" href="{href}">
            <span class="menu-tile">
                <span class="menu-icon" aria-hidden="true">{ICONS[key]}</span>
            </span>
            <span class="menu-label">{labels[key]}</span>
        </a>
    '''


def build_menu(html: str) -> str:
    labels = MENU_LABELS[get_lang(html)]
    items = "\n".join(menu_item_html(key, href, extra_class, labels) for key, href, extra_class in MENU_ITEMS)
    return f'''
<section id="menu-sheet" class="screen menu-card menu-screen-approved">
    <div class="menu-kicker">{labels["kicker"]}</div>
    <h2 class="menu-script-title">{labels["title"]}</h2>
    <p class="menu-subtitle">{labels["subtitle"]}</p>
    <div class="menu-grid menu-grid-approved">
        {items}
    </div>
</section>
'''


def replace_menu(html: str) -> str:
    pattern = r'<section\s+id="menu-sheet"\s+class="screen menu-card"[\s\S]*?</section>'
    replacement = build_menu(html)
    new_html, count = re.subn(pattern, replacement, html, count=1)
    if count == 0:
        print("Warning: menu-sheet section was not found; menu was not replaced")
        return html
    return new_html


def patch_welcome_image(html: str) -> str:
    replacement = f'<div class="welcome-image"><img src="{WELCOME_IMG}" alt="Welcome" loading="eager"></div>'
    pattern = r'<div\s+class="welcome-image">[\s\S]*?</div>'
    return re.sub(pattern, replacement, html, count=1)


def inject_css(html: str) -> str:
    if CSS_MARKER in html:
        return html
    if "</style>" not in html:
        print("Warning: </style> not found; approved menu CSS was not injected")
        return html
    return html.replace("</style>", APPROVED_MENU_CSS + "\n</style>", 1)


def inject(html: str) -> str:
    html = replace_menu(html)
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
        file.write_text(inject(file.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"Postprocessed {file}")


if __name__ == "__main__":
    main()
