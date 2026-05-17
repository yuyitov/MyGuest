#!/usr/bin/env python3
"""Generates the Classic style demo: Le Marais Flat, Paris."""
import sys
import os
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
os.chdir(project_root)
sys.path.insert(0, script_dir)

PAYLOAD = {
    "metadata": {
        "slug": "le-marais-flat",
    },
    "property": {
        "property_name": "Le Marais Flat",
        "property_address": "12 Rue des Francs-Bourgeois, Paris 75004, France",
        "style": "Classic",
        "property_environment": "City",
        "primary_language": "English",
    },
    "content": {
        "demo_mode": True,
        "wifi_ssid": "LeMaraisFlat",
        "wifi_password": "Paris2024Bienvenue",
        "house_access_private": (
            "Building door code: A1847B. "
            "Take the staircase to the 3rd floor — apartment 3A. "
            "Key safe next to the door — code: 5291. "
            "Please return all keys to the safe on checkout."
        ),
        "host_phone": "+33 6 12 34 56 78",
        "about_house": {
            "welcome_message": (
                "Welcome to Le Marais Flat — a classic Haussmann apartment in the "
                "heart of one of Paris's most beloved neighbourhoods. "
                "We hope this guide helps you feel at home and make the most of your stay. "
                "Please reach out any time — we are always happy to help."
            ),
            "about_hosts": (
                "Your stay is hosted by Sophie & Marc, Parisians born and raised in Le Marais. "
                "We love sharing our neighbourhood with guests from around the world. "
                "We are available by email and typically respond within a few hours."
            ),
            "amenities_list": (
                "High-speed WiFi\n"
                "Smart TV with Netflix\n"
                "Nespresso machine & French press\n"
                "Fully equipped kitchen\n"
                "Central heating\n"
                "Parquet floors & period mouldings\n"
                "Overlooking a quiet inner courtyard\n"
                "Iron & ironing board\n"
                "Hairdryer\n"
                "Fresh towels & luxury bed linen"
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
                "Street parking in Le Marais is very limited and time-restricted. "
                "Nearest underground car park: Parking Saint-Paul, 4 Rue de l'Ave Maria (5 min walk). "
                "We strongly recommend arriving by metro, taxi, or rideshare."
            ),
        },
        "location_transport": {
            "google_maps_link": (
                "https://maps.google.com/?q=12+Rue+des+Francs-Bourgeois+Paris+75004+France"
            ),
            "directions_text": (
                "Located in Le Marais, one of Paris's most historic and vibrant districts. "
                "From Charles de Gaulle Airport: take the RER B to Châtelet-Les Halles, "
                "then 15 minutes on foot or one stop on line 1 to Saint-Paul — about 50 minutes total. "
                "From Orly Airport: take Orlyval + RER B or taxi directly (approx. 45 min)."
            ),
            "transport_options": (
                "Metro: Saint-Paul (line 1) and Chemin Vert (line 8) are both 5 minutes on foot. "
                "Vélib' bike-share stations are on every other block throughout Le Marais. "
                "Taxis and rideshares (Uber, Bolt) are available 24/7 throughout Paris."
            ),
        },
        "rules_info": {
            "things_to_know": (
                "The building door code must be entered each time — it does not stay open.\n"
                "The apartment is on the 3rd floor — there is no lift.\n"
                "Rubbish bins are in the courtyard to the right of the main entrance. "
                "Yellow bin for recycling, green for general waste.\n"
                "The neighbourhood is lively at night — earplugs are in the bedside drawer "
                "if needed."
            ),
            "house_rules": (
                "No smoking anywhere in the apartment or on the balcony.\n"
                "Maximum 2 guests at all times.\n"
                "Please keep noise levels respectful after 10 PM — the building has thin walls.\n"
                "No parties or events.\n"
                "Please do not ring neighbours' doorbells."
            ),
            "before_you_leave": (
                "Strip used bedding and leave it at the foot of the bed.\n"
                "Leave used towels in the bathtub.\n"
                "Dispose of all food waste in the bins in the courtyard.\n"
                "Ensure windows are closed and locked.\n"
                "Return keys to the safe and pull the front door firmly shut."
            ),
        },
        "recommendations": {
            "property_environment": "City",
            "restaurant_1_name": "L'As du Fallafel",
            "restaurant_1_maps_link": "https://maps.google.com/?q=34+Rue+des+Rosiers+Paris+75004",
            "restaurant_1_description": (
                "A Le Marais legend — the best falafel in Paris, possibly in Europe. "
                "Expect a queue. Takeaway or eat standing. Cash only. Worth it."
            ),
            "restaurant_2_name": "Septime",
            "restaurant_2_maps_link": "https://maps.google.com/?q=80+Rue+de+Charonne+Paris+75011",
            "restaurant_2_description": (
                "One of Paris's most celebrated bistronomy restaurants. "
                "Seasonal, creative, and deeply French. Book 3–4 weeks in advance."
            ),
            "restaurant_3_name": "Breizh Café",
            "restaurant_3_maps_link": "https://maps.google.com/?q=109+Rue+Vieille+du+Temple+Paris+75003",
            "restaurant_3_description": (
                "The finest crêpes in Paris, made with Breton buckwheat and exceptional "
                "ingredients. The salted caramel crêpe is unmissable."
            ),
            "bar_1_name": "Le Mary Celeste",
            "bar_1_maps_link": "https://maps.google.com/?q=1+Rue+Commines+Paris+75003",
            "bar_1_description": (
                "Natural wines, craft cocktails and excellent oysters in a lively "
                "Le Marais setting. No reservations — arrive early or late."
            ),
            "bar_2_name": "Candelaria",
            "bar_2_maps_link": "https://maps.google.com/?q=52+Rue+de+Saintonge+Paris+75003",
            "bar_2_description": (
                "Hidden speakeasy behind a taqueria — some of the most inventive "
                "cocktails in Paris. Ring the bell on the unmarked door at the back."
            ),
            "activity_1_name": "Le Marais Gallery Walk",
            "activity_1_link": "https://maps.google.com/?q=Le+Marais+Paris+galleries",
            "activity_1_description": (
                "The apartment is surrounded by private contemporary art galleries. "
                "Most are open Tuesday–Saturday and free to enter. "
                "Rue Vieille-du-Temple and Rue Debelleyme are the best streets to explore."
            ),
            "activity_2_name": "Centre Pompidou",
            "activity_2_link": "https://centrepompidou.fr",
            "activity_2_description": (
                "Europe's premier modern and contemporary art museum, 10 minutes on foot. "
                "The rooftop offers one of the best panoramic views of Paris."
            ),
            "activity_3_name": "Place des Vosges",
            "activity_3_link": "https://maps.google.com/?q=Place+des+Vosges+Paris",
            "activity_3_description": (
                "Paris's oldest planned square — a masterpiece of French Renaissance "
                "architecture, 5 minutes on foot. Perfect for a morning coffee "
                "under the arcades."
            ),
            "local_directory": (
                "Nearest supermarket: Monoprix, 71 Rue Saint-Antoine (5 min walk)\n"
                "Nearest pharmacy: Pharmacie du Marais, 88 Rue de Rivoli\n"
                "Hôtel-Dieu Hospital (emergency): +33 1 42 34 82 34"
            ),
        },
        "contact_social": {
            "host_email": "hello@lemarasflat.com",
            "emergency_contacts": (
                "European emergency: 112\n"
                "Police: 17 / SAMU (ambulance): 15\n"
                "Host team: hello@lemarasflat.com"
            ),
            "airbnb_review_link": "https://airbnb.com/",
            "instagram_handle": "@lemarisflat.paris",
        },
    },
}

PRE_TRANSLATIONS = {
    "Español": {
        "welcome_message": (
            "Bienvenido a Le Marais Flat — un clásico apartamento Haussmann en el "
            "corazón de uno de los barrios más queridos de París. "
            "Esperamos que esta guía te haga sentir en casa y aproveches al máximo "
            "tu estadía. Contáctanos cuando quieras — estamos felices de ayudar."
        ),
        "about_hosts": (
            "Tu estadía es gestionada por Sophie y Marc, parisinos nacidos y criados "
            "en Le Marais. Nos encanta compartir nuestro barrio con huéspedes de "
            "todo el mundo. Estamos disponibles por correo y solemos responder en pocas horas."
        ),
        "house_access_private": (
            "Código de la puerta del edificio: A1847B. "
            "Sube la escalera al 3er piso — apartamento 3A. "
            "Caja de seguridad junto a la puerta — código: 5291. "
            "Por favor devuelve todas las llaves a la caja al hacer el checkout."
        ),
        "house_access_public": (
            "Las instrucciones detalladas de acceso se enviarán de forma privada "
            "antes del check-in."
        ),
        "parking_info": (
            "El estacionamiento en Le Marais es muy limitado y con horario restringido. "
            "Parking subterráneo más cercano: Parking Saint-Paul, 4 Rue de l'Ave Maria (5 min). "
            "Recomendamos llegar en metro, taxi o transporte compartido."
        ),
        "directions_text": (
            "Ubicado en Le Marais, uno de los distritos más históricos y vibrantes de París. "
            "Desde el aeropuerto Charles de Gaulle: toma el RER B hasta Châtelet-Les Halles, "
            "luego 15 min a pie o una parada en línea 1 hasta Saint-Paul — unos 50 min en total. "
            "Desde Orly: Orlyval + RER B o taxi directo (aprox. 45 min)."
        ),
        "transport_options": (
            "Metro: Saint-Paul (línea 1) y Chemin Vert (línea 8) a 5 min a pie. "
            "Estaciones de Vélib' (bicicletas) en cada cuadra de Le Marais. "
            "Taxis y rideshares (Uber, Bolt) disponibles 24/7 en todo París."
        ),
        "things_to_know": (
            "El código de la puerta del edificio debe introducirse cada vez — no queda abierta.\n"
            "El apartamento está en el 3er piso — no hay ascensor.\n"
            "Los cubos de basura están en el patio a la derecha de la entrada principal. "
            "Amarillo para reciclaje, verde para residuos generales.\n"
            "El barrio es animado por la noche — hay tapones para los oídos en el cajón "
            "de la mesita de noche si los necesitas."
        ),
        "house_rules": (
            "Prohibido fumar en el apartamento o en el balcón.\n"
            "Máximo 2 huéspedes en todo momento.\n"
            "Por favor mantén el ruido bajo después de las 10 PM — las paredes son delgadas.\n"
            "Prohibidas las fiestas o eventos.\n"
            "Por favor no toques los timbres de los vecinos."
        ),
        "before_you_leave": (
            "Quita la ropa de cama usada y déjala al pie de la cama.\n"
            "Deja las toallas usadas en la bañera.\n"
            "Elimina todos los residuos de comida en los cubos del patio.\n"
            "Asegúrate de que las ventanas estén cerradas y con llave.\n"
            "Devuelve las llaves a la caja y cierra bien la puerta principal."
        ),
        "restaurant_1_description": (
            "Una leyenda de Le Marais — el mejor falafel de París, quizás de Europa. "
            "Espera fila. Para llevar o comer de pie. Solo efectivo. Vale la pena."
        ),
        "restaurant_2_description": (
            "Uno de los restaurantes de bistronomy más celebrados de París. "
            "De temporada, creativo y profundamente francés. Reserva con 3–4 semanas de antelación."
        ),
        "restaurant_3_description": (
            "Las mejores crêpes de París, hechas con trigo sarraceno bretón e ingredientes "
            "excepcionales. La crêpe de caramelo salado es imperdible."
        ),
        "bar_1_description": (
            "Vinos naturales, cócteles artesanales y excelentes ostras en un ambiente "
            "animado de Le Marais. Sin reservas — llega temprano o tarde."
        ),
        "bar_2_description": (
            "Speakeasy escondido detrás de una taquería — algunos de los cócteles más "
            "creativos de París. Toca el timbre en la puerta sin cartel al fondo."
        ),
        "activity_1_description": (
            "El apartamento está rodeado de galerías de arte contemporáneo privadas. "
            "La mayoría abren martes–sábado y la entrada es gratuita. "
            "Rue Vieille-du-Temple y Rue Debelleyme son las mejores calles para explorar."
        ),
        "activity_2_description": (
            "El museo de arte moderno y contemporáneo más importante de Europa, a 10 min a pie. "
            "La azotea ofrece una de las mejores vistas panorámicas de París."
        ),
        "activity_3_description": (
            "La plaza más antigua de París — una obra maestra del Renacimiento francés, "
            "a 5 minutos a pie. Perfecta para un café matutino bajo las arcadas."
        ),
        "local_directory": (
            "Supermercado más cercano: Monoprix, 71 Rue Saint-Antoine (5 min a pie)\n"
            "Farmacia más cercana: Pharmacie du Marais, 88 Rue de Rivoli\n"
            "Hospital Hôtel-Dieu (urgencias): +33 1 42 34 82 34"
        ),
        "emergency_contacts": (
            "Emergencias europeas: 112\n"
            "Policía: 17 / SAMU (ambulancia): 15\n"
            "Equipo anfitrión: hello@lemarasflat.com"
        ),
    },
    "Français": {
        "welcome_message": (
            "Bienvenue au Marais Flat — un appartement haussmannien classique au cœur "
            "de l'un des quartiers les plus aimés de Paris. "
            "Nous espérons que ce guide vous aidera à vous sentir chez vous et à "
            "profiter pleinement de votre séjour. N'hésitez pas à nous contacter."
        ),
        "about_hosts": (
            "Votre séjour est pris en charge par Sophie et Marc, Parisiens nés et "
            "élevés dans le Marais. Nous adorons partager notre quartier avec des "
            "voyageurs du monde entier. Nous sommes disponibles par e-mail et "
            "répondons généralement en quelques heures."
        ),
        "house_access_private": (
            "Code de la porte de l'immeuble : A1847B. "
            "Montez l'escalier jusqu'au 3e étage — appartement 3A. "
            "Boîte à clés à côté de la porte — code : 5291. "
            "Veuillez remettre toutes les clés dans la boîte à clés au départ."
        ),
        "house_access_public": (
            "Les instructions d'accès détaillées vous seront envoyées de façon privée "
            "avant le check-in."
        ),
        "parking_info": (
            "Le stationnement dans le Marais est très limité et soumis à des horaires. "
            "Parking souterrain le plus proche : Parking Saint-Paul, 4 rue de l'Ave Maria (5 min). "
            "Nous recommandons vivement d'arriver en métro, taxi ou VTC."
        ),
        "directions_text": (
            "Situé dans le Marais, l'un des quartiers les plus historiques et vivants de Paris. "
            "Depuis l'aéroport Charles de Gaulle : prenez le RER B jusqu'à Châtelet-Les Halles, "
            "puis 15 minutes à pied ou un arrêt sur la ligne 1 jusqu'à Saint-Paul — "
            "environ 50 minutes au total. "
            "Depuis Orly : Orlyval + RER B ou taxi direct (environ 45 min)."
        ),
        "transport_options": (
            "Métro : Saint-Paul (ligne 1) et Chemin Vert (ligne 8) à 5 minutes à pied. "
            "Stations Vélib' disponibles dans tout le Marais. "
            "Taxis et VTC (Uber, Bolt) disponibles 24h/24 dans tout Paris."
        ),
        "things_to_know": (
            "Le code de la porte de l'immeuble doit être saisi à chaque fois — elle ne reste pas ouverte.\n"
            "L'appartement est au 3e étage — il n'y a pas d'ascenseur.\n"
            "Les poubelles se trouvent dans la cour à droite de l'entrée principale. "
            "Jaune pour le recyclage, vert pour les ordures ménagères.\n"
            "Le quartier est animé le soir — des bouchons d'oreilles se trouvent dans "
            "le tiroir de la table de nuit si nécessaire."
        ),
        "house_rules": (
            "Il est interdit de fumer dans l'appartement ou sur le balcon.\n"
            "Maximum 2 personnes à tout moment.\n"
            "Veuillez limiter le bruit après 22h — les murs sont fins.\n"
            "Fêtes et événements interdits.\n"
            "Merci de ne pas sonner chez les voisins."
        ),
        "before_you_leave": (
            "Retirez la literie utilisée et laissez-la au pied du lit.\n"
            "Laissez les serviettes dans la baignoire.\n"
            "Jetez tous les déchets alimentaires dans les poubelles de la cour.\n"
            "Vérifiez que les fenêtres sont bien fermées à clé.\n"
            "Remettez les clés dans la boîte à clés et fermez bien la porte d'entrée."
        ),
        "restaurant_1_description": (
            "Une légende du Marais — le meilleur falafel de Paris, peut-être d'Europe. "
            "Attendez-vous à une queue. À emporter ou debout. Espèces uniquement. Ça vaut le détour."
        ),
        "restaurant_2_description": (
            "L'un des restaurants de bistronomie les plus célébrés de Paris. "
            "Saisonnier, créatif et profondément français. Réservez 3 à 4 semaines à l'avance."
        ),
        "restaurant_3_description": (
            "Les meilleures crêpes de Paris, préparées avec du sarrasin breton et "
            "des ingrédients d'exception. La crêpe au caramel beurre salé est incontournable."
        ),
        "bar_1_description": (
            "Vins naturels, cocktails artisanaux et excellentes huîtres dans une ambiance "
            "animée du Marais. Sans réservation — arrivez tôt ou tard."
        ),
        "bar_2_description": (
            "Speakeasy caché derrière une taqueria — certains des cocktails les plus créatifs "
            "de Paris. Sonnez à la porte discrète au fond."
        ),
        "activity_1_description": (
            "L'appartement est entouré de galeries d'art contemporain privées. "
            "La plupart sont ouvertes du mardi au samedi et l'entrée est gratuite. "
            "La rue Vieille-du-Temple et la rue Debelleyme sont les meilleures rues à explorer."
        ),
        "activity_2_description": (
            "Le premier musée d'art moderne et contemporain d'Europe, à 10 minutes à pied. "
            "Le toit offre l'une des plus belles vues panoramiques sur Paris."
        ),
        "activity_3_description": (
            "La plus ancienne place de Paris — un chef-d'œuvre de la Renaissance française, "
            "à 5 minutes à pied. Parfaite pour un café du matin sous les arcades."
        ),
        "local_directory": (
            "Supermarché le plus proche : Monoprix, 71 rue Saint-Antoine (5 min à pied)\n"
            "Pharmacie la plus proche : Pharmacie du Marais, 88 rue de Rivoli\n"
            "Hôpital Hôtel-Dieu (urgences) : +33 1 42 34 82 34"
        ),
        "emergency_contacts": (
            "Urgences européennes : 112\n"
            "Police : 17 / SAMU (ambulance) : 15\n"
            "Équipe hôte : hello@lemarasflat.com"
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

print("=== Generating Classic demo: Le Marais Flat Paris (en / es / fr / index) ===")
import generate_villa
generate_villa.translate_public_content = make_patched_translate(
    generate_villa.translate_public_content
)
generate_villa.generate()

print("\n=== Generating print HTML + PDF ===")
import build_print_pdf
build_print_pdf.main()

print("\nDone.")
