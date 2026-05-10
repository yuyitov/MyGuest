#!/usr/bin/env python3
"""One-shot runner: generates the Ocean Drive Retreat commercial demo.

Provides pre-translated content for ES/FR so no OpenAI key is needed locally.
The translations are embedded directly to guarantee quality in the committed files.
"""
import sys
import os
import json

# Run from project root so all relative paths resolve correctly
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
os.chdir(project_root)
sys.path.insert(0, script_dir)

PAYLOAD = {
    "metadata": {
        "slug": "ocean-drive-retreat",
    },
    "property": {
        "property_name": "Ocean Drive Retreat",
        "property_address": "800 Ocean Drive, Miami Beach, FL 33139",
        "style": "Coastal",
        "property_environment": "Beach",
        "primary_language": "English",
    },
    "content": {
        "demo_mode": True,
        "wifi_ssid": "OceanDrive_Guest",
        "wifi_password": "SunsetBeach2024!",
        "house_access_private": (
            "Lockbox at main entrance — code: #4521. "
            "Front door keypad: 7842#. "
            "Please leave all keys in the lockbox upon departure."
        ),
        "host_phone": "+1 (305) 555-0142",
        "about_house": {
            "welcome_message": (
                "Welcome to Ocean Drive Retreat — a sun-drenched haven steps from "
                "Miami Beach's most iconic boulevard. We hope this guide makes your "
                "stay effortless and memorable. Reach out anytime if there is "
                "anything you need."
            ),
            "about_hosts": (
                "Your stay is managed by The Ocean Drive Team, a group of Miami "
                "Beach locals passionate about great hospitality. We are available "
                "by email and typically respond within a few hours."
            ),
            "amenities_list": (
                "Private rooftop pool\n"
                "Ocean-view terrace\n"
                "High-speed WiFi\n"
                "Central AC\n"
                "Full kitchen\n"
                "Smart TV\n"
                "Beach towels & chairs\n"
                "Umbrella to borrow\n"
                "In-unit washer & dryer"
            ),
            "pet_friendly": False,
        },
        "checkin": {
            "checkin_time": "3:00 PM",
            "checkout_time": "11:00 AM",
            "house_access_public": (
                "Detailed arrival instructions will be shared privately before check-in."
            ),
            "parking_info": (
                "Street parking available on Ocean Drive and Collins Ave. "
                "Nearest city garage: 7th St & Collins Ave — approximately $15/day."
            ),
        },
        "location_transport": {
            "google_maps_link": (
                "https://maps.google.com/?q=800+Ocean+Drive+Miami+Beach+FL+33139"
            ),
            "directions_text": (
                "Located directly on Ocean Drive in the heart of the Art Deco "
                "Historic District. From Miami International Airport, take SR-836 E "
                "to I-195 E, then head south on Alton Rd to Ocean Drive — "
                "approximately 30 minutes."
            ),
            "transport_options": (
                "Rideshare: Uber and Lyft are widely available throughout South Beach. "
                "Citi Bike stations are within a 2-minute walk. "
                "The South Beach Local circulator bus runs nearby and is free of charge."
            ),
        },
        "rules_info": {
            "things_to_know": (
                "The terrace door opens by pulling the handle upward — it locks "
                "automatically when closed.\n"
                "The ice maker takes 24 hours to fill after first use.\n"
                "Recycling bin is the blue one under the kitchen sink.\n"
                "The rooftop pool area closes at 10 PM per building rules."
            ),
            "house_rules": (
                "No smoking indoors or on the terrace.\n"
                "Please keep noise levels respectful after 10 PM.\n"
                "Maximum 4 guests at any time.\n"
                "No parties or large gatherings."
            ),
            "before_you_leave": (
                "Strip used bedding and leave towels in the bathtub.\n"
                "Dispose of food waste before departing.\n"
                "Ensure all lights, AC, and appliances are off.\n"
                "Lock the front door upon exit."
            ),
        },
        "recommendations": {
            "property_environment": "Beach",
            "restaurant_1_name": "Larios on the Beach",
            "restaurant_1_maps_link": "https://maps.google.com/?q=820+Ocean+Dr+Miami+Beach+FL",
            "restaurant_1_description": (
                "Cuban classics and fresh mojitos right on the boulevard. "
                "Great for people-watching — an Ocean Drive staple."
            ),
            "restaurant_2_name": "Joe's Stone Crab",
            "restaurant_2_maps_link": "https://maps.google.com/?q=11+Washington+Ave+Miami+Beach+FL",
            "restaurant_2_description": (
                "Miami Beach institution since 1913. Stone crabs are a must when "
                "in season (Oct–May). Reservations recommended."
            ),
            "restaurant_3_name": "Yardbird Southern Table & Bar",
            "restaurant_3_maps_link": "https://maps.google.com/?q=1600+Lenox+Ave+Miami+Beach+FL",
            "restaurant_3_description": (
                "Beloved Southern comfort food with exceptional fried chicken. "
                "Reservations strongly recommended on weekends."
            ),
            "bar_1_name": "Sweet Liberty",
            "bar_1_maps_link": "https://maps.google.com/?q=237+20th+St+Miami+Beach+FL",
            "bar_1_description": (
                "Award-winning craft cocktail bar with an inventive menu and lively crowd. "
                "Try the Paper Plane."
            ),
            "bar_2_name": "The Broken Shaker",
            "bar_2_maps_link": "https://maps.google.com/?q=2727+Indian+Creek+Dr+Miami+Beach+FL",
            "bar_2_description": (
                "Outdoor garden bar in a courtyard setting — one of Miami's most beloved "
                "and atmospheric spots."
            ),
            "activity_1_name": "South Beach at Sunrise",
            "activity_1_link": "https://maps.google.com/?q=South+Beach+Miami+FL",
            "activity_1_description": (
                "The beach is steps from your door. Early mornings are magical — "
                "calm water, cool breeze, and no crowds."
            ),
            "activity_2_name": "Art Deco Walking Tour",
            "activity_2_link": "https://mdpl.org/tours/",
            "activity_2_description": (
                "Explore Miami Beach's iconic Art Deco architecture on a guided or "
                "self-guided tour through the historic district."
            ),
            "activity_3_name": "Wynwood Walls",
            "activity_3_link": "https://maps.google.com/?q=Wynwood+Walls+Miami+FL",
            "activity_3_description": (
                "World-famous outdoor street art museum, 15 minutes by rideshare. "
                "A must-see Miami cultural landmark."
            ),
            "local_directory": (
                "Nearest Walgreens: Collins Ave & 9th St\n"
                "Nearest Publix Supermarket: 1920 West Ave (10 min by rideshare)\n"
                "Mount Sinai Medical Center: +1 (305) 674-2121"
            ),
        },
        "contact_social": {
            "host_email": "hello@oceandriveretreat.com",
            "emergency_contacts": (
                "Emergency: 911\n"
                "Property Team: hello@oceandriveretreat.com"
            ),
            "instagram_handle": "@oceandriveretreat",
        },
    },
}

# Pre-translated content — avoids needing OPENAI_API_KEY locally.
PRE_TRANSLATIONS = {
    "Español": {
        "welcome_message": (
            "Bienvenido a Ocean Drive Retreat — un paraíso soleado a pasos del "
            "bulevar más icónico de Miami Beach. Esperamos que esta guía haga tu "
            "estadía fácil y memorable. Contáctanos en cualquier momento si "
            "necesitas algo."
        ),
        "about_hosts": (
            "Tu estadía está gestionada por The Ocean Drive Team, un grupo de "
            "locales de Miami Beach apasionados por la hospitalidad. Estamos "
            "disponibles por correo electrónico y generalmente respondemos en "
            "pocas horas."
        ),
        "directions_text": (
            "Ubicado directamente en Ocean Drive, en el corazón del Distrito "
            "Histórico Art Deco. Desde el Aeropuerto Internacional de Miami, "
            "toma SR-836 E hacia I-195 E, luego dirígete al sur por Alton Rd "
            "hasta Ocean Drive — aproximadamente 30 minutos."
        ),
        "transport_options": (
            "Transporte compartido: Uber y Lyft están ampliamente disponibles "
            "en South Beach. Las estaciones de Citi Bike están a 2 minutos a pie. "
            "El autobús local South Beach Local circula cerca y es gratuito."
        ),
        "things_to_know": (
            "La puerta de la terraza se abre tirando el mango hacia arriba — "
            "se cierra automáticamente.\n"
            "El fabricador de hielo tarda 24 horas en llenarse con el primer uso.\n"
            "El bote de reciclaje es el azul debajo del fregadero.\n"
            "El área de la piscina en la azotea cierra a las 10 PM según las "
            "reglas del edificio."
        ),
        "house_rules": (
            "Prohibido fumar dentro o en la terraza.\n"
            "Por favor mantén niveles de ruido considerados después de las 10 PM.\n"
            "Máximo 4 huéspedes en todo momento.\n"
            "Prohibidas las fiestas o reuniones numerosas."
        ),
        "before_you_leave": (
            "Quita la ropa de cama usada y deja las toallas en la bañera.\n"
            "Elimina los residuos de comida antes de salir.\n"
            "Asegúrate de que todas las luces, el AC y los electrodomésticos "
            "estén apagados.\n"
            "Cierra la puerta principal al salir."
        ),
        "house_access_private": (
            "Caja de seguridad en la entrada principal — código: #4521. "
            "Teclado de la puerta: 7842#. "
            "Por favor deja todas las llaves en la caja de seguridad al salir."
        ),
        "house_access_public": (
            "Las instrucciones detalladas de llegada se compartirán de forma "
            "privada antes del check-in."
        ),
        "parking_info": (
            "Estacionamiento en la calle disponible en Ocean Drive y Collins Ave. "
            "Garaje municipal más cercano: 7th St & Collins Ave — "
            "aproximadamente $15/día."
        ),
        "restaurant_1_description": (
            "Clásicos cubanos y mojitos frescos justo en el bulevar. "
            "Ideal para ver pasar a la gente — un clásico de Ocean Drive."
        ),
        "restaurant_2_description": (
            "Institución de Miami Beach desde 1913. Los cangrejos de piedra son "
            "imprescindibles cuando están en temporada (oct–may). "
            "Se recomienda reservar."
        ),
        "restaurant_3_description": (
            "Amada comida sureña con un pollo frito excepcional. "
            "Se recomienda reservar los fines de semana."
        ),
        "bar_1_description": (
            "Bar de cócteles artesanales galardonado con una carta creativa y "
            "ambiente animado. Prueba el Paper Plane."
        ),
        "bar_2_description": (
            "Bar al aire libre en un patio acogedor — uno de los rincones más "
            "queridos y con más ambiente de Miami."
        ),
        "activity_1_description": (
            "La playa está a pasos de tu puerta. Los amaneceres son mágicos — "
            "agua tranquila, brisa fresca y sin multitudes."
        ),
        "activity_2_description": (
            "Explora la icónica arquitectura Art Deco de Miami Beach en un tour "
            "guiado o autoguiado por el distrito histórico."
        ),
        "activity_3_description": (
            "Famoso museo al aire libre de arte urbano, a 15 minutos en "
            "transporte compartido. Un referente cultural imprescindible de Miami."
        ),
        "local_directory": (
            "Walgreens más cercano: Collins Ave & 9th St\n"
            "Supermercado Publix más cercano: 1920 West Ave (10 min en transporte)\n"
            "Mount Sinai Medical Center: +1 (305) 674-2121"
        ),
        "emergency_contacts": (
            "Emergencias: 911\n"
            "Equipo de la propiedad: hello@oceandriveretreat.com"
        ),
    },
    "Français": {
        "welcome_message": (
            "Bienvenue à Ocean Drive Retreat — un havre ensoleillé à deux pas du "
            "boulevard le plus emblématique de Miami Beach. Nous espérons que ce "
            "guide rendra votre séjour simple et mémorable. N'hésitez pas à nous "
            "contacter à tout moment si vous avez besoin de quoi que ce soit."
        ),
        "about_hosts": (
            "Votre séjour est géré par The Ocean Drive Team, un groupe de Miamiens "
            "passionnés par l'hospitalité. Nous sommes disponibles par e-mail et "
            "répondons généralement en quelques heures."
        ),
        "directions_text": (
            "Situé directement sur Ocean Drive, au cœur du quartier historique "
            "Art Déco. Depuis l'aéroport international de Miami, prenez la "
            "SR-836 E vers l'I-195 E, puis dirigez-vous vers le sud sur Alton Rd "
            "jusqu'à Ocean Drive — environ 30 minutes."
        ),
        "transport_options": (
            "VTC : Uber et Lyft sont largement disponibles à South Beach. "
            "Les stations Citi Bike sont à 2 minutes à pied. "
            "Le bus local South Beach Local passe à proximité et est gratuit."
        ),
        "things_to_know": (
            "La porte de la terrasse s'ouvre en tirant la poignée vers le haut "
            "— elle se verrouille automatiquement à la fermeture.\n"
            "La machine à glace met 24 heures à se remplir lors de la première "
            "utilisation.\n"
            "Le bac de recyclage est le bleu sous l'évier de la cuisine.\n"
            "L'espace piscine sur le toit ferme à 22h conformément au règlement "
            "de l'immeuble."
        ),
        "house_rules": (
            "Il est interdit de fumer à l'intérieur ou sur la terrasse.\n"
            "Veuillez maintenir un niveau sonore raisonnable après 22h.\n"
            "Maximum 4 personnes à tout moment.\n"
            "Fêtes et grands rassemblements interdits."
        ),
        "before_you_leave": (
            "Retirez la literie utilisée et laissez les serviettes dans la "
            "baignoire.\n"
            "Éliminez les déchets alimentaires avant de partir.\n"
            "Vérifiez que toutes les lumières, la climatisation et les appareils "
            "sont éteints.\n"
            "Verrouillez la porte d'entrée en sortant."
        ),
        "house_access_private": (
            "Boîte à clés à l'entrée principale — code : #4521. "
            "Clavier de la porte : 7842#. "
            "Veuillez laisser toutes les clés dans la boîte à clés au départ."
        ),
        "house_access_public": (
            "Les instructions détaillées d'arrivée seront communiquées de façon "
            "privée avant le check-in."
        ),
        "parking_info": (
            "Stationnement possible dans la rue sur Ocean Drive et Collins Ave. "
            "Parking municipal le plus proche : 7th St & Collins Ave — "
            "environ 15 $/jour."
        ),
        "restaurant_1_description": (
            "Classiques cubains et mojitos frais directement sur le boulevard. "
            "Idéal pour observer les passants — une institution d'Ocean Drive."
        ),
        "restaurant_2_description": (
            "Institution de Miami Beach depuis 1913. Les crabes de pierre sont "
            "incontournables en saison (oct–mai). Réservations recommandées."
        ),
        "restaurant_3_description": (
            "Comfort food américain apprécié avec un poulet frit exceptionnel. "
            "Réservations fortement recommandées le week-end."
        ),
        "bar_1_description": (
            "Bar à cocktails artisanaux primé avec une carte inventive et une "
            "ambiance animée. À essayer : le Paper Plane."
        ),
        "bar_2_description": (
            "Bar en plein air dans une cour intérieure — l'un des endroits les "
            "plus aimés et les plus atmosphériques de Miami."
        ),
        "activity_1_description": (
            "La plage est à deux pas. Les matins sont magiques — eau calme, "
            "brise fraîche et aucune foule."
        ),
        "activity_2_description": (
            "Explorez l'architecture Art Déco emblématique de Miami Beach lors "
            "d'une visite guidée ou en autonomie dans le quartier historique."
        ),
        "activity_3_description": (
            "Célèbre musée d'art de rue en plein air, à 15 minutes en VTC. "
            "Un lieu culturel incontournable à Miami."
        ),
        "local_directory": (
            "Walgreens le plus proche : Collins Ave & 9th St\n"
            "Supermarché Publix le plus proche : 1920 West Ave (10 min en VTC)\n"
            "Mount Sinai Medical Center : +1 (305) 674-2121"
        ),
        "emergency_contacts": (
            "Urgences : 911\n"
            "Équipe de la propriété : hello@oceandriveretreat.com"
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

print("=== Generating villa pages (en / es / fr / index) ===")
import generate_villa
generate_villa.translate_public_content = make_patched_translate(
    generate_villa.translate_public_content
)
generate_villa.generate()

print("\n=== Generating print HTML + PDF ===")
import build_print_pdf
build_print_pdf.main()

print("\nDone.")
