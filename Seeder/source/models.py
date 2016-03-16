import tld
import constants

from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from tld.exceptions import TldDomainNotFound
from reversion import revisions

from core.models import BaseModel, DatePickerField
from publishers.models import Publisher, ContactPerson
from legacy_db.models import TransferRecord


def validate_tld(value):
    try:
        tld.get_tld(value)
    except TldDomainNotFound:
        raise ValidationError('Invalid domain name')


class SeedManager(models.Manager):
    """
    Auto-filters seeds that are ready to be archived
    """
    def get_queryset(self):
        today = timezone.now()
        return super(SeedManager, self).get_queryset().filter(
            Q(source__state__in=constants.ARCHIVING_STATES,
              state=constants.SEED_STATE_INCLUDE) &
            Q(
                Q(to_time__lte=today, from_time__gte=today) |
                Q(to_time__isnull=True))
        )


class Category(models.Model):
    name = models.CharField(unique=True, max_length=150)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.id, self.name)


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255)
    subcategory_id = models.CharField(max_length=40, blank=True, null=True)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.subcategory_id, self.name)


@revisions.register(exclude=('last_changed',))
class Source(BaseModel):
    """
        Source in the context of this project means an information source that
        is going to be downloaded. This usually means website. ``seeds`` field
        represent individual urls. In most of the cases there will be one seed
        which will be equal to ``base_url``.
    """
    created_by = models.ForeignKey(
        User, related_name='sources_created',
        on_delete=models.PROTECT)

    owner = models.ForeignKey(
        User, verbose_name=_('Curator'),
        on_delete=models.PROTECT)

    publisher = models.ForeignKey(
        verbose_name=_('Publisher'),
        to=Publisher,
        null=True, blank=True,
        on_delete=models.DO_NOTHING)

    publisher_contact = models.ForeignKey(
        ContactPerson,
        null=True, blank=True,
        on_delete=models.DO_NOTHING)

    name = models.CharField(_('Name'), max_length=256)
    comment = models.TextField(_('Comment'), null=True, blank=True)
    annotation = models.TextField(_('Annotation'), null=True, blank=True)

    suggested_by = models.CharField(
        _('Suggested by'),
        max_length=10,
        null=True, blank=True,
        default=constants.SUGGESTED_CURATOR,
        choices=constants.SUGGESTED_CHOICES)

    aleph_id = models.CharField(max_length=100, blank=True, null=True)
    issn = models.CharField(max_length=20, blank=True, null=True)

    state = models.CharField(
        verbose_name=_('State'),
        max_length=15,
        choices=constants.SOURCE_STATES,
        default=constants.STATE_VOTE)

    frequency = models.IntegerField(
        verbose_name=_('Frequency'),
        choices=constants.SOURCE_FREQUENCY_PER_YEAR,
        blank=True, null=True)

    category = models.ForeignKey(
        Category, verbose_name=_('Category'),
        on_delete=models.PROTECT)

    sub_category = models.ForeignKey(
        SubCategory,
        verbose_name=_('Sub category'),
        null=True, blank=True,
        on_delete=models.DO_NOTHING)

    screenshot = models.ImageField(
        verbose_name=_('Screenshot'),
        upload_to='screenshots',
        null=True, blank=True
    )
    
    screenshot_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')

        # Extra permission for supervisors to enable them manage Sources that
        # they don't own..
        permissions = (
            ('manage_sources', 'Manage others sources'),
        )

    def get_legacy_url(self):
        """
        Returns url to legacy system with this source
        """
        record = TransferRecord.objects.filter(
            target_type=ContentType.objects.get_for_model(self),
            target_id=self.id).first()
        if record:
            return constants.LEGACY_URL.format(pk=record.original_id)

    def __unicode__(self):
        return self.name

    def css_class(self):
        """
            Get css class based on status
        """
        for css_class, states in constants.STATE_COLORS.items():
            if self.state in states:
                return css_class
        return ''

    def get_absolute_url(self):
        return reverse('source:detail', args=[str(self.id)])

    def wakat_url(self):
        """
        :return: link to https://github.com/WebArchivCZ/wa-kat
        """
        return settings.WAKAT_URL.format(id=self.id)

        
@revisions.register(exclude=('last_changed',))
class Seed(BaseModel):
    """
        Seeds are individual urls in Source.
    """
    GENTLE_FETCH_CHOICES = (
        ('default', _('default')),
        ('low', _('low')),
        ('very_low', _('very_low')),
    )

    BUDGET_CHOICES = (
        (15000, 15000),
        (60000, 60000),
        (5600, 5600),
    )

    source = models.ForeignKey(Source, on_delete=models.PROTECT)

    url = models.URLField(_('Seed url'), validators=[validate_tld])
    state = models.CharField(choices=constants.SEED_STATES,
                             default=constants.SEED_STATE_INCLUDE,
                             max_length=15)

    comment = models.TextField(_('Comment'), null=True, blank=True)
    from_time = DatePickerField(verbose_name=_('From'), null=True, blank=True)
    to_time = DatePickerField(verbose_name=_('To'), null=True, blank=True)

    # Seed state fields:
    javascript = models.BooleanField(_('Javascript'), default=False)
    global_reject = models.BooleanField(_('Global reject'), default=False)
    youtube = models.BooleanField(_('Youtube'), default=False)
    calendars = models.BooleanField(_('Calendars'), default=False)
    local_traps = models.BooleanField(_('Local traps'), default=False)
    redirect = models.BooleanField(_('Redirect on seed'), default=False)
    robots = models.BooleanField(_('Robots.txt active'), default=False)

    gentle_fetch = models.CharField(
        max_length=10,
        choices=GENTLE_FETCH_CHOICES,
        blank=True,
    )

    budget = models.IntegerField(
        choices=BUDGET_CHOICES,
        blank=True,
        null=True,
    )

    objects = models.Manager()
    archiving = SeedManager()

    class Meta:
        verbose_name = _('Seed')
        verbose_name_plural = _('Seeds')

    def css_class(self):
        if self.active and self.from_time and self.to_time:
            return 'success'
        return constants.SEED_COLORS[self.state]

    def __unicode__(self):
        return self.url


class SeedExport(BaseModel):
    """
        Represents seed export file
    """

    frequency = models.IntegerField(
        verbose_name=_('Frequency'),
        choices=constants.SOURCE_FREQUENCY_PER_YEAR)
    export_file = models.FileField()

    def __unicode__(self):
        return self.frequency
