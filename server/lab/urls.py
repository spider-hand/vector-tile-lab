from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatasetViewSet, TilesetViewSet

router = DefaultRouter()
router.register(r"datasets", DatasetViewSet)
router.register(r"tilesets", TilesetViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
