from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save

from core.models import BaseModel
from source.models import Source
from source import constants as source_constants
from search_blob.models import SearchModel, update_search


class QualityAssuranceCheck(SearchModel, BaseModel):
    """
    QA check, is considered open until source_action is filled.
    """
    source = models.ForeignKey(
        verbose_name=_('Source'),
        to=Source,
        on_delete=models.DO_NOTHING
    )

    checked_by = models.ForeignKey(
        verbose_name=_('Checked by'),
        to=User,
        on_delete=models.DO_NOTHING
    )

    content_changed = models.BooleanField(
        verbose_name=_('Content changed too much'),
        default=False,
    )

    technical_quality_changed = models.BooleanField(
        verbose_name=_('Technical side decreased too much'),
        default=False,
    )

    comment = models.TextField(
        verbose_name=_('Comment'),
        blank=True
    )

    source_action = models.CharField(
        verbose_name=_('Resulting action'),
        max_length=15,
        choices=source_constants.SOURCE_STATES,
        null=True,
        blank=True,
        help_text=_('This will close QA and act upon the source'),
    )

    class Meta:
        verbose_name = _('Quality assurance check')
        verbose_name_plural = _('Quality assurance checks')

    def __str__(self):
        return 'QA: {0}'.format(self.source)

    def get_search_blob(self):
        """
        :return: Search blob to be indexed in elastic
        """
        return self.comment

    def get_search_title(self):
        return self.__str__()

    def get_search_url(self):
        return self.get_detail_url()

    def process_action(self):
        if self.source_action:
            self.source.state = self.source_action
            self.source.save()

    def get_edit_url(self):
        return reverse('qa:edit', args=[str(self.id)])

    def get_detail_url(self):
        return reverse('qa:detail', args=[str(self.id)])

    def get_absolute_url(self):
        if self.source_action:
            return self.get_detail_url()
        return self.get_edit_url()

post_save.connect(update_search, sender=QualityAssuranceCheck)
