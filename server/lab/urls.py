from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatasetViewSet, TilesetViewSet

router = DefaultRouter()
router.register(r"datasets", DatasetViewSet)

# Manual nested routing for tilesets under datasets
urlpatterns = [
    path("", include(router.urls)),
    path(
        "datasets/<int:dataset_id>/tilesets/",
        TilesetViewSet.as_view({"get": "list"}),
        name="dataset-tilesets-list",
    ),
    path(
        "datasets/<int:dataset_id>/tilesets/<int:pk>/",
        TilesetViewSet.as_view({"get": "retrieve", "delete": "destroy"}),
        name="dataset-tilesets-detail",
    ),
    path(
        "datasets/<int:dataset_id>/tilesets/<int:pk>/presigned_url/",
        TilesetViewSet.as_view({"get": "presigned_url"}),
        name="dataset-tilesets-presigned-url",
    ),
]
