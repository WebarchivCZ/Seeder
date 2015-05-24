import models

from core.utils import EmptyFilter


class SourceFilter(EmptyFilter):
    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'web_proposal', 'publisher', 'state',
                  'conspectus', 'sub_conspectus', 'created',  'last_changed')