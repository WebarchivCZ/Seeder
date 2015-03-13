from django_pg import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from . import constants


class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_changed = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ('created', )


class Seed(BaseModel):
    url = models.URLField()

    class Meta:
        verbose_name = _('Seed')
        verbose_name_plural = _('Seeds')

    def __unicode__(self):
        return self.url


class Publisher(BaseModel):
    """
        Publisher of the Source(s), Publisher can have multiple contacts.
    """
    name = models.CharField(_('Name'), max_length=64)
    contacts = models.ArrayField(of=models.CharField())

    class Meta:
        verbose_name = _('Publisher')
        verbose_name_plural = _('Publishers')

    def __unicode__(self):
        return self.name


class Source(BaseModel):
    """
        Source in the context of this project means an information source that
        is going to be downloaded. This usually means website. ``seeds`` field
        represent individual urls. In most of the cases there will be one seed
        which will be equal to ``base_url``.
    """
    created_by = models.ForeignKey(User, related_name='created_by')
    owner = models.ForeignKey(User, verbose_name=_('Curator'))
    name = models.CharField(_('Name'), max_length=64)
    comment = models.TextField(_('Comment'), blank=True)
    base_url = models.URLField()
    web_proposal = models.BooleanField(_('Proposed by visitor'), default=False)
    seeds = models.ManyToManyField(verbose_name=_('Seeds'), to=Seed)
    publisher = models.ForeignKey(verbose_name=_('Publisher'), to=Publisher)
    special_contact = models.CharField(blank=True, max_length=64)

    state = models.CharField(
        verbose_name=_('State'),
        max_length=3,
        choices=constants.SOURCE_STATES)
    conspectus = models.CharField(
        verbose_name=_('Conspectus'),
        choices=constants.CONSPECTUS_CHOICES,
        blank=True,
        max_length=3)
    sub_conspectus = models.CharField(
        verbose_name=_('Sub conspectus'),
        choices=constants.SUB_CONSPECTUS_CHOICES,
        blank=True,
        max_length=3)

    class Meta:
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')

    def __unicode__(self):
        return self.name