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


CONTRACT_CREATIVE_COMMONS = 'CCOMMONS'
CONTRACT_PROPRIETARY = 'PROPRIETARY'

CONTRACT_TYPE_CHOICES = (
    (CONTRACT_CREATIVE_COMMONS, _('Creative commons')),
    (CONTRACT_PROPRIETARY, _('Proprietary')),
)
