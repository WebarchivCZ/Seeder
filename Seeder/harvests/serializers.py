from rest_framework import serializers
from .models import (HarvestConfiguration)


class HarvestConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HarvestConfiguration
        fields = (
            "harvest_type",
            "duration",
            "budget",
            "dataLimit",
            "documentLimit",
            "deduplication",
        )
