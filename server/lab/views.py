from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import Dataset
from .serializers import DatasetSerializer
from drf_spectacular.utils import extend_schema
from .tasks import process_uploaded_geojson
import redis
from .constants import TaskStatus


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
