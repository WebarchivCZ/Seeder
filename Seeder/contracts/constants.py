from django.utils.translation import ugettext_lazy as _
from source import constants as source_constants


CONTRACT_STATE_NEGOTIATION = 'NEGOTIATION'
CONTRACT_STATE_DECLINED = 'DECLINED'
CONTRACT_STATE_VALID = 'VALID'
CONTRACT_STATE_EXPIRED = 'EXPIRED'


CONTRACT_STATES = (
    (CONTRACT_STATE_NEGOTIATION, _('Contract in negotiation')),
    (CONTRACT_STATE_DECLINED, _('Publisher declined')),
    (CONTRACT_STATE_VALID, _('Contract is valid')),
    (CONTRACT_STATE_EXPIRED, _('Contract expired')),
)


STATE_CONVERSION = {
    CONTRACT_STATE_DECLINED: source_constants.STATE_DECLINED_BY_PUBLISHER,
    CONTRACT_STATE_VALID: source_constants.STATE_RUNNING,
    CONTRACT_STATE_EXPIRED: source_constants.STATE_CONTRACT_EXPIRED,
}

# number of days between each email reminder:
NEGOTIATION_DELAY = 14

NEGOTIATION_TEMPLATES = [
    'negotiations/first.html', 'negotiations/second.html',
    'negotiations/third.html', 'negotiations/last.html'
]

OPEN_SOURCES_TYPES = (
    ('creative', _('CreativeCommons')),
    ('apache', _('Apache')),
    ('gpl', _('GPL')),
    ('MIT', _('MIT')),
    ('LGPL 2', _('LGPL 2')),
    ('LGPL 3', _('LGPL 3')),
    ('mozilla', _('mozilla')),
)

EMAILS_TITLE = _('Narodni knihovna CR - archivace Vasich webovych stranek')


CREATIVE_COMMONS_TYPES = {
    "CC BY 4.0": {
        "description": "Attribution 4.0 International (CC BY 4.0)",
        "url": "https://creativecommons.org/licenses/by/4.0/",
    },
    "CC BY-SA 4.0": {
        "description": "Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
        "url": "https://creativecommons.org/licenses/by-sa/4.0/",
    },
    "CC BY-ND 4.0": {
        "description": "Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0)",
        "url": "https://creativecommons.org/licenses/by-nd/4.0/",
    },
    "CC BY-NC 4.0": {
        "description": "Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)",
        "url": "https://creativecommons.org/licenses/by-nc/4.0/",
    },
    "CC BY-NC-SA 4.0": {
        "description": "Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)",
        "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    },
    "CC BY-NC-ND 4.0": {
        "description": "Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)",
        "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
    },
    "CC BY 3.0 CZ": {
        "description": "Uveďte původ 3.0 Česká republika (CC BY 3.0 CZ)",
        "url": "https://creativecommons.org/licenses/by/3.0/cz/",
    },
    "CC BY-NC 3.0 CZ": {
        "description": "Uveďte původ-Neužívejte komerčně 3.0 Česká republika (CC BY-NC 3.0 CZ)",
        "url": "https://creativecommons.org/licenses/by-nc/3.0/cz/",
    },
    "CC BY-SA 3.0 CZ": {
        "description": "Uveďte původ-Zachovejte licenci 3.0 Česká republika (CC BY-SA 3.0 CZ)",
        "url": "https://creativecommons.org/licenses/by-sa/3.0/cz/",
    },
    "CC BY-ND 3.0 CZ": {
        "description": "Uveďte původ-Nezpracovávejte 3.0 Česká republika (CC BY-ND 3.0 CZ)",
        "url": "https://creativecommons.org/licenses/by-nd/3.0/cz/",
    },
    "CC BY-NC-SA 3.0 CZ": {
        "description": "Uveďte původ-Neužívejte dílo komerčně-Zachovejte licenci 3.0 Česká republika (CC BY-NC-SA 3.0 CZ)",
        "url": "https://creativecommons.org/licenses/by-nc-sa/3.0/cz/",
    },
    "CC BY-NC-ND 3.0 CZ": {
        "description": "Uveďte původ-Neužívejte komerčně-Nezpracovávejte 3.0 Česká republika (CC BY-NC-ND 3.0 CZ)",
        "url": "https://creativecommons.org/licenses/by-nc-nd/3.0/cz/",
    },
    "CC BY 3.0": {
        "description": "Attribution 3.0 Unported (CC BY 3.0)",
        "url": "https://creativecommons.org/licenses/by/3.0/",
    },
    "CC BY-NC 3.0": {
        "description": "Attribution-NonCommercial 3.0 Unported (CC BY-NC 3.0)",
        "url": "https://creativecommons.org/licenses/by-nc/3.0/",
    },
    "CC BY-SA 3.0": {
        "description": "Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)",
        "url": "https://creativecommons.org/licenses/by-sa/3.0/",
    },
    "CC BY-ND 3.0": {
        "description": "Attribution-NoDerivs 3.0 Unported (CC BY-ND 3.0)",
        "url": "https://creativecommons.org/licenses/by-nd/3.0/",
    },
    "CC BY-NC-SA 3.0": {
        "description": "Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)",
        "url": "https://creativecommons.org/licenses/by-nc-sa/3.0/",
    },
    "CC BY-NC-ND 3.0": {
        "description": "Attribution-NonCommercial-NoDerivs 3.0 Unported (CC BY-NC-ND 3.0)",
        "url": "https://creativecommons.org/licenses/by-nc-nd/3.0/",
    },
    "CC BY 2.0": {
        "description": "Uveďte původ 2.0 Generic (CC BY 2.0)",
        "url": "https://creativecommons.org/licenses/by/2.0/deed.cs",
    },
    "CC BY-NC 2.0": {
        "description": "Uveďte původ-Neužívejte komerčně 2.0 Generic (CC BY-NC 2.0)",
        "url": "https://creativecommons.org/licenses/by-nc/2.0/deed.cs",
    },
    "CC BY-SA 2.0": {
        "description": "Uveďte původ-Zachovejte licenci 2.0 Generic (CC BY-SA 2.0)",
        "url": "https://creativecommons.org/licenses/by-sa/2.0/deed.cs",
    },
    "CC BY-ND 2.0": {
        "description": "Uveďte původ-Nezpracovávejte 2.0 Generic (CC BY-ND 2.0)",
        "url": "https://creativecommons.org/licenses/by-nd/2.0/deed.cs",
    },
    "CC BY-NC-SA 2.0": {
        "description": "Uveďte původ-Neužívejte dílo komerčně-Zachovejte licenci 2.0 Generic (CC BY-NC-SA 2.0)",
        "url": "https://creativecommons.org/licenses/by-nc-sa/2.0/deed.cs",
    },
    "CC BY-NC-ND 2.0": {
        "description": "Uveďte původ-Neužívejte komerčně-Nezpracovávejte 2.0 Generic (CC BY-NC-ND 2.0)",
        "url": "https://creativecommons.org/licenses/by-nc-nd/2.0/deed.cs",
    },
    "CC BY 1.0": {
        "description": "Uveďte původ 1.0 Generic (CC BY 1.0)",
        "url": "https://creativecommons.org/licenses/by/1.0/deed.cs",
    },
    "CC BY-NC 1.0": {
        "description": "Uveďte původ-Neužívejte komerčně 1.0 Generic (CC BY-NC 1.0)",
        "url": "https://creativecommons.org/licenses/by-nc/1.0/deed.cs",
    },
    "CC BY-SA 1.0": {
        "description": "Uveďte původ-Zachovejte licenci 1.0 Generic (CC BY-SA 1.0)",
        "url": "https://creativecommons.org/licenses/by-sa/1.0/deed.cs",
    },
    "CC BY-ND 1.0": {
        "description": "Uveďte původ-Nezpracovávejte 1.0 Generic (CC BY-ND 1.0)",
        "url": "https://creativecommons.org/licenses/by-nd/1.0/deed.cs",
    },
    "CC BY-NC-SA 1.0": {
        "description": "Uveďte původ-Neužívejte dílo komerčně-Zachovejte licenci 1.0 Generic (CC BY-NC-SA 1.0)",
        "url": "https://creativecommons.org/licenses/by-nc-sa/1.0/deed.cs",
    },
    "CC BY-NC-ND 1.0": {
        "description": "Uveďte původ-Nezpracovávejte-Neužívejte komerčně 1.0 Generic (CC BY-ND-NC 1.0)",
        "url": "https://creativecommons.org/licenses/by-nc-nd/1.0/deed.cs",
    },
}

CREATIVE_COMMONS_TYPES_CHOICES = ((None, "--------"),) + tuple(
    (key, cc['description']) for key, cc in CREATIVE_COMMONS_TYPES.items()
)
