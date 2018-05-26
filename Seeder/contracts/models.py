import uuid

from datetime import date

from django.db import models
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from ckeditor.fields import RichTextField
from reversion import revisions

from core.models import BaseModel, DatePickerField
from source.models import Source
from publishers.models import Publisher
from . import constants


def get_str_uuid():
    return str(uuid.uuid4())


def this_year():
    return date.today().year


class ContractManager(models.Manager):
    """
        Custom manager for filtering active contracts
    """

    def valid(self):
        return self.get_queryset().filter(
            Q(state=constants.CONTRACT_STATE_VALID) &
            Q(Q(valid_to__gte=date.today()) | Q(valid_to=None))
        )


@revisions.register(exclude=('last_changed',))
class Contract(BaseModel):
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.DO_NOTHING,
    )
    sources = models.ManyToManyField(Source)
    state = models.CharField(_('State'),
                             choices=constants.CONTRACT_STATES,
                             default=constants.CONTRACT_STATE_NEGOTIATION,
                             max_length=15)

    creative_commons = models.BooleanField(
        _('Creative commons or other OS licence'),
        default=False
    )

    creative_commons_type = models.CharField(
        _('Creative commons type'),
        null=True,
        blank=True,
        max_length=128
    )

    valid_from = DatePickerField(
        _('Valid from'),
        null=True,
        blank=True
    )
    valid_to = DatePickerField(
        _('Valid to'),
        null=True,
        blank=True
    )

    year = models.PositiveIntegerField(
        _('Year'),
        default=this_year()
    )

    contract_file = models.FileField(
        _('Contract file'),
        null=True,
        blank=True,
        upload_to='contracts'
    )

    contract_number = models.IntegerField(
        _('Contract number'),
        null=True,
        blank=True
    )

    in_communication = models.BooleanField(
        _('In communication'),
        help_text=_('Does the publisher responds to the emails?'),
        default=False
    )

    description = models.TextField(
        _('Description'),
        null=True,
        blank=True
    )

    parent_contract = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name='sub_contracts',
    )

    objects = ContractManager()

    class Meta:
        unique_together = ('contract_number', 'year')
        ordering = ['-created']

    def __str__(self):
        if self.state == constants.CONTRACT_STATE_NEGOTIATION:
            return _('Contract in negotiation with {0}').format(self.publisher)
        return self.get_contract_number()

    def get_contract_number(self):
        return '{} / {}'.format(self.contract_number or ' - ', self.year)

    def get_type(self):
        if self.creative_commons:
            return self.creative_commons_type
        return _('Contract with {0}'.format(self.publisher))

    def publisher_responds(self):
        return (self.in_communication or
                self.state != constants.CONTRACT_STATE_NEGOTIATION)

    def get_absolute_url(self):
        return reverse('contracts:detail', args=[str(self.id)])

    def expire(self):
        """
        Expires contract and its sources
        """
        self.state = constants.CONTRACT_STATE_EXPIRED
        self.save()

        for source in self.sources.all():
            source.handle_expiring_contracts()

    def is_valid(self):
        """
        Checks that contract is valid and that it did not expire.
        If it is expired self.valid will be set to false.
        """
        if self.state == constants.CONTRACT_STATE_VALID:
            expired = (self.valid_to < date.today()
                       if self.valid_to else False)

            if expired:
                self.expire()

            return not expired
        return False

    def get_style(self):
        """
        Helper class to get css class according to status of the contract
        """
        if self.is_valid():
            return 'success'
        return 'danger'

    def assign_number(self):
        if self.contract_number:
            return

        self.contract_number = self.__class__.new_contract_number(self.year)
        self.save()

    @classmethod
    def new_contract_number(cls, year=None):
        if year is None:
            year = this_year()

        max_number = cls.objects.filter(year=year).aggregate(
            max_id=models.Max('contract_number')
        )['max_id'] or 0

        return max_number + 1

    def can_delete(self):
        return not self.contract_number


@revisions.register(exclude=('last_changed',))
class EmailNegotiation(models.Model):
    """
        This model represents an email that is going to be sent to the
        publisher, its content will be pre-filled with html template.
    """
    contract = models.ForeignKey(Contract, on_delete=models.DO_NOTHING)
    sent = models.BooleanField(default=False)

    title = models.CharField(max_length=64)
    to_email = models.EmailField()

    scheduled_date = DatePickerField(_('When to send this message'))
    content = RichTextField()
    template = models.CharField(max_length=64)

    class Meta:
        ordering = ('scheduled_date', )
