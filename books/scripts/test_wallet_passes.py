"""Pruebas de los pases de wallet, con credenciales de mentira.

Ningun material criptografico vive en el repo: las llaves y los certificados se
generan con `openssl` dentro de un temporal al correr la prueba y se borran al
salir. Asi el candado de secrets del workflow nunca ve un PEM, y la prueba de
todos modos ejerce la firma de verdad (RS256 para Google, PKCS#7 para Apple).

Lo que estas pruebas afirman, en orden de importancia:

1. Con los flags apagados no se firma, no se escribe y no se publica nada.
2. Con el flag prendido, el pase que sale es un pase valido y verificable.
3. En ningun caso viaja un secreto ni el token de acceso dentro del pase.
4. Una credencial rota NO tumba la generacion de la guia (solo se cae el boton).
"""

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import wallet_passes
from wallet_passes import (
    APPLE_PASS_FILENAME,
    GOOGLE_JWT_SAFE_LENGTH,
    build_wallet_assets,
    openssl_available,
)

pytestmark = pytest.mark.skipif(
    not openssl_available(),
    reason="openssl no esta disponible en esta maquina",
)

PROPERTY = {
    "slug": "casa-serena-4j8p2k9x7",
    "property_name": "Casa Serena",
    "property_address": "12 Playa Norte, Sayulita, Nayarit",
}

# Marcadores de lo que NUNCA puede aparecer dentro de un pase: un pase se
# comparte igual que una tarjeta de contacto.
FORBIDDEN_IN_PASS = [
    "token=",
    "wifi_password",
    "wifi_ssid",
    "door_code",
    "lockbox",
    "keypad",
    "host_phone",
    "house_access_private",
    "/guest/",
    "/print/",
]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Cada prueba arranca con TODOS los flags y credenciales apagados."""
    for name in (
        "MYGUEST_GOOGLE_WALLET_ENABLED",
        "MYGUEST_APPLE_WALLET_ENABLED",
        "MYGUEST_PUBLIC_BASE_URL",
        "GOOGLE_WALLET_ISSUER_ID",
        "GOOGLE_WALLET_CLASS_SUFFIX",
        "GOOGLE_WALLET_SERVICE_ACCOUNT_JSON",
        "APPLE_WALLET_PASS_TYPE_ID",
        "APPLE_WALLET_TEAM_ID",
        "APPLE_WALLET_CERT_PEM",
        "APPLE_WALLET_KEY_PEM",
        "APPLE_WALLET_WWDR_PEM",
        "APPLE_WALLET_KEY_PASSWORD",
    ):
        monkeypatch.delenv(name, raising=False)

    wallet_passes.reset_memo()
    yield
    wallet_passes.reset_memo()


def _openssl(*args, **kwargs):
    result = subprocess.run(["openssl", *args], capture_output=True, **kwargs)
    assert result.returncode == 0, result.stderr.decode("utf-8", "ignore")
    return result


def _fake_rsa_key(tmp_path, name):
    """Llave RSA de mentira, solo para esta prueba."""
    key_path = tmp_path / f"{name}.pem"
    _openssl("genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(key_path))
    return key_path


def _fake_cert(tmp_path, name, common_name):
    """Certificado autofirmado de mentira. NO es de Apple y no vale para nada."""
    key_path = _fake_rsa_key(tmp_path, f"{name}-key")
    cert_path = tmp_path / f"{name}-cert.pem"
    _openssl(
        "req", "-x509", "-new", "-key", str(key_path), "-out", str(cert_path),
        "-days", "2", "-subj", f"/CN={common_name}",
    )
    return key_path, cert_path


def _enable_google(monkeypatch, tmp_path):
    key_path = _fake_rsa_key(tmp_path, "google-sa")
    account = {
        "type": "service_account",
        "client_email": "fake-pases@myguest-de-mentira.iam.gserviceaccount.com",
        "private_key": key_path.read_text(encoding="utf-8"),
    }
    monkeypatch.setenv("MYGUEST_GOOGLE_WALLET_ENABLED", "true")
    monkeypatch.setenv("GOOGLE_WALLET_ISSUER_ID", "3388000000000000000")
    monkeypatch.setenv("GOOGLE_WALLET_SERVICE_ACCOUNT_JSON", json.dumps(account))
    return key_path


def _enable_apple(monkeypatch, tmp_path):
    key_path, cert_path = _fake_cert(tmp_path, "pass", "MyGuest Fake Pass Cert")
    _, wwdr_path = _fake_cert(tmp_path, "wwdr", "Fake WWDR Intermediate")

    monkeypatch.setenv("MYGUEST_APPLE_WALLET_ENABLED", "1")
    monkeypatch.setenv("APPLE_WALLET_PASS_TYPE_ID", "pass.com.myguestguide.stay")
    monkeypatch.setenv("APPLE_WALLET_TEAM_ID", "FAKETEAM99")
    monkeypatch.setenv("APPLE_WALLET_CERT_PEM", cert_path.read_text(encoding="utf-8"))
    monkeypatch.setenv("APPLE_WALLET_KEY_PEM", key_path.read_text(encoding="utf-8"))
    monkeypatch.setenv("APPLE_WALLET_WWDR_PEM", wwdr_path.read_text(encoding="utf-8"))


# ── 1. Apagado es apagado ──────────────────────────────────────────────────

def test_apagado_no_produce_nada(tmp_path):
    """El estado por default: ni un archivo, ni una URL, ni una firma."""
    out = tmp_path / "villa"
    assets = build_wallet_assets(output_dir=str(out), **PROPERTY)

    assert assets == {"google_wallet_url": "", "apple_pass_href": ""}
    assert not out.exists(), "con los flags apagados no se escribe nada en disco"


def test_apagado_deja_la_guia_sin_botones(tmp_path):
    """El HTML generado no puede traer link de wallet con los flags apagados."""
    out = tmp_path / "villa"
    assets = build_wallet_assets(output_dir=str(out), **PROPERTY)

    assert "pay.google.com" not in assets["google_wallet_url"]
    assert APPLE_PASS_FILENAME not in assets["apple_pass_href"]


# ── 2. Google Wallet, prendido con credenciales de mentira ─────────────────

def test_google_arma_un_jwt_rs256_verificable(monkeypatch, tmp_path):
    key_path = _enable_google(monkeypatch, tmp_path)
    assets = build_wallet_assets(output_dir=str(tmp_path / "villa"), **PROPERTY)

    url = assets["google_wallet_url"]
    assert url.startswith("https://pay.google.com/gp/v/save/")

    jwt = url.rsplit("/", 1)[1]
    header_b64, claims_b64, signature_b64 = jwt.split(".")

    # La firma es de verdad: se verifica con la llave publica de la llave falsa.
    pub_path = tmp_path / "google-pub.pem"
    _openssl("rsa", "-in", str(key_path), "-pubout", "-out", str(pub_path))

    signing_input = tmp_path / "signing-input.txt"
    signing_input.write_bytes(f"{header_b64}.{claims_b64}".encode("ascii"))

    signature_path = tmp_path / "signature.bin"
    signature_path.write_bytes(_b64url_decode(signature_b64))

    _openssl(
        "dgst", "-sha256", "-verify", str(pub_path),
        "-signature", str(signature_path), str(signing_input),
    )


def test_google_respeta_el_largo_seguro_de_la_url(monkeypatch, tmp_path):
    """La doc de Google fija 1800 caracteres; pasarse trunca el link en el movil."""
    _enable_google(monkeypatch, tmp_path)
    assets = build_wallet_assets(output_dir=str(tmp_path / "villa"), **PROPERTY)

    jwt = assets["google_wallet_url"].rsplit("/", 1)[1]
    assert len(jwt) <= GOOGLE_JWT_SAFE_LENGTH


def test_google_solo_lleva_datos_publicos(monkeypatch, tmp_path):
    _enable_google(monkeypatch, tmp_path)
    assets = build_wallet_assets(output_dir=str(tmp_path / "villa"), **PROPERTY)

    jwt = assets["google_wallet_url"].rsplit("/", 1)[1]
    claims = json.loads(_b64url_decode(jwt.split(".")[1]))
    serialized = json.dumps(claims)

    assert PROPERTY["property_name"] in serialized
    assert PROPERTY["property_address"] in serialized

    # El link del pase es el publico SIN token.
    assert f"https://myguestguide.com/villas/{PROPERTY['slug']}/" in serialized
    _assert_sin_secretos(serialized)


def test_google_prendido_sin_credenciales_no_rompe(monkeypatch, tmp_path):
    """Flag prendido y configuracion incompleta: aviso y guia sin boton."""
    monkeypatch.setenv("MYGUEST_GOOGLE_WALLET_ENABLED", "true")
    assets = build_wallet_assets(output_dir=str(tmp_path / "villa"), **PROPERTY)
    assert assets["google_wallet_url"] == ""


# ── 3. Apple Wallet, prendido con certificado de mentira ───────────────────

def test_apple_arma_un_pkpass_firmado(monkeypatch, tmp_path):
    out = tmp_path / "villa"
    _enable_apple(monkeypatch, tmp_path)

    assets = build_wallet_assets(output_dir=str(out), **PROPERTY)
    assert assets["apple_pass_href"] == APPLE_PASS_FILENAME

    pass_path = out / APPLE_PASS_FILENAME
    assert pass_path.is_file()

    with zipfile.ZipFile(pass_path) as bundle:
        nombres = set(bundle.namelist())
        assert {"pass.json", "manifest.json", "signature", "icon.png", "icon@2x.png"} <= nombres

        manifest = json.loads(bundle.read("manifest.json"))

        # El manifest es SHA-1 de cada archivo: si no casa, iOS rechaza el pase.
        import hashlib
        for nombre, digest in manifest.items():
            assert hashlib.sha1(bundle.read(nombre)).hexdigest() == digest, nombre

        assert "manifest.json" not in manifest and "signature" not in manifest

        firma = bundle.read("signature")

    # La firma es un PKCS#7 en DER de verdad: openssl la sabe leer.
    firma_path = tmp_path / "signature.der"
    firma_path.write_bytes(firma)
    salida = _openssl("pkcs7", "-inform", "DER", "-in", str(firma_path), "-print_certs")
    assert b"MyGuest Fake Pass Cert" in salida.stdout


def test_apple_pass_json_tiene_lo_que_ios_exige(monkeypatch, tmp_path):
    out = tmp_path / "villa"
    _enable_apple(monkeypatch, tmp_path)
    build_wallet_assets(output_dir=str(out), **PROPERTY)

    with zipfile.ZipFile(out / APPLE_PASS_FILENAME) as bundle:
        pass_json = json.loads(bundle.read("pass.json"))

    for clave in (
        "formatVersion",
        "passTypeIdentifier",
        "teamIdentifier",
        "serialNumber",
        "organizationName",
        "description",
    ):
        assert pass_json.get(clave), f"pass.json sin {clave}: iOS no abre el pase"

    assert pass_json["formatVersion"] == 1
    assert pass_json["generic"]["primaryFields"][0]["value"] == PROPERTY["property_name"]


def test_apple_solo_lleva_datos_publicos(monkeypatch, tmp_path):
    out = tmp_path / "villa"
    _enable_apple(monkeypatch, tmp_path)
    build_wallet_assets(output_dir=str(out), **PROPERTY)

    with zipfile.ZipFile(out / APPLE_PASS_FILENAME) as bundle:
        crudo = bundle.read("pass.json").decode("utf-8")

    assert f"https://myguestguide.com/villas/{PROPERTY['slug']}/" in crudo
    _assert_sin_secretos(crudo)


def test_apple_con_certificado_roto_no_tumba_la_generacion(monkeypatch, tmp_path):
    """Un certificado vencido o mal pegado se lleva el boton, no la guia."""
    out = tmp_path / "villa"
    _enable_apple(monkeypatch, tmp_path)
    monkeypatch.setenv("APPLE_WALLET_CERT_PEM", "-----BEGIN CERTIFICATE-----\nbasura\n-----END CERTIFICATE-----")

    assets = build_wallet_assets(output_dir=str(out), **PROPERTY)

    assert assets["apple_pass_href"] == ""
    assert not (out / APPLE_PASS_FILENAME).exists()


# ── 4. Reglas transversales ────────────────────────────────────────────────

def test_no_se_arma_pase_apuntando_a_github_io(monkeypatch, tmp_path):
    """Regla de copy del repo: los links van a myguestguide.com."""
    _enable_google(monkeypatch, tmp_path)
    monkeypatch.setenv("MYGUEST_PUBLIC_BASE_URL", "https://yuyitov.github.io/MyGuest")

    assets = build_wallet_assets(output_dir=str(tmp_path / "villa"), **PROPERTY)
    assert assets == {"google_wallet_url": "", "apple_pass_href": ""}


def test_sin_nombre_de_propiedad_no_hay_pase(monkeypatch, tmp_path):
    _enable_google(monkeypatch, tmp_path)
    datos = dict(PROPERTY, property_name="  ")

    assets = build_wallet_assets(output_dir=str(tmp_path / "villa"), **datos)
    assert assets == {"google_wallet_url": "", "apple_pass_href": ""}


# ── Utilidades ─────────────────────────────────────────────────────────────

def _b64url_decode(value):
    import base64
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _assert_sin_secretos(texto):
    minusculas = texto.lower()
    for marcador in FORBIDDEN_IN_PASS:
        assert marcador.lower() not in minusculas, (
            f"el pase se comparte y trae {marcador!r} dentro"
        )
