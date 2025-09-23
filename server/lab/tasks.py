import subprocess
from celery import shared_task
import boto3
from environ import Env

env = Env()
env.read_env()


@shared_task
def process_uploaded_geojson(dataset_name):
    print(f"Start to process {dataset_name} ...")

    minio_access_key = env.str("MINIO_ROOT_USER", default="minio")
    minio_secret_key = env.str("MINIO_ROOT_PASSWORD", default="minio123")
    minio_bucket = env.str("MINIO_BUCKET_NAME", default="vector-tile-lab-storage")
    minio_endpoint = env.str("MINIO_ENDPOINT_URL", default=None)

    s3 = boto3.client(
        "s3",
        endpoint_url=minio_endpoint,
        aws_access_key_id=minio_access_key,
        aws_secret_access_key=minio_secret_key,
    )
    geojson_object_name = f"datasets/geojson/{dataset_name}.geojson"
    local_geojson_path = f"/tmp/{dataset_name}.geojson"
    try:
        s3.download_file(minio_bucket, geojson_object_name, local_geojson_path)
        print(f"Downloaded {geojson_object_name} from MinIO bucket.")
    except Exception as e:
        print(f"Failed to download geojson from MinIO: {e}")
        return

    print(f"Running tippecanoe for {dataset_name} ...")

    local_mbtiles_path = f"/tmp/{dataset_name}.mbtiles"
    try:
        subprocess.run(
            ["tippecanoe", "-o", local_mbtiles_path, local_geojson_path],
            capture_output=True,
            text=True,
            check=True,
        )
        print("Tippecanoe completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Tippecanoe failed: {e.stderr}")
        return

    print("Uploading mbtiles to MinIO ...")

    mbtiles_object_name = f"datasets/tiles/{dataset_name}.mbtiles"
    try:
        s3.upload_file(local_mbtiles_path, minio_bucket, mbtiles_object_name)
        print(f"Uploaded {mbtiles_object_name} to MinIO bucket.")
    except Exception as e:
        print(f"Failed to upload mbtiles to MinIO: {e}")
