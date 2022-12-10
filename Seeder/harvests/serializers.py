from rest_framework import serializers
from .models import (HarvestConfiguration, ExternalTopicCollection)


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


class ExternalTopicCollectionTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalTopicCollection
        fields = ("title", "title_cs", "title_en")
