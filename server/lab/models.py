from django.db import models
from .constants import TASK_STATUS_CHOICES


class Dataset(models.Model):
    name = models.CharField(max_length=255)
    geojson_file = models.FileField(
        upload_to="datasets/geojson/", null=True, blank=True
    )

    shp_file = models.FileField(upload_to="datasets/shapefile/", null=True, blank=True)
    shx_file = models.FileField(upload_to="datasets/shapefile/", null=True, blank=True)
    dbf_file = models.FileField(upload_to="datasets/shapefile/", null=True, blank=True)
    prj_file = models.FileField(upload_to="datasets/shapefile/", null=True, blank=True)
    cpg_file = models.FileField(upload_to="datasets/shapefile/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Tileset(models.Model):
    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE, related_name="tilesets"
    )
    name = models.CharField(max_length=255)
    pmtiles_file = models.FileField(upload_to="datasets/pmtiles/")
    status = models.CharField(
        max_length=50, choices=TASK_STATUS_CHOICES, default=TASK_STATUS_CHOICES[0][0]
    )
    metadata = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
