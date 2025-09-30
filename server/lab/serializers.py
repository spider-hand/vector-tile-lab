from rest_framework import serializers
from .models import Dataset, Tileset


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ["id", "name", "geojson_file", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class TilesetSerializer(serializers.ModelSerializer):
    dataset_name = serializers.CharField(source="dataset.name", read_only=True)

    class Meta:
        model = Tileset
        fields = [
            "id",
            "dataset",
            "dataset_name",
            "name",
            "pmtiles_file",
            "status",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "dataset",
            "dataset_name",
            "name",
            "pmtiles_file",
            "status",
            "metadata",
            "created_at",
            "updated_at",
        ]
