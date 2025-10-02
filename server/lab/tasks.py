import subprocess
from celery import shared_task
import boto3
from environ import Env
import re
import redis
from pmtiles.reader import Reader, MmapSource
from .constants import TaskStatus
from .models import Dataset, Tileset

env = Env()
env.read_env()


def extract_pmtiles_metadata(pmtiles_path):
    """Extract metadata from PMTiles"""
    try:
        with open(pmtiles_path, "rb") as f:
            source = MmapSource(f)
            reader = Reader(source)

            header = reader.header()
            metadata = reader.metadata()
            return {
                "header": {
                    "min_zoom": header["min_zoom"],
                    "max_zoom": header["max_zoom"],
                    "bounds": [
                        header["min_lon_e7"] / 1e7,
                        header["min_lat_e7"] / 1e7,
                        header["max_lon_e7"] / 1e7,
                        header["max_lat_e7"] / 1e7,
                    ],
                    "center": [
                        header["center_lon_e7"] / 1e7,
                        header["center_lat_e7"] / 1e7,
                        header["center_zoom"],
                    ],
                },
                "metadata": metadata,
            }

    except Exception as e:
        print(f"Error extracting PMTiles metadata: {e}")
        return None


@shared_task
def process_uploaded_geojson(dataset_id, dataset_name):
    print(f"Start to process {dataset_name} ...")

    try:
        dataset = Dataset.objects.get(id=dataset_id)
    except Dataset.DoesNotExist:
        print(f"Dataset with id {dataset_id} does not exist")
        return

    tileset = Tileset.objects.create(
        dataset=dataset, name="default", status=TaskStatus.IN_PROGRESS, metadata={}
    )
    print(f"Created Tileset with id {tileset.id}")

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
        tileset.status = TaskStatus.FAILED
        tileset.save()
        print(f"Failed to download geojson from MinIO: {e}")
        return

    print(f"Running tippecanoe for {dataset_name} ...")

    local_pmtiles_path = f"/tmp/{dataset_name}.pmtiles"
    try:
        progress = subprocess.Popen(
            ["tippecanoe", "-o", local_pmtiles_path, "-f", local_geojson_path],
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
        print("Progress: 100%")
        print("Tippecanoe completed successfully.")

        # Extract metadata from generated PMTiles file
        print("Extracting metadata from PMTiles...")
        pmtiles_metadata = extract_pmtiles_metadata(local_pmtiles_path)

        if pmtiles_metadata:
            # Save metadata directly to tileset
            tileset.metadata = pmtiles_metadata
            tileset.save()
            print(f"Saved metadata to tileset {tileset.id}")
        else:
            print("No metadata found in PMTiles file")
    except subprocess.CalledProcessError as e:
        redis_client.hset(
            f"dataset:{dataset_id}",
            mapping={
                "status": TaskStatus.FAILED,
                "progress": last_progress,
            },
        )
        tileset.status = TaskStatus.FAILED
        tileset.save()
        print(f"Tippecanoe failed: {e.stderr}")
        return

    print("Uploading pmtiles to MinIO ...")

    pmtiles_object_name = f"datasets/pmtiles/{dataset_name}.pmtiles"
    try:
        s3.upload_file(local_pmtiles_path, minio_bucket, pmtiles_object_name)
        print(f"Uploaded {pmtiles_object_name} to MinIO bucket.")

        tileset.pmtiles_file.name = pmtiles_object_name
        tileset.status = TaskStatus.COMPLETED
        tileset.save()

        redis_client.hset(
            f"dataset:{dataset_id}",
            mapping={
                "status": TaskStatus.COMPLETED,
                "progress": 100,
            },
        )
        print(f"Updated Tileset {tileset.id} with completion status")
    except Exception as e:
        tileset.status = TaskStatus.FAILED
        tileset.save()
        print(f"Failed to upload pmtiles to MinIO: {e}")
