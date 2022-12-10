from . import viewsets
from harvests.viewsets import (
    HarvestConfigurationViewSet, ExternalTopicCollectionViewSet)

from rest_framework import routers


api_router = routers.SimpleRouter()
api_router.register('category', viewsets.CategoryViewSet)
api_router.register('source', viewsets.SourceViewSet)
api_router.register('seed', viewsets.SeedViewSet)
api_router.register('blacklist', viewsets.BlacklistViewSet)
api_router.register('harvest_config', HarvestConfigurationViewSet,
                    basename="harvest_config")
api_router.register('external_tc', ExternalTopicCollectionViewSet,
                    basename="external_tc")
