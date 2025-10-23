from rest_framework import serializers
from .models import Dataset, Tileset, TierList


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = [
            "id",
            "name",
            "geojson_file",
            "shp_file",
            "shx_file",
            "dbf_file",
            "prj_file",
            "cpg_file",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        """
        Validate that either geojson_file OR all required shapefile components are provided
        """
        geojson_file = data.get("geojson_file")
        shp_file = data.get("shp_file")
        shx_file = data.get("shx_file")
        dbf_file = data.get("dbf_file")

        has_geojson = geojson_file is not None
        has_required_shp = all([shp_file, shx_file, dbf_file])

        if not has_geojson and not has_required_shp:
            raise serializers.ValidationError(
                "Either 'geojson_file' or all required shapefile components "
                "('shp_file', 'shx_file', 'dbf_file') must be provided."
            )

        if has_geojson and has_required_shp:
            raise serializers.ValidationError(
                "Please provide either 'geojson_file' OR shapefile components, not both."
            )

        if has_required_shp:
            self._validate_shapefile_extensions(data)

        if has_geojson:
            self._validate_geojson_extension(geojson_file)

        return data

    def _validate_shapefile_extensions(self, data):
        file_validations = {
            "shp_file": [".shp"],
            "shx_file": [".shx"],
            "dbf_file": [".dbf"],
            "prj_file": [".prj"],
            "cpg_file": [".cpg"],
        }

        for field_name, valid_extensions in file_validations.items():
            file_obj = data.get(field_name)
            if file_obj:
                filename = file_obj.name.lower()
                if not any(filename.endswith(ext) for ext in valid_extensions):
                    raise serializers.ValidationError(
                        {
                            field_name: f"File must have one of these extensions: {', '.join(valid_extensions)}"
                        }
                    )

    def _validate_geojson_extension(self, geojson_file):
        filename = geojson_file.name.lower()
        if not (filename.endswith(".geojson") or filename.endswith(".json")):
            raise serializers.ValidationError(
                {"geojson_file": "File must have .geojson or .json extension"}
            )


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


class TierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TierList
        fields = [
            "id",
            "dataset",
            "field",
            "method",
            "breaks",
        ]
        read_only_fields = [
            "id",
            "dataset",
            "field",
            "method",
            "breaks",
        ]
