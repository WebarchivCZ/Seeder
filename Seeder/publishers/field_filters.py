import models
from core.utils import EmptyFilter


class PublisherFilter(EmptyFilter):
    class Meta:
        model = models.Publisher
        fields = ('name',)
