import sys
import json
import os

def generate():
    # Recibir datos de Tally
    try:
        data = json.loads(sys.argv[1])
    except:
        print("Error al leer JSON")
        return
    
    # Definición de Estilos Actualizada
    styles = {
        "Coastal": {"primary": "#2C7A7B", "accent": "#F4A261", "bg": "#F0F9FF", "text": "#2D3748"},
        "Minimalist": {"primary": "#8B6F47", "accent": "#D9CEBA", "bg": "#F9F6F0", "text": "#2E2218"},
        "Classic": {"primary": "#000000", "accent": "#A0A0A0", "bg": "#FFFFFF", "text": "#1A1A1A"},
        "Sunset": {"primary": "#E76F51", "accent": "#E9C46A", "bg": "#FFF5F2", "text": "#264653"}
    }

    # Si el estilo no coincide, usa Minimalist por default
    style = styles.get(data.get('style'), styles['Minimalist'])
    
    # Leer plantilla maestra
    with open('templates/master.html', 'r') as f:
        html = f.read()

    # Reemplazar variables (aseguramos que los nombres coincidan con Tally)
    html = html.replace('{{VILLA_NAME}}', data.get('name', 'My Villa'))
    html = html.replace('{{WIFI_SSID}}', data.get('wifi_name', 'WiFi_Name'))
    html = html.replace('{{WIFI_PASSWORD}}', data.get('wifi_pass', 'Password'))
    html = html.replace('{{MAPS_LINK}}', data.get('maps', '#'))
    html = html.replace('{{PHONE}}', data.get('phone', '')) # Agregamos esta que faltaba
    html = html.replace('{{COLOR_PRIMARY}}', style['primary'])
    html = html.replace('{{COLOR_ACCENT}}', style['accent'])
    html = html.replace('{{COLOR_BG}}', style['bg'])
    html = html.replace('{{COLOR_TEXT}}', style['text'])

    # Crear carpeta del cliente (nombre en minúsculas y sin espacios)
    folder_name = data.get('name', 'demo').lower().replace(' ', '-')
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open(f"{folder_name}/index.html", "w") as f:
        f.write(html)

if __name__ == "__main__":
    generate()
