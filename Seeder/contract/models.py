import constants
import reversion

from datetime import datetime

from django.db import models
from django.db.models.query_utils import Q
from django.utils.translation import ugettext as _

from core.models import BaseModel
from source.models import Source


class ContractManager(models.Manager):
    """
        Custom manager for filtering active contracts
    """

    def valid(self):
        return self.get_queryset().filter(
            Q(valid=True) &
            Q(Q(date_end__gte=datetime.now()) | Q(date_end=None))
        )


@reversion.register(exclude=('last_changed',))
class Contract(BaseModel):
    source = models.ForeignKey(Source)

    date_start = models.DateField()
    date_end = models.DateField(null=True, blank=True)

    contract_file = models.FileField(null=True, blank=True)
    contract_type = models.CharField(choices=constants.CONTRACT_TYPE_CHOICES,
                                     max_length=12)

    valid = models.BooleanField(default=True)

    objects = ContractManager()

    def __unicode__(self):
        return _('{0} valid from {1} to {2}').format(
            self.get_contract_type_display(),
            self.date_start,
            self.date_end or '---'
        )

    def is_valid(self):
        """
        Checks that contract is valid and that it did not expire.
        If it is expired self.valid will be set to false.
        """
        if self.valid:
            expired = (self.date_end < datetime.now()
                       if self.date_end else False)
            if expired:
                self.valid = False
                self.save()
            return not expired
        return self.valid

    def get_style(self):
        """
        Helper class to get css class according to status of the contract
        :return:
        """
        if self.is_valid():
            return 'success'
        return 'danger'
