"""
Google Places API (New) lookup for the MyGuest printable guide.
Returns address, phone, website for a named place.
Never raises — all errors produce an empty result.
"""
import json
import urllib.request

_cache: dict = {}

FIELD_MASK = ",".join([
    "places.formattedAddress",
    "places.internationalPhoneNumber",
    "places.nationalPhoneNumber",
    "places.websiteUri",
])


def lookup_place(name: str, location_hint: str, api_key: str) -> dict:
    """
    Query Google Places Text Search for `name` near `location_hint`.
    Returns {"address": ..., "phone": ..., "website": ...}, any value may be None.
    Returns {} on any error, missing key, or missing api_key.
    """
    if not api_key or not name:
        return {}

    cache_key = (name.strip().lower(), (location_hint or "").strip().lower())
    if cache_key in _cache:
        return _cache[cache_key]

    result = _fetch(name, location_hint, api_key)
    _cache[cache_key] = result
    return result


def _fetch(name: str, location_hint: str, api_key: str) -> dict:
    try:
        query = f"{name} {location_hint}".strip() if location_hint else name
        body = json.dumps({
            "textQuery": query,
            "maxResultCount": 1,
            "languageCode": "en",
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://places.googleapis.com/v1/places:searchText",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": FIELD_MASK,
            },
        )

        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        places = data.get("places") or []
        if not places:
            return {}

        p = places[0]
        return {
            "address": p.get("formattedAddress") or None,
            "phone": (
                p.get("internationalPhoneNumber")
                or p.get("nationalPhoneNumber")
                or None
            ),
            "website": p.get("websiteUri") or None,
        }
    except Exception:
        return {}
