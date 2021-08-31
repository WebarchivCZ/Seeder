from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from .models import (HarvestConfiguration)
from .serializers import HarvestConfigurationSerializer


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
