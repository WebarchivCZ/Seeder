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
    'creative', _('CreativeCommons'),
    'apache', _('Apache'),
    'gpl', _('GPL'),
    'MIT', _('MIT'),
    'LGPL 2', _('LGPL 2'),
    'LGPL 3', _('LGPL 3'),
    'mozilla', _('mozilla'),
)

EMAILS_TITLE = _('Narodni knihovna CR - archivace Vasich webovych stranek')
