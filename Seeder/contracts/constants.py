from django.utils.translation import ugettext as _


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


NEGOTIATION_TEMPLATES = [
    'negotiation/first.html', 'negotiation/second.html',
    'negotiation/third.html', 'last.html'
]


CONTRACT_CREATIVE_COMMONS = 'CCOMMONS'
CONTRACT_PROPRIETARY = 'PROPRIETARY'

CONTRACT_TYPE_CHOICES = (
    (CONTRACT_CREATIVE_COMMONS, _('Creative commons')),
    (CONTRACT_PROPRIETARY, _('Proprietary')),
)
