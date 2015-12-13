from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel


class QualityAssuranceCheck(BaseModel):
    checked_by = models.ForeignKey(User)
    result_score = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)

    