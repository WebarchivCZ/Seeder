from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from reversion import revisions

from core.models import BaseModel


class ContractManager(models.Manager):
    """
        Custom manager for filtering active Publishers
    """

    def get_queryset(self):
        return super().get_queryset().filter(active=True)


@revisions.register(exclude=('last_changed',))
class Publisher(BaseModel):
    """
        Publisher of the Source(s), Publisher can have multiple contacts.
    """
    name = models.CharField(_('Name'), max_length=150)

    objects = ContractManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = _('Publisher')
        verbose_name_plural = _('Publishers')

    def __str__(self):
        return self.name

    def search_blob(self):
        """
        :return: Search blob to be indexed in elastic
        """
        return self.name

    def get_absolute_url(self):
        return reverse('publishers:detail', kwargs={'pk': self.id})


@revisions.register(exclude=('last_changed',))
class ContactPerson(BaseModel):
    """
        Bigger publishers with a lot of source might have different people
        handling different sources.
    """
    publisher = models.ForeignKey(Publisher, on_delete=models.DO_NOTHING)

    name = models.CharField(_('Name'), max_length=256, blank=True, null=True)
    email = models.EmailField(_('E-mail'))
    phone = models.CharField(_('Phone'), blank=True, null=True, max_length=128)
    address = models.TextField(_('Address'), blank=True, null=True)
    position = models.CharField(_('Position'), max_length=256,
                                blank=True, null=True)

    class Meta:
        verbose_name = _('Publisher contact')
        verbose_name_plural = _('Publisher contacts')

    def __str__(self):
        return self.name or self.email

    def search_blob(self):
        """
        :return: Search blob to be indexed in elastic
        """
        parts = [
            self.name,
            self.email,
            self.phone,
            self.address,
            self.position,
        ]
        return ' '.join(filter(None, parts))

    def get_absolute_url(self):
        return reverse('publishers:detail', kwargs={'pk': self.publisher.id})
