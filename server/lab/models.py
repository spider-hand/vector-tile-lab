from django.db import models


class Dataset(models.Model):
    name = models.CharField(max_length=255)

    geojson_file = models.FileField(upload_to="datasets/geojson/")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TileGeneration(models.Model):
    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE, related_name="tile_generations"
    )

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )

    tile_file = models.FileField(upload_to="datasets/tiles/")

    # TODO: Tippecanoe parameters

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
