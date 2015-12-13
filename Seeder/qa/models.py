from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel
from source.models import Source


class QualityAssuranceCheck(BaseModel):
    source = models.ForeignKey(Source)

    checked_by = models.ForeignKey(User)
    result_score = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
