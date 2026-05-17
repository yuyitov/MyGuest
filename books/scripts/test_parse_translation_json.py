import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from generate_villa import parse_translation_json


def test_plain_json():
    raw = json.dumps({"welcome_message": "Hola", "about_hosts": "Somos tus anfitriones"})
    parsed = parse_translation_json(raw)
    assert parsed == {"welcome_message": "Hola", "about_hosts": "Somos tus anfitriones"}


def test_wrapper_json_with_fields():
    raw = json.dumps(
        {
            "target_language": "Español",
            "fields": {
                "welcome_message": "Bienvenidos",
                "about_hosts": "Tus anfitriones",
            },
        }
    )
    parsed = parse_translation_json(raw)
    assert parsed == {"welcome_message": "Bienvenidos", "about_hosts": "Tus anfitriones"}


def test_markdown_fenced_json():
    raw = """```json
    {
      \"welcome_message\": \"Bonjour\",
      \"about_hosts\": \"Vos hôtes\"
    }
    ```"""
    parsed = parse_translation_json(raw)
    assert parsed == {"welcome_message": "Bonjour", "about_hosts": "Vos hôtes"}


if __name__ == "__main__":
    test_plain_json()
    test_wrapper_json_with_fields()
    test_markdown_fenced_json()
    print("OK: parse_translation_json tests passed")
