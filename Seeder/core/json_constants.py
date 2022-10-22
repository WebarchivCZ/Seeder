import json
import os
from django.conf import settings


CONSTANTS_PATH = os.path.join(settings.BASE_DIR, "settings", "constants.json")

TYPE_BOOL = "bool"
TYPE_SHORT = "short"
TYPE_LONG = "long"


class FieldType:
    BOOL = "bool"    # BooleanField
    SHORT = "short"  # CharField
    LONG = "long"    # TextField
    RICH = "rich"    # TextField using CKEditor


""" Constant field definition with defaults """
FIELDS = {
    "webarchive_size": {
        "type": FieldType.SHORT,
        "default": "409 TB",
    },
    "wayback_maintenance": {
        "type": FieldType.BOOL,
        "default": False,
    },
    "wayback_maintenance_text_cs": {
        "type": FieldType.RICH,
        "default": """
<p><span style=\"font-size:24px\">Pokud vidíte tuto stránku, <strong>probíhá údržba dat</strong> a v archivu nelze nyní vyhledávat. Některé linky vrátí chybu.</span></p>
<p><span style=\"font-size:24px\">Prosím zkuste načíst Webarchiv později.</span></p>
""",
    },
    "wayback_maintenance_text_en": {
        "type": FieldType.RICH,
        "default": """
<p><span style=\"font-size:24px\">If you see this page, <strong>we are currently doing maintenance</strong> and it is not possible to search the archive. Some links may return an error.</span></p>
<p><span style=\"font-size:24px\">Please, try to load Webarchiv again later.</span></p>
"""
    }
}


def get_defaults():
    """ Retrieve only field key and default value, not the type """
    return {key: field["default"] for key, field in FIELDS.items()}


def get_type_for_key(key):
    """ Retrieve field's preset type or default to SHORT """
    return FIELDS.get(key, {}).get("type", FieldType.SHORT)


def load_constants():
    """ Return the DEFAULTS extended by saved constants """
    data = get_defaults()
    try:
        with open(CONSTANTS_PATH, "r") as f:
            loaded = json.load(f)
        # Only overwrite already present keys with loaded constants
        for key in data.keys():
            data[key] = loaded.get(key, data[key])
    except:
        pass
    return data


def store_constants(data):
    """ Store {key: value} pairs """
    with open(CONSTANTS_PATH, "w") as f:
        json.dump(data, f)


def update_constant(key, value):
    data = load_constants()
    data[key] = value
    store_constants(data)


def get_constant(key):
    data = load_constants()  # this includes defaults
    return data.get(key, None)
