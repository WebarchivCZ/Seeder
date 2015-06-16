import constants
import reversion
import uuid

from datetime import datetime

from django.db import models
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from core.models import BaseModel
from source.models import Source
from ckeditor.fields import RichTextField


def get_str_uuid():
    return str(uuid.uuid4())


class ContractManager(models.Manager):
    """
        Custom manager for filtering active contracts
    """

    def valid(self):
        return self.get_queryset().filter(
            Q(state=constants.CONTRACT_STATE_VALID) &
            Q(Q(valid_to__gte=datetime.now()) | Q(valid_to=None))
        )


@reversion.register(exclude=('last_changed',))
class Contract(BaseModel):
    source = models.ForeignKey(Source)
    state = models.CharField(choices=constants.CONTRACT_STATES,
                             default=constants.CONTRACT_STATE_NEGOTIATION,
                             max_length=15)

    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)

    contract_file = models.FileField(null=True, blank=True,
                                     upload_to='contracts')
    contract_type = models.CharField(choices=constants.CONTRACT_TYPE_CHOICES,
                                     max_length=12)
    contract_number = models.IntegerField(null=True, blank=True)

    in_communication = models.BooleanField(
        help_text=_('Does the publisher responds to the emails?'),
        default=False)

    access_token = models.CharField(null=True, blank=True,
                                    max_length=37)
    description = models.TextField(null=True, blank=True)
    objects = ContractManager()

    def __unicode__(self):
        return _('{pk}/{year}').format(
            pk=self.pk,
            year=self.created.year
        )

    def get_absolute_url(self):
        return reverse('contracts:detail', args=[str(self.id)])

    def is_valid(self):
        """
        Checks that contract is valid and that it did not expire.
        If it is expired self.valid will be set to false.
        """
        if self.state == constants.CONTRACT_STATE_VALID:
            expired = (self.valid_to < datetime.now()
                       if self.valid_to else False)
            if expired:
                self.state = constants.CONTRACT_STATE_EXPIRED
                self.save()
            return not expired
        return False

    def get_style(self):
        """
        Helper class to get css class according to status of the contract
        """
        if self.is_valid():
            return 'success'
        return 'danger'


@reversion.register(exclude=('last_changed',))
class EmailNegotiation(models.Model):
    """
        This model represents an email that is going to be sent to the
        publisher, its content will be pre-filled with html template.
    """
    contract = models.ForeignKey(Contract)
    sent = models.BooleanField(default=False)

    title = models.CharField(max_length=64)

    scheduled_date = models.DateField(_('When to send this message'))
    content = RichTextField()
    template = models.CharField(max_length=64)

    class Meta:
        ordering = ('scheduled_date', )
