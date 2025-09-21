import subprocess
from celery import shared_task


@shared_task
def process_uploaded_geojson(dataset_name):
    print(f"Start to process {dataset_name} ...")
    result = subprocess.run(["tippecanoe", "--version"], capture_output=True, text=True)
    print(result.stderr.strip())
