from rest_framework import routers
from .viewsets import CategoryViewSet

api_router = routers.SimpleRouter()
api_router.register('category', CategoryViewSet)
