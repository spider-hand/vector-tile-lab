from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Dataset, Tileset
from .serializers import DatasetSerializer, TilesetSerializer
from .filters import TilesetFilter
from drf_spectacular.utils import extend_schema
from .tasks import process_uploaded_geojson, generate_tileset_with_options
import redis
from .constants import TaskStatus
from .utils import s3_service
from botocore.exceptions import ClientError


class DatasetViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "geojson_file": {"type": "string", "format": "binary"},
                },
                "required": ["name", "geojson_file"],
            }
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        process_uploaded_geojson.delay(instance.id, instance.name)
        return instance

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "integer"},
                    "dataset_name": {"type": "string"},
                    "progress": {"type": "integer", "minimum": 0, "maximum": 100},
                    "status": {"type": "string", "enum": [s.value for s in TaskStatus]},
                },
                "required": ["dataset_id", "dataset_name", "progress", "status"],
            },
            500: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        summary="Get dataset processing progress",
        description="Retrieves the current processing progress for a specific dataset from Redis cache.",
    )
    @action(detail=True, methods=["get"])
    def progress(self, request, pk=None):
        """Get the current processing progress for a dataset."""
        dataset = self.get_object()

        try:
            redis_client = redis.Redis(host="redis", port=6379, db=0)
            progress_key = f"dataset:{dataset.id}"
            progress_obj = redis_client.hgetall(progress_key)

            if not progress_obj:
                progress_percent = 0
                progress_status = TaskStatus.IN_PROGRESS
            else:
                data = {k.decode(): v.decode() for k, v in progress_obj.items()}
                progress_percent = int(data.get("progress", 0))
                progress_status = data.get("status", TaskStatus.IN_PROGRESS)

            return Response(
                {
                    "dataset_id": dataset.id,
                    "dataset_name": dataset.name,
                    "progress": progress_percent,
                    "status": progress_status,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve progress: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TilesetViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Tileset.objects.all()
    serializer_class = TilesetSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TilesetFilter

    def get_queryset(self):
        dataset_id = self.kwargs.get("dataset_id")
        if dataset_id:
            return Tileset.objects.filter(dataset_id=dataset_id)
        return Tileset.objects.all()

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name for the new tileset",
                    },
                    "max_zoom": {
                        "type": "string",
                        "description": "Maximum zoom level (0-22 or 'g' for guess)",
                        "default": "g",
                    },
                    "drop_densest": {
                        "type": "boolean",
                        "description": "Whether to drop densest as needed",
                        "default": True,
                    },
                },
                "required": ["name"],
            }
        },
        responses={
            201: TilesetSerializer,
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
            404: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    )
    def create(self, request, *args, **kwargs):
        """Create a new tileset with custom tippecanoe options."""
        dataset_id = self.kwargs.get("dataset_id")
        if not dataset_id:
            return Response(
                {"error": "Dataset ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except Dataset.DoesNotExist:
            return Response(
                {"error": "Dataset not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        name = request.data.get("name")
        max_zoom = request.data.get("max_zoom", "g")
        drop_densest = request.data.get("drop_densest", True)

        if not name:
            return Response(
                {"error": "Tileset name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if max_zoom != "g":
            try:
                zoom_int = int(max_zoom)
                if zoom_int < 0 or zoom_int > 22:
                    return Response(
                        {"error": "max_zoom must be between 0-22 or 'g'"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except ValueError:
                return Response(
                    {"error": "max_zoom must be a number between 0-22 or 'g'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        tileset = Tileset.objects.create(
            dataset=dataset,
            name=name,
            status=TaskStatus.IN_PROGRESS,
            metadata={},
        )

        generate_tileset_with_options.delay(
            dataset.name,
            tileset.id,
            name,
            max_zoom,
            drop_densest,
        )

        serializer = self.get_serializer(tileset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "tileset_id": {"type": "integer"},
                    "tileset_name": {"type": "string"},
                    "progress": {"type": "integer", "minimum": 0, "maximum": 100},
                    "status": {"type": "string", "enum": [s.value for s in TaskStatus]},
                },
                "required": ["tileset_id", "tileset_name", "progress", "status"],
            },
            500: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        summary="Get tileset generation progress",
        description="Retrieves the current generation progress for a specific tileset from Redis cache.",
    )
    @action(detail=True, methods=["get"])
    def progress(self, request, pk=None, dataset_id=None):
        """Get the current generation progress for a tileset."""
        tileset = self.get_object()

        try:
            redis_client = redis.Redis(host="redis", port=6379, db=0)
            progress_key = f"tileset:{tileset.id}"
            progress_obj = redis_client.hgetall(progress_key)

            if not progress_obj:
                progress_percent = 0
                progress_status = tileset.status
            else:
                data = {k.decode(): v.decode() for k, v in progress_obj.items()}
                progress_percent = int(data.get("progress", 0))
                progress_status = data.get("status", tileset.status)

            return Response(
                {
                    "tileset_id": tileset.id,
                    "tileset_name": tileset.name,
                    "progress": progress_percent,
                    "status": progress_status,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve progress: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "presigned_url": {"type": "string", "format": "uri"},
                    "expires_in": {
                        "type": "integer",
                        "description": "URL expiration time in seconds",
                    },
                },
                "required": ["presigned_url", "expires_in"],
            },
            404: {"type": "object", "properties": {"error": {"type": "string"}}},
            500: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        summary="Get presigned URL for PMTiles file",
        description="Generate a presigned URL to access the PMTiles file directly from MinIO/S3 storage.",
    )
    @action(detail=True, methods=["get"])
    def presigned_url(self, request, pk=None, dataset_id=None):
        """Generate a presigned URL for accessing the tileset's PMTiles file."""
        tileset = self.get_object()

        # Check if tileset has a PMTiles file and is completed
        if not tileset.pmtiles_file or tileset.status != TaskStatus.COMPLETED:
            return Response(
                {"error": "Tileset is not completed or PMTiles file is not available"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # Extract the object key from the file path
            object_key = tileset.pmtiles_file.name

            # Check if the file exists in S3
            if not s3_service.check_object_exists(object_key):
                return Response(
                    {"error": "PMTiles file not found in storage"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Generate presigned URL
            expires_in = 3600
            presigned_url = s3_service.generate_presigned_url(object_key, expires_in)

            return Response(
                {
                    "presigned_url": presigned_url,
                    "expires_in": expires_in,
                    "object_key": object_key,
                }
            )

        except ClientError as e:
            return Response(
                {"error": f"Failed to generate presigned URL: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
