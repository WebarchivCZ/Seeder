from . import models

from core.custom_filters import BaseFilterSet


class QAFilter(BaseFilterSet):
    class Meta:
        model = models.QualityAssuranceCheck
        fields = {
            'source__name': ('icontains',),
            'checked_by': ('exact',),
            'content_changed': ('exact',),
            'technical_quality_changed': ('exact',),
            'source_action': ('exact',),
        }
