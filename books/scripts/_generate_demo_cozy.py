#!/usr/bin/env python3
"""Generates the Cozy style demo: Casa Selva, Tulum."""
import sys
import os
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
os.chdir(project_root)
sys.path.insert(0, script_dir)

PAYLOAD = {
    "metadata": {
        "slug": "casa-selva-tulum",
    },
    "property": {
        "property_name": "Casa Selva",
        "property_address": "Aldea Zamá, Tulum, Quintana Roo 77760, México",
        "style": "Sunset",
        "property_environment": "Cozy",
        "primary_language": "English",
    },
    "content": {
        "demo_mode": True,
        "wifi_ssid": "CasaSelva_Guests",
        "wifi_password": "JungleMoon2024",
        "house_access_private": (
            "Entrance gate code: #6391. "
            "Lockbox on the left wall inside the gate — code: 4827. "
            "Your house key is inside. "
            "Please return all keys to the lockbox upon departure."
        ),
        "host_phone": "+52 (984) 555-0167",
        "about_house": {
            "welcome_message": (
                "Welcome to Casa Selva — a secluded jungle bungalow tucked inside "
                "Tulum's most beloved eco-neighbourhood. We hope you feel completely "
                "at home here. This guide has everything you need for a perfect stay. "
                "Reach out any time — we're always nearby."
            ),
            "about_hosts": (
                "Your stay is hosted by Ana & Luis, Tulum locals who built Casa Selva "
                "with a deep love for the jungle, sustainable living, and genuine "
                "hospitality. We live 10 minutes away and are always available."
            ),
            "amenities_list": (
                "Private jungle garden with hammocks\n"
                "Plunge pool\n"
                "Outdoor rain shower\n"
                "Outdoor yoga & meditation deck\n"
                "High-speed WiFi\n"
                "King bed with organic cotton linens\n"
                "Handmade artisan furniture\n"
                "Fully equipped kitchen\n"
                "Bicycle for two (complimentary)\n"
                "Ceiling fans & cross ventilation (no AC — jungle stays naturally cool)\n"
                "Eco-friendly toiletries"
            ),
            "pet_friendly": False,
        },
        "checkin": {
            "checkin_time": "3:00 PM",
            "checkout_time": "10:00 AM",
            "house_access_public": (
                "Detailed arrival instructions will be shared privately before check-in."
            ),
            "parking_info": (
                "Free parking available inside the gated property — space for one car. "
                "The entrance gate code is included in your private access details."
            ),
        },
        "location_transport": {
            "google_maps_link": (
                "https://maps.google.com/?q=Aldea+Zama+Tulum+Quintana+Roo+Mexico"
            ),
            "directions_text": (
                "Casa Selva is located inside Aldea Zamá, Tulum's premier eco-residential "
                "development. From Cancún International Airport: take Highway 307 south "
                "for approximately 130 km — about 2 hours by car or ADO bus. "
                "From central Tulum town: 10 minutes south by taxi or rental car."
            ),
            "transport_options": (
                "Rental car or scooter: strongly recommended — Tulum rewards exploration. "
                "Taxis: widely available and inexpensive within Tulum. "
                "Bicycles: complimentary bikes are available for nearby cenotes and the ruins. "
                "ADO bus: direct service from Cancún and Playa del Carmen to Tulum bus terminal."
            ),
        },
        "rules_info": {
            "things_to_know": (
                "No AC — the jungle architecture keeps the house naturally cool. "
                "Ceiling fans are on remote controls in the bedside drawer.\n"
                "Please do not leave food uncovered outdoors — the jungle has wildlife.\n"
                "Mosquito repellent is available in the bathroom cabinet.\n"
                "The plunge pool is unheated — perfect on warm afternoons.\n"
                "Water is filtered and safe to drink directly from the kitchen tap."
            ),
            "house_rules": (
                "No single-use plastics — Tulum is an eco-sensitive zone. "
                "Reusable bottles and bags are provided in the kitchen.\n"
                "No loud music after 9 PM — the jungle wildlife is part of the experience.\n"
                "Maximum 2 guests at all times.\n"
                "Please keep the entrance gate closed at all times.\n"
                "Shoes off at the front door — there's a rack provided."
            ),
            "before_you_leave": (
                "Bag any food waste in the compostable bags under the kitchen sink.\n"
                "Leave used towels on the bathroom floor.\n"
                "Close all windows and the patio door before leaving.\n"
                "Return the bicycles to the rack by the entrance.\n"
                "Return all keys to the lockbox and close the gate behind you."
            ),
        },
        "recommendations": {
            "property_environment": "Cozy",
            "restaurant_1_name": "Hartwood",
            "restaurant_1_maps_link": "https://maps.google.com/?q=Hartwood+Tulum+Mexico",
            "restaurant_1_description": (
                "Tulum's most celebrated restaurant — all wood-fired, all local. "
                "No reservations. Arrive early (opens at 6 PM) or expect a wait. "
                "Worth every minute."
            ),
            "restaurant_2_name": "Arca",
            "restaurant_2_maps_link": "https://maps.google.com/?q=Arca+Tulum+Mexico",
            "restaurant_2_description": (
                "Contemporary Mexican cuisine in a stunning open-air space. "
                "Creative tasting menus using local ingredients. "
                "Reservations recommended."
            ),
            "restaurant_3_name": "El Camello Jr.",
            "restaurant_3_maps_link": "https://maps.google.com/?q=El+Camello+Jr+Tulum+Mexico",
            "restaurant_3_description": (
                "No-frills local seafood at its best — fresh ceviche, grilled fish, "
                "cold beers. A true Tulum gem that tourists rarely find."
            ),
            "bar_1_name": "Gitano",
            "bar_1_maps_link": "https://maps.google.com/?q=Gitano+Tulum+Mexico",
            "bar_1_description": (
                "A magical jungle bar with mezcal cocktails, live music, and "
                "a setting unlike anywhere else on earth. Sunset is perfect timing."
            ),
            "bar_2_name": "Batey Mojito & Guarapo Bar",
            "bar_2_maps_link": "https://maps.google.com/?q=Batey+Mojito+Tulum+Mexico",
            "bar_2_description": (
                "Crushed sugarcane mojitos made fresh to order in an open-air shack. "
                "Cash only, unforgettable, and impossibly cheap."
            ),
            "activity_1_name": "Gran Cenote",
            "activity_1_link": "https://maps.google.com/?q=Gran+Cenote+Tulum+Mexico",
            "activity_1_description": (
                "The most beautiful cenote near Tulum — crystal-clear water, "
                "stalactites, and turtles. Reachable by bicycle in 15 minutes. "
                "Arrive before 9 AM to beat the crowds."
            ),
            "activity_2_name": "Tulum Ruins",
            "activity_2_link": "https://maps.google.com/?q=Tulum+Ruins+Mexico",
            "activity_2_description": (
                "Ancient Mayan cliff-top ruins overlooking the turquoise Caribbean. "
                "One of the most photogenic archaeological sites in Mexico. "
                "Open daily from 8 AM."
            ),
            "activity_3_name": "Sian Ka'an Biosphere Reserve",
            "activity_3_link": "https://maps.google.com/?q=Sian+Kaan+Biosphere+Tulum",
            "activity_3_description": (
                "UNESCO World Heritage Site just 30 minutes south. "
                "Boat tours through mangroves, wildlife spotting, and remote beaches "
                "that feel like the edge of the world."
            ),
            "local_directory": (
                "Nearest supermarket: Chedraui, Tulum town (15 min by car)\n"
                "Nearest pharmacy: Farmacia Similares, Av. Tulum (15 min)\n"
                "Cruz Roja Tulum (Red Cross): +52 (984) 871-2222"
            ),
        },
        "contact_social": {
            "host_email": "hola@casaselvatulum.com",
            "emergency_contacts": (
                "Emergency: 911\n"
                "Cruz Roja Tulum: +52 (984) 871-2222\n"
                "Host Ana & Luis: hola@casaselvatulum.com"
            ),
            "airbnb_review_link": "https://airbnb.com/",
            "instagram_handle": "@casaselva.tulum",
        },
    },
}

PRE_TRANSLATIONS = {
    "Español": {
        "welcome_message": (
            "Bienvenido a Casa Selva — un bungalow escondido en la selva dentro del "
            "vecindario eco-residencial más querido de Tulum. Esperamos que te sientas "
            "completamente en casa. Esta guía tiene todo lo que necesitas para una "
            "estadía perfecta. Contáctanos cuando quieras — siempre estamos cerca."
        ),
        "about_hosts": (
            "Tu estadía es gestionada por Ana y Luis, locales de Tulum que construyeron "
            "Casa Selva con un amor profundo por la selva, la vida sostenible y la "
            "hospitalidad genuina. Vivimos a 10 minutos y siempre estamos disponibles."
        ),
        "house_access_private": (
            "Código de la puerta de entrada: #6391. "
            "Caja de seguridad en la pared izquierda dentro de la puerta — código: 4827. "
            "Tu llave de casa está adentro. "
            "Por favor devuelve todas las llaves a la caja de seguridad al salir."
        ),
        "house_access_public": (
            "Las instrucciones detalladas de llegada se compartirán de forma "
            "privada antes del check-in."
        ),
        "parking_info": (
            "Estacionamiento gratuito dentro de la propiedad cerrada — espacio para un auto. "
            "El código de la puerta de entrada está en tus detalles privados de acceso."
        ),
        "directions_text": (
            "Casa Selva está dentro de Aldea Zamá, el desarrollo eco-residencial más "
            "distinguido de Tulum. Desde el Aeropuerto Internacional de Cancún: toma "
            "la Carretera 307 sur por aproximadamente 130 km — unas 2 horas en auto o "
            "autobús ADO. Desde el centro de Tulum: 10 minutos al sur en taxi o auto."
        ),
        "transport_options": (
            "Auto o scooter de alquiler: muy recomendado — Tulum invita a explorar. "
            "Taxis: ampliamente disponibles y económicos en Tulum. "
            "Bicicletas: disponibles de forma gratuita para cenotes y ruinas cercanas. "
            "ADO: servicio directo desde Cancún y Playa del Carmen a la terminal de Tulum."
        ),
        "things_to_know": (
            "Sin aire acondicionado — la arquitectura de selva mantiene la casa naturalmente fresca. "
            "Los ventiladores de techo tienen controles remotos en el cajón de la mesita de noche.\n"
            "Por favor no dejes comida descubierta afuera — la selva tiene vida silvestre.\n"
            "Hay repelente de mosquitos en el botiquín del baño.\n"
            "La piscina plunge no está calentada — perfecta en las tardes cálidas.\n"
            "El agua es filtrada y segura para beber directamente del grifo de la cocina."
        ),
        "house_rules": (
            "Sin plásticos de un solo uso — Tulum es una zona eco-sensible. "
            "Hay botellas y bolsas reutilizables en la cocina.\n"
            "Sin música alta después de las 9 PM — la fauna de la selva es parte de la experiencia.\n"
            "Máximo 2 huéspedes en todo momento.\n"
            "Por favor mantén la puerta de entrada cerrada en todo momento.\n"
            "Zapatos fuera en la entrada — hay un rack disponible."
        ),
        "before_you_leave": (
            "Mete los residuos de comida en las bolsas compostables bajo el fregadero.\n"
            "Deja las toallas usadas en el suelo del baño.\n"
            "Cierra todas las ventanas y la puerta del patio antes de salir.\n"
            "Devuelve las bicicletas al rack junto a la entrada.\n"
            "Devuelve todas las llaves a la caja de seguridad y cierra la puerta al salir."
        ),
        "restaurant_1_description": (
            "El restaurante más celebrado de Tulum — todo a leña, todo local. "
            "Sin reservaciones. Llega temprano (abre a las 6 PM) o espera en fila. "
            "Vale cada minuto."
        ),
        "restaurant_2_description": (
            "Cocina mexicana contemporánea en un impresionante espacio al aire libre. "
            "Menús de degustación creativos con ingredientes locales. "
            "Se recomienda reservar."
        ),
        "restaurant_3_description": (
            "Mariscos locales sin pretensiones en su mejor versión — ceviche fresco, "
            "pescado a la parrilla, cervezas frías. Una joya de Tulum que pocos turistas conocen."
        ),
        "bar_1_description": (
            "Un bar de selva mágico con cócteles de mezcal, música en vivo y "
            "un ambiente único en el mundo. El atardecer es el momento perfecto."
        ),
        "bar_2_description": (
            "Mojitos de caña de azúcar exprimida en el momento en una choza al aire libre. "
            "Solo efectivo, inolvidable e increíblemente barato."
        ),
        "activity_1_description": (
            "El cenote más hermoso cerca de Tulum — agua cristalina, "
            "estalactitas y tortugas. Accesible en bicicleta en 15 minutos. "
            "Llega antes de las 9 AM para evitar multitudes."
        ),
        "activity_2_description": (
            "Ruinas mayas en lo alto de un acantilado con vista al Caribe turquesa. "
            "Uno de los sitios arqueológicos más fotogénicos de México. "
            "Abierto todos los días desde las 8 AM."
        ),
        "activity_3_description": (
            "Sitio Patrimonio de la Humanidad de la UNESCO a 30 minutos al sur. "
            "Tours en lancha por manglares, avistamiento de fauna y playas remotas "
            "que parecen el fin del mundo."
        ),
        "local_directory": (
            "Supermercado más cercano: Chedraui, centro de Tulum (15 min en auto)\n"
            "Farmacia más cercana: Farmacia Similares, Av. Tulum (15 min)\n"
            "Cruz Roja Tulum: +52 (984) 871-2222"
        ),
        "emergency_contacts": (
            "Emergencias: 911\n"
            "Cruz Roja Tulum: +52 (984) 871-2222\n"
            "Anfitriones Ana y Luis: hola@casaselvatulum.com"
        ),
    },
    "Français": {
        "welcome_message": (
            "Bienvenue à Casa Selva — un bungalow caché dans la jungle, au cœur du "
            "quartier éco-résidentiel le plus prisé de Tulum. Nous espérons que vous "
            "vous y sentirez vraiment chez vous. Ce guide contient tout ce dont vous "
            "avez besoin. N'hésitez pas à nous contacter — nous sommes toujours proches."
        ),
        "about_hosts": (
            "Votre séjour est pris en charge par Ana et Luis, des habitants de Tulum "
            "qui ont construit Casa Selva avec une profonde passion pour la jungle, "
            "le mode de vie durable et une hospitalité sincère. "
            "Nous habitons à 10 minutes et sommes toujours disponibles."
        ),
        "house_access_private": (
            "Code du portail d'entrée : #6391. "
            "Boîte à clés sur le mur gauche à l'intérieur du portail — code : 4827. "
            "Votre clé de maison est à l'intérieur. "
            "Veuillez remettre toutes les clés dans la boîte à clés au départ."
        ),
        "house_access_public": (
            "Les instructions détaillées d'arrivée seront communiquées de façon "
            "privée avant le check-in."
        ),
        "parking_info": (
            "Parking gratuit à l'intérieur de la propriété clôturée — place pour une voiture. "
            "Le code du portail est inclus dans vos informations d'accès privées."
        ),
        "directions_text": (
            "Casa Selva est située dans Aldea Zamá, le développement éco-résidentiel "
            "de référence à Tulum. Depuis l'aéroport international de Cancún : "
            "prenez la route 307 vers le sud sur environ 130 km — environ 2 heures en voiture "
            "ou en bus ADO. Depuis le centre de Tulum : 10 minutes vers le sud en taxi ou voiture."
        ),
        "transport_options": (
            "Voiture ou scooter de location : fortement recommandé — Tulum invite à l'exploration. "
            "Taxis : largement disponibles et abordables à Tulum. "
            "Vélos : mis à disposition gratuitement pour les cénotes et les ruines proches. "
            "Bus ADO : service direct depuis Cancún et Playa del Carmen jusqu'au terminal de Tulum."
        ),
        "things_to_know": (
            "Pas de climatisation — l'architecture jungle maintient la maison naturellement fraîche. "
            "Les ventilateurs de plafond ont des télécommandes dans le tiroir de la table de nuit.\n"
            "Ne laissez pas de nourriture à découvert à l'extérieur — la jungle abrite une faune sauvage.\n"
            "Du répulsif anti-moustiques est disponible dans l'armoire de la salle de bain.\n"
            "La piscine plunge n'est pas chauffée — parfaite les après-midi chauds.\n"
            "L'eau est filtrée et peut être bue directement au robinet de la cuisine."
        ),
        "house_rules": (
            "Pas de plastiques à usage unique — Tulum est une zone éco-sensible. "
            "Des gourdes et sacs réutilisables sont fournis dans la cuisine.\n"
            "Pas de musique forte après 21h — la faune de la jungle fait partie de l'expérience.\n"
            "Maximum 2 personnes à tout moment.\n"
            "Veuillez maintenir le portail d'entrée fermé en permanence.\n"
            "Chaussures à enlever à l'entrée — un rack est prévu à cet effet."
        ),
        "before_you_leave": (
            "Mettez les déchets alimentaires dans les sacs compostables sous l'évier de cuisine.\n"
            "Laissez les serviettes utilisées sur le sol de la salle de bain.\n"
            "Fermez toutes les fenêtres et la porte du patio avant de partir.\n"
            "Ramenez les vélos au rack près de l'entrée.\n"
            "Remettez toutes les clés dans la boîte à clés et fermez le portail derrière vous."
        ),
        "restaurant_1_description": (
            "Le restaurant le plus célèbre de Tulum — tout au feu de bois, tout local. "
            "Sans réservation. Arrivez tôt (ouverture à 18h) ou attendez en file. "
            "Chaque minute vaut la peine."
        ),
        "restaurant_2_description": (
            "Cuisine mexicaine contemporaine dans un cadre en plein air spectaculaire. "
            "Menus dégustation créatifs avec des ingrédients locaux. Réservations recommandées."
        ),
        "restaurant_3_description": (
            "Fruits de mer locaux sans chichi dans leur plus bel expression — ceviche frais, "
            "poisson grillé, bières fraîches. Un joyau de Tulum que les touristes trouvent rarement."
        ),
        "bar_1_description": (
            "Un bar de jungle magique avec cocktails au mezcal, musique live et "
            "une atmosphère unique au monde. L'heure du coucher de soleil est idéale."
        ),
        "bar_2_description": (
            "Mojitos à la canne à sucre fraîchement pressée dans un stand en plein air. "
            "Espèces uniquement, inoubliable et incroyablement bon marché."
        ),
        "activity_1_description": (
            "Le plus beau cénote près de Tulum — eau cristalline, "
            "stalactites et tortues. Accessible à vélo en 15 minutes. "
            "Arrivez avant 9h pour éviter la foule."
        ),
        "activity_2_description": (
            "Ruines mayas au sommet d'une falaise surplombant les Caraïbes turquoise. "
            "L'un des sites archéologiques les plus photogéniques du Mexique. "
            "Ouvert tous les jours dès 8h."
        ),
        "activity_3_description": (
            "Site classé au patrimoine mondial de l'UNESCO à 30 minutes vers le sud. "
            "Tours en bateau dans les mangroves, observation de la faune et plages sauvages "
            "qui semblent être au bout du monde."
        ),
        "local_directory": (
            "Supermarché le plus proche : Chedraui, centre de Tulum (15 min en voiture)\n"
            "Pharmacie la plus proche : Farmacia Similares, Av. Tulum (15 min)\n"
            "Cruz Roja Tulum : +52 (984) 871-2222"
        ),
        "emergency_contacts": (
            "Urgences : 911\n"
            "Cruz Roja Tulum : +52 (984) 871-2222\n"
            "Hôtes Ana et Luis : hola@casaselvatulum.com"
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

print("=== Generating Cozy demo: Casa Selva Tulum (en / es / fr / index) ===")
import generate_villa
generate_villa.translate_public_content = make_patched_translate(
    generate_villa.translate_public_content
)
generate_villa.generate()

print("\n=== Generating print HTML + PDF ===")
import build_print_pdf
build_print_pdf.main()

print("\nDone.")
