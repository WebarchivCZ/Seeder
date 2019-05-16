from . import models
from core.custom_filters import EmptyFilter


class TopicCollectionFilter(EmptyFilter):
    class Meta:
        model = models.TopicCollection
        fields = {
            'status': ('exact',),
            'title': ('icontains',),
        }
