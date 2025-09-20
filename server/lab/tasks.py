from celery import shared_task


@shared_task
def process_uploaded_geojson(dataset_name):
    print(f"Start to process {dataset_name} ...")
    return f"Start to process {dataset_name} ..."
