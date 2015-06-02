import models

from core.utils import EmptyFilter


class ContractFilter(EmptyFilter):
    class Meta:
        model = models.Contract
        fields = ('state', 'date_start', 'date_end', 'contract_type',
                  'in_communication')
