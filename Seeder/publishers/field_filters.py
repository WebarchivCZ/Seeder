import django_filters
import models


class PublisherFilter(django_filters.FilterSet):
    class Meta:
        model = models.Publisher
        fields = ('name', 'website', 'email', 'phone')
