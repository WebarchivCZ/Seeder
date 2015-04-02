import models
import django_tables2 as tables


class SourceTable(tables.Table):
    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'created', 'last_changed', 'state',
                  'publisher', 'conspectus', 'sub_conspectus')
        attrs = {
            'class': 'table table-striped'
        }