import serializers
import source

from rest_framework import viewsets
from rest_framework import mixins as rf_mixins


class CategoryViewSet(rf_mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.CategorySerializer
    queryset = source.models.Category.objects.all()


class SourceViewSet(rf_mixins.RetrieveModelMixin, rf_mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    """
    Viewset that does not implement listing, deleting and creating of sources.
    """
    serializer_class = serializers.SourceSerializer
    queryset = source.models.Source.objects.all()


class SeedViewSet(viewsets.GenericViewSet, rf_mixins.RetrieveModelMixin,
                rf_mixins.UpdateModelMixin):
    """
    Viewset for updating seeds
    """
    serializer_class = serializers.SeedSerializer
    queryset = source.models.Seed.objects.all()