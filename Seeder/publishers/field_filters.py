from . import models

from core.custom_filters import EmptyFilter


class PublisherFilter(EmptyFilter):
    class Meta:
        model = models.Publisher
        fields = ('name',)
