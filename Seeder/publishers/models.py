import reversion

from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from core.models import BaseModel


@reversion.register(exclude=('last_changed',))
class Publisher(BaseModel):
    """
        Publisher of the Source(s), Publisher can have multiple contacts.
    """
    name = models.CharField(_('Name'), max_length=64)
    email = models.EmailField(_('E-mail'), blank=True, null=True)
    phone = models.CharField(_('Phone'), blank=True, null=True, max_length=64)
    website = models.URLField(_('Website'), blank=True, null=True)

    class Meta:
        verbose_name = _('Publisher')
        verbose_name_plural = _('Publishers')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('publishers:detail', kwargs={'pk': self.id})
