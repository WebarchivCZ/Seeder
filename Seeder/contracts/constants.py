from django.utils.translation import ugettext as _


CONTRACT_CREATIVE_COMMONS = 'CCOMONS'
CONTRACT_PROPRIETARY = 'PROPRIETARY'

CONTRACT_TYPE_CHOICES = (
    (CONTRACT_CREATIVE_COMMONS, _('Creative commons')),
    (CONTRACT_PROPRIETARY, _('Proprietary')),
)
