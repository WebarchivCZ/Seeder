import tld
import constants
import reversion

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

from tld.exceptions import TldDomainNotFound
from core.models import BaseModel
from publishers.models import Publisher, ContactPerson
from legacy_db.models import TransferRecord


def validate_tld(value):
    try:
        tld.get_tld(value)
    except TldDomainNotFound:
        raise ValidationError('Invalid domain name')


class Category(models.Model):
    name = models.CharField(unique=True, max_length=150)

    def __unicode__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharField(max_length=255)
    subcategory_id = models.CharField(max_length=40, blank=True, null=True)

    def __unicode__(self):
        return self.name


@reversion.register(exclude=('last_changed',))
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
        on_delete=models.SET_NULL)

    publisher_contact = models.ForeignKey(
        ContactPerson,
        null=True, blank=True,
        on_delete=models.SET_NULL)

    name = models.CharField(_('Name'), max_length=256)
    comment = models.TextField(_('Comment'), null=True, blank=True)
    annotation = models.TextField(_('Annotation'), null=True, blank=True)

    suggested_by = models.CharField(
        _('Suggested by'),
        max_length=10,
        null=True, blank=True,
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
        on_delete=models.SET_NULL)

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


@reversion.register(exclude=('last_changed',))
class Seed(BaseModel):
    """
        Seeds are individual urls in Source.
    """
    source = models.ForeignKey(Source, on_delete=models.PROTECT)

    url = models.URLField(_('Seed url'), validators=[validate_tld])
    state = models.CharField(choices=constants.SEED_STATES,
                             default=constants.SEED_STATE_INCLUDE,
                             max_length=15)
    redirect = models.BooleanField(_('Redirect on seed'), default=False)
    robots = models.BooleanField(_('Robots.txt active'), default=False)
    comment = models.TextField(_('Comment'), null=True, blank=True)

    from_time = models.DateTimeField(verbose_name=_('From'), null=True,
                                     blank=True)
    to_time = models.DateTimeField(verbose_name=_('To'), null=True, blank=True)

    screenshot = models.ImageField(verbose_name=_('Screenshot'),
                                   upload_to='screenshots',
                                   null=True, blank=True)
    screenshot_date = models.DateTimeField(null=True, blank=True)

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
