#!/usr/bin/env python3
"""Generates the City style demo: The SoHo Loft, New York."""
import sys
import os
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
os.chdir(project_root)
sys.path.insert(0, script_dir)

PAYLOAD = {
    "metadata": {
        "slug": "the-soho-loft",
    },
    "property": {
        "property_name": "The SoHo Loft",
        "property_address": "285 Spring Street, New York, NY 10013",
        "style": "Minimalist",
        "property_environment": "City",
        "primary_language": "English",
    },
    "content": {
        "demo_mode": True,
        "wifi_ssid": "SoHoLoft_Guest",
        "wifi_password": "WelcomeNYC2024",
        "house_access_private": (
            "Building entrance code: *1847. "
            "Take elevator to floor 4 — apartment 4B. "
            "Lockbox next to the door — code: 3829. "
            "Return keys to lockbox on checkout."
        ),
        "host_phone": "+1 (212) 555-0198",
        "about_house": {
            "welcome_message": (
                "Welcome to The SoHo Loft — a sleek, light-filled space in one of "
                "New York's most iconic neighbourhoods. We hope this guide helps you "
                "make the most of your stay. Don't hesitate to reach out if you need "
                "anything at all."
            ),
            "about_hosts": (
                "Your stay is hosted by The SoHo Loft Team, New Yorkers who believe "
                "great design and great hospitality go hand in hand. We are available "
                "by email and typically reply within a few hours."
            ),
            "amenities_list": (
                "High-speed fiber WiFi\n"
                "Smart TV with Netflix & Apple TV\n"
                "Espresso machine & pour-over coffee kit\n"
                "Fully equipped kitchen\n"
                "Central air conditioning & heating\n"
                "In-unit washer & dryer\n"
                "Designer linens & towels\n"
                "Work desk with natural light\n"
                "Floor-to-ceiling windows with city views\n"
                "Keypad entry — no physical key needed"
            ),
            "pet_friendly": False,
        },
        "checkin": {
            "checkin_time": "3:00 PM",
            "checkout_time": "11:00 AM",
            "house_access_public": (
                "Detailed access instructions will be sent privately before check-in."
            ),
            "parking_info": (
                "Street parking in SoHo is very limited. "
                "Nearest parking garage: SP+ at 505 Canal St — approx. $35–50/day. "
                "We strongly recommend arriving by subway, taxi, or rideshare."
            ),
        },
        "location_transport": {
            "google_maps_link": (
                "https://maps.google.com/?q=285+Spring+Street+New+York+NY+10013"
            ),
            "directions_text": (
                "Located in the heart of SoHo, one block from the C/E subway at Spring St. "
                "From JFK Airport: take the AirTrain to Jamaica, then the E train to "
                "Spring St — approximately 55 minutes. "
                "From Newark Airport: NJ Transit to Penn Station, then the C or E to Spring St."
            ),
            "transport_options": (
                "Subway: C/E at Spring St (1 block away) and 1 at Houston St (4 blocks). "
                "Citi Bike stations are on every other block throughout SoHo. "
                "Taxis and rideshares are abundant 24/7."
            ),
        },
        "rules_info": {
            "things_to_know": (
                "The elevator requires a key fob — yours is in the lockbox with the apartment key.\n"
                "Trash and recycling room is at the end of the 4th floor hallway.\n"
                "Building laundry is also available in the basement (coin-operated).\n"
                "The apartment faces south — afternoon light is beautiful but can be bright; "
                "blackout blinds are on every window."
            ),
            "house_rules": (
                "No smoking anywhere in the building.\n"
                "Maximum 2 guests at all times.\n"
                "Please keep noise levels respectful after 10 PM — walls are thin.\n"
                "No parties or events.\n"
                "Shoes off at the entrance — there's a mat and shelf by the door."
            ),
            "before_you_leave": (
                "Strip used bedding and leave it on the floor by the bed.\n"
                "Leave used towels in the bathtub.\n"
                "Empty the fridge of any opened food items.\n"
                "Turn off all lights and appliances.\n"
                "Return keys to the lockbox and close the apartment door firmly."
            ),
        },
        "recommendations": {
            "property_environment": "City",
            "restaurant_1_name": "Raoul's",
            "restaurant_1_maps_link": "https://maps.google.com/?q=180+Prince+St+New+York+NY+10012",
            "restaurant_1_description": (
                "A SoHo legend since 1975. Dark, romantic French bistro with "
                "outstanding steak au poivre. Reservations essential."
            ),
            "restaurant_2_name": "Charlie Bird",
            "restaurant_2_maps_link": "https://maps.google.com/?q=5+King+St+New+York+NY+10012",
            "restaurant_2_description": (
                "Vibrant Italian-American spot with excellent pasta and natural wines. "
                "Walk-in bar seating is often available at the counter."
            ),
            "restaurant_3_name": "Estela",
            "restaurant_3_maps_link": "https://maps.google.com/?q=47+E+Houston+St+New+York+NY+10012",
            "restaurant_3_description": (
                "One of NYC's most celebrated restaurants — refined small plates "
                "with unexpected flavour combinations. Book well in advance."
            ),
            "bar_1_name": "Fanelli Cafe",
            "bar_1_maps_link": "https://maps.google.com/?q=94+Prince+St+New+York+NY+10012",
            "bar_1_description": (
                "The oldest bar in SoHo, open since 1847. No frills, cold beer, "
                "great burgers — a New York institution."
            ),
            "bar_2_name": "The Ear Inn",
            "bar_2_maps_link": "https://maps.google.com/?q=326+Spring+St+New+York+NY+10013",
            "bar_2_description": (
                "One of the oldest bars in New York City, steps from the apartment. "
                "Cozy and unpretentious — locals love it."
            ),
            "activity_1_name": "SoHo Gallery Walk",
            "activity_1_link": "https://maps.google.com/?q=SoHo+Art+Galleries+New+York+NY",
            "activity_1_description": (
                "The neighbourhood is packed with world-class art galleries. "
                "Start on West Broadway and wander — most are free to enter."
            ),
            "activity_2_name": "The High Line",
            "activity_2_link": "https://thehighline.org",
            "activity_2_description": (
                "Elevated park built on a former railway — 1.5 miles of art, gardens, "
                "and stunning city views. Free entry, 10 minutes by subway."
            ),
            "activity_3_name": "Whitney Museum of American Art",
            "activity_3_link": "https://whitney.org",
            "activity_3_description": (
                "World-class collection of 20th and 21st century American art, "
                "housed in a striking Renzo Piano building in the Meatpacking District."
            ),
            "local_directory": (
                "Nearest Whole Foods: 270 Greenwich St (10 min walk)\n"
                "Nearest pharmacy (CVS): 180 W Houston St\n"
                "NYU Langone Health: +1 (212) 263-7300"
            ),
        },
        "contact_social": {
            "host_email": "hello@thesoholoft.com",
            "emergency_contacts": (
                "Emergency: 911\n"
                "NYC non-emergency: 311\n"
                "Host team: hello@thesoholoft.com"
            ),
            "airbnb_review_link": "https://airbnb.com/",
            "instagram_handle": "@thesoholoft.nyc",
        },
    },
}

PRE_TRANSLATIONS = {
    "Español": {
        "welcome_message": (
            "Bienvenido a The SoHo Loft — un espacio elegante y luminoso en uno de "
            "los barrios más icónicos de Nueva York. Esperamos que esta guía te ayude "
            "a aprovechar al máximo tu estadía. No dudes en contactarnos si necesitas "
            "cualquier cosa."
        ),
        "about_hosts": (
            "Tu estadía es gestionada por The SoHo Loft Team, neoyorquinos que creen "
            "que el gran diseño y la gran hospitalidad van de la mano. Estamos "
            "disponibles por correo electrónico y solemos responder en pocas horas."
        ),
        "house_access_private": (
            "Código de entrada al edificio: *1847. "
            "Toma el ascensor hasta el piso 4 — apartamento 4B. "
            "Caja de seguridad junto a la puerta — código: 3829. "
            "Devuelve las llaves a la caja de seguridad al hacer el checkout."
        ),
        "house_access_public": (
            "Las instrucciones detalladas de acceso se enviarán de forma privada "
            "antes del check-in."
        ),
        "parking_info": (
            "El estacionamiento en SoHo es muy limitado. "
            "Garaje más cercano: SP+ en 505 Canal St — aprox. $35–50/día. "
            "Recomendamos llegar en metro, taxi o transporte compartido."
        ),
        "directions_text": (
            "Ubicado en el corazón de SoHo, a una cuadra del metro C/E en Spring St. "
            "Desde el aeropuerto JFK: toma el AirTrain hasta Jamaica, luego el tren E "
            "hasta Spring St — aproximadamente 55 minutos. "
            "Desde Newark: NJ Transit hasta Penn Station, luego C o E hasta Spring St."
        ),
        "transport_options": (
            "Metro: C/E en Spring St (a 1 cuadra) y línea 1 en Houston St (a 4 cuadras). "
            "Estaciones de Citi Bike en cada otra cuadra de SoHo. "
            "Taxis y transporte compartido disponibles las 24 horas."
        ),
        "things_to_know": (
            "El ascensor requiere un llavero — está en la caja de seguridad con la llave.\n"
            "Cuarto de basura y reciclaje al final del pasillo del piso 4.\n"
            "Lavandería del edificio en el sótano (monedas).\n"
            "El apartamento da al sur — la luz de tarde es hermosa pero intensa; "
            "todas las ventanas tienen persianas blackout."
        ),
        "house_rules": (
            "Prohibido fumar en cualquier parte del edificio.\n"
            "Máximo 2 huéspedes en todo momento.\n"
            "Por favor mantén el ruido bajo después de las 10 PM — las paredes son delgadas.\n"
            "Prohibidas las fiestas o eventos.\n"
            "Quítate los zapatos en la entrada — hay una alfombra y estante junto a la puerta."
        ),
        "before_you_leave": (
            "Retira la ropa de cama usada y déjala en el suelo junto a la cama.\n"
            "Deja las toallas usadas en la bañera.\n"
            "Vacía el refrigerador de los alimentos abiertos.\n"
            "Apaga todas las luces y electrodomésticos.\n"
            "Devuelve las llaves a la caja de seguridad y cierra bien la puerta."
        ),
        "restaurant_1_description": (
            "Una leyenda de SoHo desde 1975. Bistro francés oscuro y romántico con "
            "un excelente steak au poivre. Reservaciones esenciales."
        ),
        "restaurant_2_description": (
            "Animado restaurante italoamericano con excelente pasta y vinos naturales. "
            "Suele haber lugares en la barra sin reservación."
        ),
        "restaurant_3_description": (
            "Uno de los restaurantes más celebrados de NYC — platos pequeños refinados "
            "con combinaciones de sabores inesperadas. Reserva con mucha antelación."
        ),
        "bar_1_description": (
            "El bar más antiguo de SoHo, abierto desde 1847. Sin pretensiones, "
            "cerveza fría y grandes hamburguesas — una institución de Nueva York."
        ),
        "bar_2_description": (
            "Uno de los bares más antiguos de Nueva York, a pasos del apartamento. "
            "Acogedor y sin pretensiones — los locales lo adoran."
        ),
        "activity_1_description": (
            "El barrio está lleno de galerías de arte de primer nivel. "
            "Empieza en West Broadway y camina — la mayoría tienen entrada gratuita."
        ),
        "activity_2_description": (
            "Parque elevado construido sobre una vía de tren — 2.4 km de arte, jardines "
            "y vistas espectaculares de la ciudad. Entrada gratuita, a 10 min en metro."
        ),
        "activity_3_description": (
            "Colección de arte americano del siglo XX y XXI de fama mundial, "
            "alojada en un impresionante edificio de Renzo Piano en el Meatpacking District."
        ),
        "local_directory": (
            "Whole Foods más cercano: 270 Greenwich St (10 min a pie)\n"
            "Farmacia CVS más cercana: 180 W Houston St\n"
            "NYU Langone Health: +1 (212) 263-7300"
        ),
        "emergency_contacts": (
            "Emergencias: 911\n"
            "NYC no urgente: 311\n"
            "Equipo anfitrión: hello@thesoholoft.com"
        ),
    },
    "Français": {
        "welcome_message": (
            "Bienvenue au SoHo Loft — un espace épuré et lumineux au cœur de l'un "
            "des quartiers les plus emblématiques de New York. Nous espérons que ce "
            "guide vous aidera à profiter pleinement de votre séjour. N'hésitez pas "
            "à nous contacter si vous avez besoin de quoi que ce soit."
        ),
        "about_hosts": (
            "Votre séjour est pris en charge par The SoHo Loft Team, des New-Yorkais "
            "convaincus que design et hospitalité vont de pair. Nous sommes disponibles "
            "par e-mail et répondons généralement en quelques heures."
        ),
        "house_access_private": (
            "Code d'entrée du bâtiment : *1847. "
            "Prenez l'ascenseur jusqu'au 4e étage — appartement 4B. "
            "Boîte à clés à côté de la porte — code : 3829. "
            "Remettez les clés dans la boîte à clés au départ."
        ),
        "house_access_public": (
            "Les instructions d'accès détaillées seront envoyées de façon privée "
            "avant le check-in."
        ),
        "parking_info": (
            "Le stationnement à SoHo est très limité. "
            "Parking le plus proche : SP+ au 505 Canal St — environ 35–50 $/jour. "
            "Nous recommandons vivement d'arriver en métro, taxi ou VTC."
        ),
        "directions_text": (
            "Situé au cœur de SoHo, à un pâté de maisons du métro C/E à Spring St. "
            "Depuis JFK : prenez l'AirTrain jusqu'à Jamaica, puis le train E jusqu'à "
            "Spring St — environ 55 minutes. "
            "Depuis Newark : NJ Transit jusqu'à Penn Station, puis C ou E jusqu'à Spring St."
        ),
        "transport_options": (
            "Métro : C/E à Spring St (1 bloc) et ligne 1 à Houston St (4 blocs). "
            "Stations Citi Bike disponibles dans tout SoHo. "
            "Taxis et VTC disponibles 24h/24."
        ),
        "things_to_know": (
            "L'ascenseur nécessite un badge — il se trouve dans la boîte à clés avec la clé.\n"
            "Local poubelles et recyclage au bout du couloir du 4e étage.\n"
            "Laverie de l'immeuble au sous-sol (pièces de monnaie).\n"
            "L'appartement est orienté sud — la lumière de l'après-midi est magnifique "
            "mais intense ; des stores occultants équipent toutes les fenêtres."
        ),
        "house_rules": (
            "Il est interdit de fumer partout dans l'immeuble.\n"
            "Maximum 2 personnes à tout moment.\n"
            "Veuillez limiter le bruit après 22h — les murs sont minces.\n"
            "Fêtes et événements interdits.\n"
            "Chaussures à enlever à l'entrée — tapis et étagère disponibles près de la porte."
        ),
        "before_you_leave": (
            "Retirez la literie utilisée et laissez-la sur le sol près du lit.\n"
            "Laissez les serviettes utilisées dans la baignoire.\n"
            "Videz le réfrigérateur des aliments ouverts.\n"
            "Éteignez toutes les lumières et appareils.\n"
            "Remettez les clés dans la boîte à clés et fermez bien la porte de l'appartement."
        ),
        "restaurant_1_description": (
            "Une légende de SoHo depuis 1975. Bistro français sombre et romantique "
            "avec un steak au poivre remarquable. Réservations indispensables."
        ),
        "restaurant_2_description": (
            "Table italo-américaine animée avec d'excellentes pâtes et vins naturels. "
            "Des places au comptoir sont souvent disponibles sans réservation."
        ),
        "restaurant_3_description": (
            "L'un des restaurants les plus célébrés de NYC — petites assiettes "
            "raffinées aux associations de saveurs inattendues. À réserver longtemps à l'avance."
        ),
        "bar_1_description": (
            "Le plus ancien bar de SoHo, ouvert depuis 1847. Sans chichis, "
            "bière fraîche et excellents burgers — une institution new-yorkaise."
        ),
        "bar_2_description": (
            "L'un des plus vieux bars de New York, à deux pas de l'appartement. "
            "Chaleureux et sans prétention — les habitués l'adorent."
        ),
        "activity_1_description": (
            "Le quartier regorge de galeries d'art de renommée mondiale. "
            "Commencez sur West Broadway et flânez — la plupart sont gratuites."
        ),
        "activity_2_description": (
            "Parc surélevé aménagé sur une ancienne voie ferrée — 2,4 km d'art, "
            "jardins et vues spectaculaires. Entrée gratuite, à 10 min en métro."
        ),
        "activity_3_description": (
            "Collection d'art américain du XXe et XXIe siècle de renommée mondiale, "
            "dans un bâtiment de Renzo Piano dans le Meatpacking District."
        ),
        "local_directory": (
            "Whole Foods le plus proche : 270 Greenwich St (10 min à pied)\n"
            "Pharmacie CVS : 180 W Houston St\n"
            "NYU Langone Health : +1 (212) 263-7300"
        ),
        "emergency_contacts": (
            "Urgences : 911\n"
            "NYC non-urgences : 311\n"
            "Équipe hôte : hello@thesoholoft.com"
        ),
    },
}


def make_patched_translate(original_fn):
    def patched(content_flat, target_language):
        if target_language in PRE_TRANSLATIONS:
            result = dict(content_flat)
            result.update(PRE_TRANSLATIONS[target_language])
            return result
        return original_fn(content_flat, target_language)
    return patched


json_str = json.dumps(PAYLOAD)
sys.argv = ["", json_str]

print("=== Generating City demo: The SoHo Loft (en / es / fr / index) ===")
import generate_villa
generate_villa.translate_public_content = make_patched_translate(
    generate_villa.translate_public_content
)
generate_villa.generate()

print("\n=== Generating print HTML + PDF ===")
import build_print_pdf
build_print_pdf.main()

print("\nDone.")
