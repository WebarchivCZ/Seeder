from . import models

from core.custom_filters import EmptyFilter


class NewsFilter(EmptyFilter):
    class Meta:
        model = models.NewsObject
        fields = {
            'title': ('icontains',),
        }
