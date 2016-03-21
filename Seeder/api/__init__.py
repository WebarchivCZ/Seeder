import viewsets

from rest_framework import routers


api_router = routers.SimpleRouter()
api_router.register('category', viewsets.CategoryViewSet)
api_router.register('source', viewsets.SourceViewSet)
api_router.register('seed', viewsets.SeedViewSet)
