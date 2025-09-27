import subprocess
from celery import shared_task
import boto3
from environ import Env
import re
import redis
from .constants import TaskStatus

env = Env()
env.read_env()


@shared_task
def process_uploaded_geojson(dataset_id, dataset_name):
    print(f"Start to process {dataset_name} ...")

    minio_access_key = env.str("MINIO_ROOT_USER", default="minio")
    minio_secret_key = env.str("MINIO_ROOT_PASSWORD", default="minio123")
    minio_bucket = env.str("MINIO_BUCKET_NAME", default="vector-tile-lab-storage")
    minio_endpoint = env.str("MINIO_ENDPOINT_URL", default=None)

    redis_client = redis.Redis(host="redis", port=6379, db=0)

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
        redis_client.hset(
            f"dataset:{dataset_id}",
            mapping={
                "status": TaskStatus.FAILED,
                "progress": 0,
            },
        )
        print(f"Failed to download geojson from MinIO: {e}")
        return

    print(f"Running tippecanoe for {dataset_name} ...")

    local_mbtiles_path = f"/tmp/{dataset_name}.mbtiles"
    try:
        progress = subprocess.Popen(
            ["tippecanoe", "-o", local_mbtiles_path, "-f", local_geojson_path],
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        buffer = ""
        pattern = re.compile(r"(\d+(\.\d+)?)%")
        last_progress = 0
        collected_err = []

        while True:
            char = progress.stderr.read(1)
            if not char:
                break
            buffer += char

            if char in ["\n", "\r"]:
                line = buffer.strip()
                buffer = ""
                if not line:
                    continue

                collected_err.append(line)
                match = pattern.search(line)
                if match:
                    percentage = float(match.group(1))
                    rounded = int((percentage // 10) * 10)
                    if rounded > last_progress:
                        redis_client.hset(
                            f"dataset:{dataset_id}",
                            mapping={
                                "status": TaskStatus.IN_PROGRESS,
                                "progress": rounded,
                            },
                        )
                        print(f"Progress: {rounded}%")
                        last_progress = rounded

        progress.wait()
        if progress.returncode != 0:
            err_output = "\n".join(collected_err)
            raise subprocess.CalledProcessError(
                progress.returncode,
                progress.args,
                output=None,
                stderr=err_output,
            )
        redis_client.hset(
            f"dataset:{dataset_id}",
            mapping={
                "status": TaskStatus.COMPLETED,
                "progress": 100,
            },
        )
        print("Progress: 100%")
        print("Tippecanoe completed successfully.")
    except subprocess.CalledProcessError as e:
        redis_client.hset(
            f"dataset:{dataset_id}",
            mapping={
                "status": TaskStatus.FAILED,
                "progress": last_progress,
            },
        )
        print(f"Tippecanoe failed: {e.stderr}")
        return

    print("Uploading mbtiles to MinIO ...")

    mbtiles_object_name = f"datasets/tiles/{dataset_name}.mbtiles"
    try:
        s3.upload_file(local_mbtiles_path, minio_bucket, mbtiles_object_name)
        print(f"Uploaded {mbtiles_object_name} to MinIO bucket.")
    except Exception as e:
        print(f"Failed to upload mbtiles to MinIO: {e}")
