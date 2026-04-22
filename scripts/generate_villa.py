import sys
import json
import os
from html import escape


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


def section_html(title, body_html):
    if not body_html.strip():
        return ""
    return f"""
        <section class="card">
            <h2 class="section-title">{escape(title)}</h2>
            {body_html}
        </section>
    """


def row_html(label, value):
    if not has_value(value):
        return ""
    return f"""
        <div class="info-row">
            <div class="info-label">{escape(label)}</div>
            <div class="info-value">{escape(safe_text(value))}</div>
        </div>
    """


def paragraph_html(value):
    if not has_value(value):
        return ""
    return f"<p class=\"paragraph\">{escape(safe_text(value))}</p>"


def link_button_html(label, url):
    clean_url = safe_text(url)
    if not clean_url:
        return ""
    return f'<a href="{escape(clean_url)}" class="btn" target="_blank" rel="noopener noreferrer">{escape(label)}</a>'


def build_content_sections(content):
    sections = []

    checkin = content.get("checkin", {}) or {}
    checkin_body = ""
    checkin_body += row_html("Check-in", checkin.get("checkin_time"))
    checkin_body += row_html("Check-out", checkin.get("checkout_time"))
    checkin_body += paragraph_html(checkin.get("house_access_public"))
    checkin_body += paragraph_html(checkin.get("parking_info"))
    sections.append(section_html("Arrival", checkin_body))

    about_house = content.get("about_house", {}) or {}
    about_body = ""
    about_body += paragraph_html(about_house.get("welcome_message"))
    about_body += paragraph_html(about_house.get("about_hosts"))
    about_body += paragraph_html(about_house.get("amenities_list"))
    if has_value(about_house.get("pet_friendly")):
        pet_value = "Yes" if about_house.get("pet_friendly") is True else "No"
        about_body += row_html("Pet friendly", pet_value)
    about_body += paragraph_html(about_house.get("pet_rules"))
    sections.append(section_html("About the stay", about_body))

    location_transport = content.get("location_transport", {}) or {}
    location_body = ""
    location_body += paragraph_html(location_transport.get("directions_text"))
    location_body += paragraph_html(location_transport.get("transport_options"))
    location_body += link_button_html("Open Google Maps", location_transport.get("google_maps_link"))
    sections.append(section_html("Location & transport", location_body))

    rules_info = content.get("rules_info", {}) or {}
    rules_body = ""
    rules_body += paragraph_html(rules_info.get("house_rules"))
    rules_body += paragraph_html(rules_info.get("things_to_know"))
    rules_body += paragraph_html(rules_info.get("before_you_leave"))
    sections.append(section_html("House info", rules_body))

    recommendations = content.get("recommendations", {}) or {}
    recommendations_body = ""
    recommendations_body += paragraph_html(recommendations.get("places_to_eat"))
    recommendations_body += paragraph_html(recommendations.get("places_to_drink"))
    recommendations_body += paragraph_html(recommendations.get("things_to_do"))
    recommendations_body += paragraph_html(recommendations.get("local_directory"))
    sections.append(section_html("Recommendations", recommendations_body))

    contact_social = content.get("contact_social", {}) or {}
    contact_body = ""
    contact_body += row_html("Host email", contact_social.get("host_email"))
    contact_body += paragraph_html(contact_social.get("emergency_contacts"))
    contact_body += link_button_html("Leave an Airbnb review", contact_social.get("airbnb_review_link"))
    instagram = safe_text(contact_social.get("instagram_handle"))
    if instagram:
        if instagram.startswith("@"):
            instagram_url = f"https://instagram.com/{instagram[1:]}"
        else:
            instagram_url = f"https://instagram.com/{instagram}"
        contact_body += link_button_html("Instagram", instagram_url)
    sections.append(section_html("Contact", contact_body))

    return "\n".join([section for section in sections if section.strip()])


def generate():
    try:
        payload = json.loads(sys.argv[1])
    except Exception:
        print("Error al leer JSON")
        return

    metadata = payload.get("metadata", {}) or {}
    property_data = payload.get("property", {}) or {}
    content = payload.get("content", {}) or {}

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
    primary_language = safe_text(property_data.get("primary_language")) or "English"
    slug = safe_text(metadata.get("slug")) or "demo"

    with open("templates/master.html", "r", encoding="utf-8") as f:
        html = f.read()

    sections_html = build_content_sections(content)

    html = html.replace("{{VILLA_NAME}}", escape(villa_name))
    html = html.replace("{{PROPERTY_ADDRESS}}", escape(property_address))
    html = html.replace("{{PRIMARY_LANGUAGE}}", escape(primary_language))
    html = html.replace("{{CONTENT_SECTIONS}}", sections_html)
    html = html.replace("{{COLOR_PRIMARY}}", style["primary"])
    html = html.replace("{{COLOR_ACCENT}}", style["accent"])
    html = html.replace("{{COLOR_BG}}", style["bg"])
    html = html.replace("{{COLOR_TEXT}}", style["text"])

    output_dir = os.path.join("public", "villas", slug)
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated public/villas/{slug}/index.html")


if __name__ == "__main__":
    generate()
