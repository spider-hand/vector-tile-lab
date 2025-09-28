from django.db import models


class Dataset(models.Model):
    name = models.CharField(max_length=255)
    geojson_file = models.FileField(upload_to="datasets/geojson/")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
