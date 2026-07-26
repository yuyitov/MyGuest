"""Pases de wallet para la guia del huesped — Google Wallet y Apple Wallet.

Por que existe
--------------
El valor de la guia es el huesped que VUELVE. Un huesped que regresa, o que
quiere recomendar la propiedad, no encuentra el link tres meses despues. La
vCard ya resuelve "guardar al anfitrion en el telefono"; el pase de wallet
resuelve "guardar la propiedad", que es lo que se abre de nuevo.

Los dos proveedores estan APAGADOS por default
----------------------------------------------
Ninguno de los dos se puede prender sin credenciales que Vero todavia no tiene:

- **Apple Wallet** necesita el Apple Developer Program: 99 USD/ano.
- **Google Wallet** no cobra, pero exige cuenta de servicio de Google Cloud +
  alta de Issuer + Business Profile con perfil de pagos para verificar
  identidad + revision manual de Google. Hasta que Google apruebe, el pase sale
  marcado `[TEST ONLY]` y **solo lo pueden guardar las cuentas admin/developer
  y las cuentas de prueba dadas de alta**: un huesped real toca el boton y no
  pasa nada. Medicion completa y como prenderlo:
  `docs/WALLET_PASSES_ENABLE_CHECKLIST.md`.

Con el flag apagado este modulo no firma nada, no escribe nada y no instala
nada: devuelve cadenas vacias, los placeholders quedan vacios y el bloque de
botones se oculta solo. Con el flag prendido y las credenciales mal puestas,
**avisa fuerte y sigue sin boton**: la guia es el producto, el boton es un
extra, y un certificado vencido (los de Apple duran un ano) no puede tumbar la
generacion de un cliente que ya pago.

Que va dentro del pase (y que NO)
---------------------------------
Un pase se comparte igual que una tarjeta de contacto, asi que lleva solo lo
que ya es publico en el sitio: nombre de la propiedad, direccion y el link
**sin token** a la guia publica. Nunca WiFi, codigos, telefono del anfitrion ni
el token de acceso. Misma regla que el `.vcf`.

Firma
-----
Con `openssl` por linea de comandos, que ya existe en el runner de GitHub y en
la maquina de Vero. Asi el flag apagado no cuesta ni una dependencia nueva de
pip en el workflow de generacion.
"""

import base64
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
import zipfile

# ── Configuracion ──────────────────────────────────────────────────────────
# Todo por variables de entorno. El workflow las pasa desde repo vars/secrets.

DEFAULT_PUBLIC_BASE_URL = "https://myguestguide.com"

# Regla de copy del repo: todos los links van a myguestguide.com, nunca a
# yuyitov.github.io.
FORBIDDEN_URL_HOSTS = ("yuyitov.github.io",)

ORGANIZATION_NAME = "MyGuest"

# Paleta MyGuest (CLAUDE.md): Deep Teal, Warm Ivory, Light Taupe.
BRAND_BG_RGB = (45, 106, 115)       # #2D6A73
BRAND_FG_RGB = (247, 243, 238)      # #F7F3EE
BRAND_LABEL_RGB = (216, 206, 194)   # #D8CEC2

# Longitud segura de un JWT de Google Wallet dentro de una URL, segun su doc.
GOOGLE_JWT_SAFE_LENGTH = 1800

# Nombre del archivo del pase de Apple dentro de la carpeta de la villa.
APPLE_PASS_FILENAME = "pass.pkpass"


def _env(name, default=""):
    return (os.getenv(name) or default).strip()


def _flag(name):
    """Un flag solo esta prendido con un valor afirmativo explicito."""
    return _env(name).lower() in ("1", "true", "yes", "on")


def public_base_url():
    base = _env("MYGUEST_PUBLIC_BASE_URL") or DEFAULT_PUBLIC_BASE_URL
    return base.rstrip("/")


def public_guide_url(slug):
    """Link publico de la guia, SIN token.

    Este es el unico link que puede viajar en un pase: el pase se comparte, y
    el link con `?token=` abre WiFi y codigos. Sin token se sirve el mismo
    shell publico que ya esta en GitHub Pages, que no trae ningun secreto.
    """
    clean = str(slug or "").strip().strip("/")
    if not clean:
        return ""
    return f"{public_base_url()}/villas/{clean}/"


def _warn(message):
    print(f"[wallet] AVISO: {message}", file=sys.stderr)


def _openssl(args, **kwargs):
    """Corre openssl. Devuelve CompletedProcess; el llamador revisa returncode."""
    binary = _env("OPENSSL_BIN") or "openssl"
    return subprocess.run(
        [binary] + list(args),
        capture_output=True,
        **kwargs,
    )


def openssl_available():
    try:
        result = _openssl(["version"])
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def _b64url(raw):
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


# ── Google Wallet ──────────────────────────────────────────────────────────

def google_wallet_enabled():
    return _flag("MYGUEST_GOOGLE_WALLET_ENABLED")


def _google_id_suffix(slug):
    """Los ids de Google Wallet solo aceptan [A-Za-z0-9._-]."""
    return re.sub(r"[^A-Za-z0-9._-]", "-", str(slug or "")).strip("-") or "stay"


def build_google_wallet_payload(*, slug, property_name, property_address, issuer_id, class_suffix):
    """El objeto del pase generico. Solo datos publicos.

    La clase va INCLUIDA en el JWT (no hay que crearla antes por la API REST):
    Google la crea en el primer guardado. Un paso menos que configurar.
    """
    guide_url = public_guide_url(slug)
    object_id = f"{issuer_id}.{_google_id_suffix(slug)}"
    class_id = f"{issuer_id}.{class_suffix}"

    generic_object = {
        "id": object_id,
        "classId": class_id,
        "state": "ACTIVE",
        "hexBackgroundColor": "#%02X%02X%02X" % BRAND_BG_RGB,
        "cardTitle": {"defaultValue": {"language": "en", "value": ORGANIZATION_NAME}},
        "header": {"defaultValue": {"language": "en", "value": property_name}},
    }

    if property_address:
        generic_object["subheader"] = {
            "defaultValue": {"language": "en", "value": property_address}
        }

    if guide_url:
        generic_object["linksModuleData"] = {
            "uris": [{"uri": guide_url, "description": "Open your guide"}]
        }
        generic_object["barcode"] = {
            "type": "QR_CODE",
            "value": guide_url,
            "alternateText": "",
        }

    return {
        "genericClasses": [{"id": class_id}],
        "genericObjects": [generic_object],
    }


def _sign_rs256(signing_input, private_key_pem):
    """Firma RS256 con openssl. Devuelve los bytes de la firma, o None."""
    tmpdir = tempfile.mkdtemp(prefix="myguest-gw-")
    try:
        key_path = os.path.join(tmpdir, "sa.pem")
        with open(key_path, "w", encoding="utf-8") as handle:
            handle.write(private_key_pem)

        result = _openssl(
            ["dgst", "-sha256", "-sign", key_path],
            input=signing_input,
        )

        if result.returncode != 0:
            _warn(f"openssl no pudo firmar el JWT de Google Wallet: {result.stderr.decode('utf-8', 'ignore').strip()}")
            return None

        return result.stdout
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def build_google_wallet_url(*, slug, property_name, property_address):
    """URL de "Add to Google Wallet", o "" si el flag esta apagado o falla algo.

    Nunca lanza: la guia se genera con o sin boton.
    """
    if not google_wallet_enabled():
        return ""

    issuer_id = _env("GOOGLE_WALLET_ISSUER_ID")
    class_suffix = _env("GOOGLE_WALLET_CLASS_SUFFIX") or "myguest_stay"
    account_raw = _env("GOOGLE_WALLET_SERVICE_ACCOUNT_JSON")

    if not issuer_id or not account_raw:
        _warn(
            "MYGUEST_GOOGLE_WALLET_ENABLED esta prendido pero falta "
            "GOOGLE_WALLET_ISSUER_ID o GOOGLE_WALLET_SERVICE_ACCOUNT_JSON. "
            "La guia sale sin boton de Google Wallet."
        )
        return ""

    try:
        account = json.loads(account_raw)
    except ValueError as exc:
        _warn(f"GOOGLE_WALLET_SERVICE_ACCOUNT_JSON no es JSON valido: {exc}")
        return ""

    client_email = str(account.get("client_email") or "").strip()
    private_key = str(account.get("private_key") or "")

    if not client_email or "PRIVATE KEY" not in private_key:
        _warn("La cuenta de servicio de Google Wallet no trae client_email o private_key.")
        return ""

    if not openssl_available():
        _warn("openssl no esta disponible: no se puede firmar el pase de Google Wallet.")
        return ""

    claims = {
        "iss": client_email,
        "aud": "google",
        "typ": "savetowallet",
        "origins": [public_base_url()],
        "payload": build_google_wallet_payload(
            slug=slug,
            property_name=property_name,
            property_address=property_address,
            issuer_id=issuer_id,
            class_suffix=class_suffix,
        ),
    }

    header = {"alg": "RS256", "typ": "JWT"}
    signing_input = ".".join(
        [
            _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _b64url(json.dumps(claims, separators=(",", ":"), ensure_ascii=False).encode("utf-8")),
        ]
    ).encode("ascii")

    signature = _sign_rs256(signing_input, private_key)
    if not signature:
        return ""

    jwt = signing_input.decode("ascii") + "." + _b64url(signature)

    # La doc de Google fija 1800 caracteres como largo seguro dentro de una URL.
    # Pasarse no da error: el navegador trunca el link y el boton falla en la
    # mano del huesped, que es justo el fallo silencioso que este repo persigue.
    if len(jwt) > GOOGLE_JWT_SAFE_LENGTH:
        _warn(
            f"El JWT de Google Wallet mide {len(jwt)} caracteres y el limite seguro "
            f"es {GOOGLE_JWT_SAFE_LENGTH}. La guia sale sin boton para no publicar "
            "un link que el navegador puede truncar."
        )
        return ""

    return f"https://pay.google.com/gp/v/save/{jwt}"


# ── Apple Wallet ───────────────────────────────────────────────────────────

def apple_wallet_enabled():
    return _flag("MYGUEST_APPLE_WALLET_ENABLED")


def build_apple_pass_json(*, slug, property_name, property_address, pass_type_id, team_id):
    """`pass.json` del pase generico. Solo datos publicos."""
    guide_url = public_guide_url(slug)

    back_fields = []
    if guide_url:
        back_fields.append(
            {"key": "guide", "label": "Your guide", "value": guide_url}
        )
    back_fields.append(
        {
            "key": "about",
            "label": "About this pass",
            "value": (
                "Keep this pass to find the place again, or to share it with "
                "someone you would recommend it to."
            ),
        }
    )

    secondary_fields = []
    if property_address:
        secondary_fields.append(
            {"key": "address", "label": "Address", "value": property_address}
        )

    pass_json = {
        "formatVersion": 1,
        "passTypeIdentifier": pass_type_id,
        "teamIdentifier": team_id,
        "serialNumber": str(slug),
        "organizationName": ORGANIZATION_NAME,
        "description": f"{property_name} — guest guide",
        "logoText": ORGANIZATION_NAME,
        "backgroundColor": "rgb(%d,%d,%d)" % BRAND_BG_RGB,
        "foregroundColor": "rgb(%d,%d,%d)" % BRAND_FG_RGB,
        "labelColor": "rgb(%d,%d,%d)" % BRAND_LABEL_RGB,
        "generic": {
            "primaryFields": [
                {"key": "property", "label": "Your stay", "value": property_name}
            ],
            "secondaryFields": secondary_fields,
            "auxiliaryFields": [],
            "backFields": back_fields,
        },
    }

    if guide_url:
        pass_json["barcodes"] = [
            {
                "format": "PKBarcodeFormatQR",
                "message": guide_url,
                "messageEncoding": "iso-8859-1",
            }
        ]

    return pass_json


def _png_solid(width, height, rgb):
    """PNG valido de un color plano, sin dependencias.

    Los iconos del pase son obligatorios para Apple. Se generan aqui para que
    el pase se pueda armar y probar sin ningun binario en el repo; si mas
    adelante se ponen los PNG de marca en `books/templates/wallet/apple/`, se
    usan esos (ver `_apple_images`).
    """
    red, green, blue = rgb
    raw = b"".join(
        b"\x00" + bytes((red, green, blue)) * width
        for _ in range(height)
    )

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def apple_template_dir():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "templates", "wallet", "apple"
    )


def _apple_images():
    """Imagenes del pase: las de marca si existen, si no un color plano."""
    required = {
        "icon.png": (29, 29),
        "icon@2x.png": (58, 58),
        "logo.png": (160, 50),
        "logo@2x.png": (320, 100),
    }

    template_dir = apple_template_dir()
    images = {}

    for name, (width, height) in required.items():
        override = os.path.join(template_dir, name)
        if os.path.isfile(override):
            with open(override, "rb") as handle:
                images[name] = handle.read()
        else:
            images[name] = _png_solid(width, height, BRAND_BG_RGB)

    return images


def _sign_apple_manifest(manifest_bytes, cert_pem, key_pem, wwdr_pem, key_password):
    """Firma PKCS#7 separada, en DER, como pide Apple. Devuelve bytes o None."""
    tmpdir = tempfile.mkdtemp(prefix="myguest-apple-")
    try:
        paths = {}
        for name, content in (
            ("cert.pem", cert_pem),
            ("key.pem", key_pem),
            ("wwdr.pem", wwdr_pem),
            ("manifest.json", manifest_bytes),
        ):
            path = os.path.join(tmpdir, name)
            with open(path, "wb") as handle:
                handle.write(content if isinstance(content, bytes) else content.encode("utf-8"))
            paths[name] = path

        signature_path = os.path.join(tmpdir, "signature")

        args = [
            "smime",
            "-binary",
            "-sign",
            "-certfile", paths["wwdr.pem"],
            "-signer", paths["cert.pem"],
            "-inkey", paths["key.pem"],
            "-in", paths["manifest.json"],
            "-out", signature_path,
            "-outform", "DER",
            "-noattr",
        ]

        if key_password:
            args += ["-passin", "pass:" + key_password]

        result = _openssl(args)

        if result.returncode != 0 or not os.path.isfile(signature_path):
            _warn(
                "openssl no pudo firmar el pase de Apple: "
                + result.stderr.decode("utf-8", "ignore").strip()
            )
            return None

        with open(signature_path, "rb") as handle:
            return handle.read()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def build_apple_pkpass(*, slug, property_name, property_address, output_dir):
    """Escribe `pass.pkpass` y devuelve su nombre, o "" si esta apagado o falla.

    Nunca lanza: si el certificado vencio, la guia se sigue generando sin boton.
    """
    if not apple_wallet_enabled():
        return ""

    pass_type_id = _env("APPLE_WALLET_PASS_TYPE_ID")
    team_id = _env("APPLE_WALLET_TEAM_ID")
    cert_pem = _env("APPLE_WALLET_CERT_PEM")
    key_pem = _env("APPLE_WALLET_KEY_PEM")
    wwdr_pem = _env("APPLE_WALLET_WWDR_PEM")
    key_password = _env("APPLE_WALLET_KEY_PASSWORD")

    missing = [
        name
        for name, value in (
            ("APPLE_WALLET_PASS_TYPE_ID", pass_type_id),
            ("APPLE_WALLET_TEAM_ID", team_id),
            ("APPLE_WALLET_CERT_PEM", cert_pem),
            ("APPLE_WALLET_KEY_PEM", key_pem),
            ("APPLE_WALLET_WWDR_PEM", wwdr_pem),
        )
        if not value
    ]

    if missing:
        _warn(
            "MYGUEST_APPLE_WALLET_ENABLED esta prendido pero falta "
            + ", ".join(missing)
            + ". La guia sale sin boton de Apple Wallet."
        )
        return ""

    if not openssl_available():
        _warn("openssl no esta disponible: no se puede firmar el pase de Apple.")
        return ""

    pass_json = build_apple_pass_json(
        slug=slug,
        property_name=property_name,
        property_address=property_address,
        pass_type_id=pass_type_id,
        team_id=team_id,
    )

    files = {"pass.json": json.dumps(pass_json, ensure_ascii=False, indent=2).encode("utf-8")}
    files.update(_apple_images())

    # El manifest es SHA-1 de cada archivo; la firma va sobre el manifest.
    manifest = {name: hashlib.sha1(content).hexdigest() for name, content in files.items()}
    manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")

    signature = _sign_apple_manifest(manifest_bytes, cert_pem, key_pem, wwdr_pem, key_password)
    if not signature:
        return ""

    os.makedirs(output_dir, exist_ok=True)
    pass_path = os.path.join(output_dir, APPLE_PASS_FILENAME)

    with zipfile.ZipFile(pass_path, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name, content in files.items():
            bundle.writestr(name, content)
        bundle.writestr("manifest.json", manifest_bytes)
        bundle.writestr("signature", signature)

    return APPLE_PASS_FILENAME


# ── Punto de entrada del generador ─────────────────────────────────────────

_MEMO = {}


def build_wallet_assets(*, slug, property_name, property_address, output_dir):
    """Devuelve `{"google_wallet_url": ..., "apple_pass_href": ...}`.

    Con los dos flags apagados devuelve las dos cadenas vacias sin tocar disco
    ni llamar a openssl: el generador deja los placeholders vacios y el bloque
    de botones se oculta solo en el navegador.

    Memoizado por slug: el generador renderiza tres idiomas y el pase es uno.
    """
    property_name = str(property_name or "").strip()
    property_address = str(property_address or "").strip()

    if not google_wallet_enabled() and not apple_wallet_enabled():
        return {"google_wallet_url": "", "apple_pass_href": ""}

    if not property_name:
        _warn("La propiedad no trae nombre: no se arma ningun pase de wallet.")
        return {"google_wallet_url": "", "apple_pass_href": ""}

    base = public_base_url()
    for host in FORBIDDEN_URL_HOSTS:
        if host in base:
            _warn(
                f"MYGUEST_PUBLIC_BASE_URL apunta a {host}. Regla del repo: los "
                "links van a myguestguide.com. No se arma ningun pase."
            )
            return {"google_wallet_url": "", "apple_pass_href": ""}

    memo_key = (slug, property_name, property_address, output_dir, base)
    if memo_key in _MEMO:
        return _MEMO[memo_key]

    assets = {
        "google_wallet_url": build_google_wallet_url(
            slug=slug,
            property_name=property_name,
            property_address=property_address,
        ),
        "apple_pass_href": build_apple_pkpass(
            slug=slug,
            property_name=property_name,
            property_address=property_address,
            output_dir=output_dir,
        ),
    }

    _MEMO[memo_key] = assets
    return assets


def reset_memo():
    """Solo para las pruebas: limpia el memo entre escenarios."""
    _MEMO.clear()
