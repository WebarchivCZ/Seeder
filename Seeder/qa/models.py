from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import BaseModel
from source.models import Source
from source import constants as source_constants


class QualityAssuranceCheck(BaseModel):
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

    comment = models.TextField(
        verbose_name=_('Comment'),
        blank=True)

    source_action = models.CharField(
        verbose_name=_('Resulting action'),
        max_length=15,
        choices=source_constants.SOURCE_STATES)

    technician_required = models.BooleanField(default=False)
    check_after_days = models.PositiveIntegerField(
        verbose_name=_('Check after days'),
        null=True
    )
