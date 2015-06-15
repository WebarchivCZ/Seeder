import models

from core.utils import EmptyFilter


class SourceFilter(EmptyFilter):
    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'publisher', 'state',
                  'category', 'sub_category', 'suggested_by', 'created',
                  'last_changed')