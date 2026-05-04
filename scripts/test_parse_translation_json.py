import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_villa import parse_translation_json


def run_tests():
    plain = json.dumps({"welcome_message": "Hola", "about_hosts": "Somos anfitriones"})
    parsed_plain = parse_translation_json(plain)
    assert parsed_plain["welcome_message"] == "Hola"
    assert parsed_plain["about_hosts"] == "Somos anfitriones"

    wrapped = json.dumps({
        "target_language": "Español",
        "fields": {
            "welcome_message": "Bienvenidos",
            "about_hosts": "Encantados de recibirte",
        },
    })
    parsed_wrapped = parse_translation_json(wrapped)
    assert parsed_wrapped == {
        "welcome_message": "Bienvenidos",
        "about_hosts": "Encantados de recibirte",
    }

    fenced = """```json
    {"fields": {"transport_options": "Toma el tranvía", "parking_info": "Parking gratuito"}}
    ```"""
    parsed_fenced = parse_translation_json(fenced)
    assert parsed_fenced["transport_options"] == "Toma el tranvía"
    assert parsed_fenced["parking_info"] == "Parking gratuito"


if __name__ == "__main__":
    run_tests()
    print("parse_translation_json tests passed")
