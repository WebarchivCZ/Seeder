import json
import os
from django.conf import settings


CONSTANTS_PATH = os.path.join(settings.BASE_DIR, "settings", "constants.json")

DEFAULTS = {
    "webarchive_size": "409 TB",
}


def store_defaults():
    store_constants(DEFAULTS)


def load_constants():
    try:
        with open(CONSTANTS_PATH, "r") as f:
            return json.load(f)
    except:
        return DEFAULTS


def store_constants(data):
    with open(CONSTANTS_PATH, "w") as f:
        json.dump(data, f)


def update_constant(key, value):
    data = load_constants()
    data[key] = value
    store_constants(data)


def get_constant(key):
    data = load_constants()
    # Precedence of value from: Saved constants -> Defaults -> 'None'
    return data.get(key, DEFAULTS.get(key, None))
