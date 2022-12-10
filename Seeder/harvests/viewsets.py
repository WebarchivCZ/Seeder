from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from .models import (HarvestConfiguration, ExternalTopicCollection)
from .serializers import (HarvestConfigurationSerializer,
                          ExternalTopicCollectionTitleSerializer)


class HarvestConfigurationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Meant for logged in users, accessed with AJAX based on harvest_type
    """
    serializer_class = HarvestConfigurationSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = HarvestConfiguration.objects.all()
        # Lower string just in case
        harvest_type = str(self.request.GET.get("harvest_type", "")).lower()
        if len(harvest_type) > 0:
            qs = qs.filter(harvest_type=harvest_type)
        return qs


class ExternalTopicCollectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Internal use to retrieve External TC titles etc.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ExternalTopicCollection.objects.all()

    @action(methods=["get"], detail=True)
    def title(self, request, pk=None):
        obj = self.get_object()
        return Response(ExternalTopicCollectionTitleSerializer(obj).data)
