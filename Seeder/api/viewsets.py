import serializers
import source

from rest_framework import viewsets
from rest_framework import mixins as rf_mixins


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CategorySerializer
    queryset = source.models.Category.objects.all()


class SourceViewSet(rf_mixins.RetrieveModelMixin, rf_mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    """
    Viewset that does not implement listing, deleting and creating of sources.
    """
    serializer_class = serializers.SourceSerializer
    queryset = source.models.Source.objects.all()
    http_method_names = ['get', 'put', 'head']
