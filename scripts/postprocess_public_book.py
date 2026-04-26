import json
import sys
from pathlib import Path

CSS_MARKER = "/* MyGuest Bloque 12 visual QA */"
JS_MARKER = "// MyGuest Bloque 12 visual QA"
WELCOME_IMG = "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&q=80"

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
body,.welcome-message,.menu-label,.paragraph,.info-value,.info-row,.card,.section-title,.arrival-time,.arrival-detail-text,.list-item-text,.rule-text {{ color:var(--myguest-deep-text)!important; }}
.screen:not(.cover-screen) {{ min-height:var(--myguest-screen-h)!important;display:flex!important;align-items:center!important;justify-content:center!important; }}
.screen:not(.cover-screen)>* {{ width:100%!important;max-height:var(--myguest-screen-h)!important;overflow-y:auto!important;scrollbar-width:none!important; }}
.screen:not(.cover-screen)>*::-webkit-scrollbar {{ display:none!important; }}
.welcome-card .arrival-grid,.welcome-card .welcome-divider {{ display:none!important; }}
.welcome-card {{ padding-top:clamp(20px,5vw,28px)!important;padding-bottom:clamp(20px,5vw,28px)!important; }}
.welcome-image {{ display:block!important;min-height:190px!important;max-height:260px!important;background:linear-gradient(180deg,#F7F0E8,#E7D8C7)!important; }}
.welcome-image img {{ display:block!important;width:100%!important;height:clamp(190px,36svh,260px)!important;object-fit:cover!important; }}
.menu-card {{ padding:18px 14px!important; }}
.menu-script-title {{ font-size:clamp(48px,13vw,62px)!important;margin-bottom:10px!important; }}
.menu-subtitle {{ font-size:clamp(16px,4.6vw,22px)!important;line-height:1.05!important;margin-bottom:16px!important; }}
.menu-grid {{ grid-template-columns:repeat(3,minmax(0,1fr))!important;column-gap:10px!important;row-gap:10px!important; }}
.menu-tile {{ background:var(--myguest-tile)!important;border:1px solid var(--myguest-border)!important;border-radius:20px!important;margin-bottom:7px!important;box-shadow:0 5px 14px rgba(58,42,28,.05)!important; }}
.menu-icon {{ width:clamp(48px,14vw,62px)!important;height:clamp(48px,14vw,62px)!important;color:var(--myguest-icon)!important; }}
.menu-icon svg,.welcome-action svg,.arrival-detail-icon svg,.info-row-icon svg,.list-item-icon svg,.wifi-center-icon svg {{ fill:none!important;stroke:currentColor!important;stroke-width:1.75!important;stroke-linecap:round!important;stroke-linejoin:round!important; }}
.menu-label {{ font-size:clamp(10px,2.75vw,12px)!important;line-height:1.12!important;color:var(--myguest-deep-text)!important;font-weight:600!important; }}
.myguest-menu-hidden {{ display:none!important; }}
.welcome-action,.info-row-icon,.arrival-detail-icon,.list-item-icon,.wifi-center-icon {{ color:var(--myguest-icon)!important; }}
"""

JS = f"""
<script>
{JS_MARKER}
(function(){{
  const imgUrl={json.dumps(WELCOME_IMG)};
  const icons={{
    arrival:'<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="24"></circle><path d="M32 18v15l10 7"></path></svg>',
    location:'<svg viewBox="0 0 64 64"><path d="M32 56s18-15.2 18-31a18 18 0 0 0-36 0c0 15.8 18 31 18 31Z"></path><circle cx="32" cy="25" r="6"></circle></svg>',
    wifi:'<svg viewBox="0 0 64 64"><path d="M12 27a31 31 0 0 1 40 0"></path><path d="M21 37a18 18 0 0 1 22 0"></path><path d="M29 47a6 6 0 0 1 6 0"></path><circle cx="32" cy="51" r="2.5"></circle></svg>',
    houseGuide:'<svg viewBox="0 0 64 64"><path d="M12 30 32 13l20 17"></path><path d="M18 28v25h28V28"></path><path d="M26 53V38h12v15"></path></svg>',
    rules:'<svg viewBox="0 0 64 64"><rect x="16" y="10" width="32" height="44" rx="4"></rect><path d="M24 24h16M24 34h16M24 44h10"></path></svg>',
    info:'<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="24"></circle><path d="M32 29v16"></path><circle cx="32" cy="21" r="2.5"></circle></svg>',
    sun:'<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="12"></circle><path d="M32 8v10M32 46v10M8 32h10M46 32h10M15 15l7 7M42 42l7 7M49 15l-7 7M22 42l-7 7"></path></svg>',
    eat:'<svg viewBox="0 0 64 64"><path d="M20 9v22M13 9v18c0 5 3 8 7 8s7-3 7-8V9M20 35v20"></path><path d="M45 9c6 8 6 20 0 27v19"></path></svg>',
    drink:'<svg viewBox="0 0 64 64"><path d="M18 11h28l-5 24a9 9 0 0 1-18 0Z"></path><path d="M32 44v11M24 55h16"></path></svg>',
    directory:'<svg viewBox="0 0 64 64"><rect x="17" y="11" width="30" height="42" rx="4"></rect><path d="M25 23h14M25 33h14M25 43h9"></path><path d="M47 20h4M47 30h4M47 40h4"></path></svg>',
    emergency:'<svg viewBox="0 0 64 64"><path d="M25 11h14v14h14v14H39v14H25V39H11V25h14Z"></path></svg>',
    contact:'<svg viewBox="0 0 64 64"><rect x="10" y="17" width="44" height="30" rx="4"></rect><path d="M12 21l20 15 20-15"></path></svg>',
    leave:'<svg viewBox="0 0 64 64"><rect x="16" y="20" width="32" height="30" rx="4"></rect><path d="M24 20v-7h16v7M16 31h32"></path></svg>',
    review:'<svg viewBox="0 0 64 64"><path d="M13 15h38v28H25L14 52v-9h-1Z"></path><path d="M24 28h17M24 36h11"></path></svg>'
  }};
  const labels={{
    en:{{arrival:'Arrival',location:'Location',wifi:'WiFi',houseGuide:'House Guide',rules:'House Rules',info:'Things to Know',sun:'Things to Do',eat:'Places to Eat',drink:'Places to Drink',directory:'Local Directory',emergency:'Emergency',contact:'Contact Me',leave:'Before You Leave',review:'Review'}},
    es:{{arrival:'Llegada',location:'Ubicación',wifi:'WiFi',houseGuide:'Guía de la Casa',rules:'Reglas de la Casa',info:'Información Importante',sun:'Qué Hacer',eat:'Dónde Comer',drink:'Dónde Tomar Algo',directory:'Directorio Local',emergency:'Emergencias',contact:'Contáctame',leave:'Antes de Salir',review:'Reseña'}},
    fr:{{arrival:'Arrivée',location:'Emplacement',wifi:'WiFi',houseGuide:'Guide de la Maison',rules:'Règles de la Maison',info:'À Savoir',sun:'Activités',eat:'Où Manger',drink:'Où Boire',directory:'Répertoire Local',emergency:'Urgence',contact:'Me Contacter',leave:'Avant le Départ',review:'Avis'}}
  }};
  const order=['arrival','location','wifi','houseGuide','rules','info','sun','eat','drink','directory','emergency','contact','leave','review'];
  function lang(){{let v=(document.documentElement.lang||'en').toLowerCase();return v.startsWith('es')?'es':v.startsWith('fr')?'fr':'en';}}
  function norm(t){{return (t||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/\s+/g,' ').trim();}}
  function kind(t){{t=norm(t);if(t.includes('transport'))return 'transport';if(t.includes('check')||t.includes('llegada / salida')||t.includes('arrivee'))return 'arrival';if(t.includes('direction')||t.includes('como llegar')||t.includes('itineraire'))return 'location';if(t.includes('wifi'))return 'wifi';if(t.includes('amenit')||t.includes('amenidad')||t.includes('equipement'))return 'houseGuide';if(t.includes('rule')||t.includes('regla')||t.includes('regle'))return 'rules';if(t.includes('things to know')||t.includes('informacion importante')||t.includes('information'))return 'info';if(t.includes('things to do')||t.includes('que hacer')||t.includes('activit'))return 'sun';if(t.includes('eat')||t.includes('comer')||t.includes('manger'))return 'eat';if(t.includes('drink')||t.includes('tomar')||t.includes('boire'))return 'drink';if(t.includes('directory')||t.includes('directorio')||t.includes('repertoire'))return 'directory';if(t.includes('emergency')||t.includes('emergencia')||t.includes('urgence'))return 'emergency';if(t.includes('before')||t.includes('antes')||t.includes('avant'))return 'leave';if(t.includes('review')||t.includes('resena')||t.includes('avis'))return 'review';if(t.includes('contact'))return 'contact';return null;}}
  function patchWelcome(){{let w=document.querySelector('.welcome-image');if(!w)return;let i=w.querySelector('img')||document.createElement('img');i.src=imgUrl;i.alt='Welcome';i.loading='eager';if(!i.parentNode)w.appendChild(i);}}
  function patchMenu(){{let g=document.querySelector('.menu-grid');if(!g)return;let rows=Array.from(g.querySelectorAll('.menu-item'));rows.forEach(el=>{{let lab=el.querySelector('.menu-label'),k=kind(lab?lab.textContent:el.textContent);if(!k)return;if(k==='transport'){{el.classList.add('myguest-menu-hidden');return;}}el.dataset.myguestKind=k;if(lab)lab.textContent=labels[lang()][k];let ic=el.querySelector('.menu-icon');if(ic&&icons[k])ic.innerHTML=icons[k];}});rows.filter(el=>!el.classList.contains('myguest-menu-hidden')).sort((a,b)=>order.indexOf(a.dataset.myguestKind)-order.indexOf(b.dataset.myguestKind)).forEach(el=>g.appendChild(el));}}
  patchWelcome();patchMenu();
}})();
</script>
"""


def inject(html: str) -> str:
    if CSS_MARKER not in html:
        html = html.replace("</style>", CSS + "\n</style>", 1)
    if JS_MARKER not in html:
        html = html.replace("</body>", JS + "\n</body>", 1)
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
