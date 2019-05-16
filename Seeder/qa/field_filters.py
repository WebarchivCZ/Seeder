from . import models

from core.custom_filters import BaseFilterSet


class QAFilter(BaseFilterSet):
    class Meta:
        model = models.QualityAssuranceCheck
        fields = [
            'checked_by',
            'content_changed',
            'technical_quality_changed',
            'source_action',
        ]
