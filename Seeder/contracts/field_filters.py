import models

from core.custom_filters import EmptyFilter


class ContractFilter(EmptyFilter):
    class Meta:
        model = models.Contract
        fields = ('state', 'valid_to', 'valid_from', 'contract_type',
                  'in_communication')
