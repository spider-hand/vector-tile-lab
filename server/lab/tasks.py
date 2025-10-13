import subprocess
import os
import shutil
from celery import shared_task
import re
import redis
from pmtiles.reader import Reader, MmapSource
from .constants import TaskStatus
from .models import Dataset, Tileset
from .utils import s3_service


def get_redis_client():
    return redis.Redis(host="redis", port=6379, db=0)


def run_tippecanoe_with_progress(
    geojson_path, output_path, redis_key, additional_options=None
):
    redis_client = get_redis_client()

    cmd = ["tippecanoe", "-o", output_path, "-f"]

    if additional_options:
        cmd.extend(additional_options)

    cmd.append(geojson_path)

    try:
        progress = subprocess.Popen(
            cmd,
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
                            redis_key,
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
        return True

    except subprocess.CalledProcessError as e:
        redis_client.hset(
            redis_key,
            mapping={
                "status": TaskStatus.FAILED,
                "progress": last_progress,
            },
        )
        print(f"Tippecanoe failed: {e.stderr}")
        return False


def extract_pmtiles_metadata(pmtiles_path):
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


def upload_pmtiles_to_minio(local_path, object_name):
    try:
        s3_service.internal_client.upload_file(
            local_path, s3_service.bucket_name, object_name
        )
        print(f"Uploaded {object_name} to MinIO bucket.")
        return True
    except Exception as e:
        print(f"Failed to upload pmtiles to MinIO: {e}")
        return False


@shared_task
def generate_tileset_with_options(
    dataset_name,
    tileset_id,
    tileset_name,
    max_zoom="g",
    drop_densest=True,
):
    print(f"Start to generate tileset '{tileset_name}' ...")

    try:
        tileset = Tileset.objects.get(id=tileset_id)
    except Tileset.DoesNotExist:
        print(f"Tileset with id {tileset_id} does not exist")
        return

    redis_client = get_redis_client()

    redis_key = f"tileset:{tileset.id}"
    geojson_object_name = f"datasets/geojson/{dataset_name}.geojson"
    local_geojson_path = f"/tmp/{dataset_name}.geojson"
    local_pmtiles_path = f"/tmp/{tileset_name}_{tileset.id}.pmtiles"

    # Download GeoJSON from MinIO
    try:
        s3_service.internal_client.download_file(
            s3_service.bucket_name, geojson_object_name, local_geojson_path
        )
        print(f"Downloaded {geojson_object_name} from MinIO bucket.")
    except Exception as e:
        redis_client.hset(
            redis_key,
            mapping={
                "status": TaskStatus.FAILED,
                "progress": 0,
            },
        )
        tileset.status = TaskStatus.FAILED
        tileset.save()
        print(f"Failed to download geojson from MinIO: {e}")
        return

    # Prepare tippecanoe options
    print(
        f"Running tippecanoe for {tileset_name} with options: --maximum_zoom={max_zoom}, --drop-densest-as-needed={drop_densest}"
    )

    additional_options = ["--maximum-zoom", str(max_zoom)]
    if drop_densest:
        additional_options.append("--drop-densest-as-needed")

    # Run tippecanoe with progress tracking
    success = run_tippecanoe_with_progress(
        local_geojson_path, local_pmtiles_path, redis_key, additional_options
    )

    if not success:
        tileset.status = TaskStatus.FAILED
        tileset.save()
        return

    # Extract and save metadata
    print("Extracting metadata from PMTiles...")
    pmtiles_metadata = extract_pmtiles_metadata(local_pmtiles_path)

    if pmtiles_metadata:
        tileset.metadata = pmtiles_metadata
        tileset.save()
        print(f"Saved metadata to tileset {tileset.id}")
    else:
        print("No metadata found in PMTiles file")

    # Upload to MinIO
    print("Uploading pmtiles to MinIO ...")
    pmtiles_object_name = f"datasets/pmtiles/{tileset_name}_{tileset.id}.pmtiles"

    if upload_pmtiles_to_minio(local_pmtiles_path, pmtiles_object_name):
        tileset.pmtiles_file.name = pmtiles_object_name
        tileset.status = TaskStatus.COMPLETED
        tileset.save()

        redis_client.hset(
            redis_key,
            mapping={
                "status": TaskStatus.COMPLETED,
                "progress": 100,
            },
        )
        print(f"Updated Tileset {tileset.id} with completion status")
    else:
        tileset.status = TaskStatus.FAILED
        tileset.save()


@shared_task
def process_uploaded_shapefile(dataset_id, dataset_name):
    """
    Process uploaded shapefile components by converting them to GeoJSON,
    then calling the existing GeoJSON processing workflow.
    """
    print(f"Start to process shapefile {dataset_name} ...")

    try:
        dataset = Dataset.objects.get(id=dataset_id)
    except Dataset.DoesNotExist:
        print(f"Dataset with id {dataset_id} does not exist")
        return

    redis_client = get_redis_client()
    redis_key = f"dataset:{dataset_id}"

    redis_client.hset(
        redis_key,
        mapping={
            "status": TaskStatus.IN_PROGRESS,
            "progress": 0,
        },
    )

    temp_dir = f"/tmp/shapefile_{dataset_id}"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        shapefile_components = {
            "shp": dataset.shp_file,
            "shx": dataset.shx_file,
            "dbf": dataset.dbf_file,
            "prj": dataset.prj_file,
            "cpg": dataset.cpg_file,
        }

        downloaded_files = {}

        for ext, file_field in shapefile_components.items():
            if file_field:
                object_name = file_field.name
                local_path = os.path.join(temp_dir, f"{dataset_name}.{ext}")

                try:
                    s3_service.internal_client.download_file(
                        s3_service.bucket_name, object_name, local_path
                    )
                    downloaded_files[ext] = local_path
                except Exception as e:
                    print(f"Failed to download {object_name}: {e}")
                    if ext in ["shp", "shx", "dbf"]:
                        raise e

        # Convert shapefile to GeoJSON
        shp_path = downloaded_files["shp"]
        geojson_path = f"/tmp/{dataset_name}.geojson"

        print("Converting shapefile to GeoJSON ...")

        ogr2ogr_cmd = ["ogr2ogr", "-f", "GeoJSON", geojson_path, shp_path]

        result = subprocess.run(
            ogr2ogr_cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            raise Exception(f"ogr2ogr failed: {result.stderr}")

        print("Successfully converted shapefile to GeoJSON")

        print("Uploading converted GeoJSON to MinIO ...")

        # Upload the converted GeoJSON to MinIO
        geojson_object_name = f"datasets/geojson/{dataset_name}.geojson"

        try:
            s3_service.internal_client.upload_file(
                geojson_path, s3_service.bucket_name, geojson_object_name
            )
            print("Uploaded converted GeoJSON to MinIO")

            dataset.geojson_file.name = geojson_object_name
            dataset.save()

        except Exception as e:
            raise Exception(f"Failed to upload converted GeoJSON to MinIO: {e}")

        # Clean up temporary files
        try:
            shutil.rmtree(temp_dir)
            os.remove(geojson_path)
        except Exception as e:
            print(f"Warning: Failed to clean up temporary files: {e}")

        process_uploaded_geojson.delay(dataset_id, dataset_name)

    except Exception as e:
        print(f"Error processing shapefile: {e}")
        redis_client.hset(
            redis_key,
            mapping={
                "status": TaskStatus.FAILED,
                "progress": 0,
            },
        )

        # Clean up on error
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as cleanup_error:
            print(f"Failed to clean up after error: {cleanup_error}")


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

    redis_client = get_redis_client()
    redis_key = f"dataset:{dataset_id}"

    geojson_object_name = f"datasets/geojson/{dataset_name}.geojson"
    local_geojson_path = f"/tmp/{dataset_name}.geojson"
    local_pmtiles_path = f"/tmp/{dataset_name}.pmtiles"

    # Download GeoJSON from MinIO
    try:
        s3_service.internal_client.download_file(
            s3_service.bucket_name, geojson_object_name, local_geojson_path
        )
        print(f"Downloaded {geojson_object_name} from MinIO bucket.")
    except Exception as e:
        redis_client.hset(
            redis_key,
            mapping={
                "status": TaskStatus.FAILED,
                "progress": 0,
            },
        )
        tileset.status = TaskStatus.FAILED
        tileset.save()
        print(f"Failed to download geojson from MinIO: {e}")
        return

    # Run tippecanoe with progress tracking with default options
    print(f"Running tippecanoe for {dataset_name} ...")

    success = run_tippecanoe_with_progress(
        local_geojson_path, local_pmtiles_path, redis_key, additional_options=None
    )

    if not success:
        tileset.status = TaskStatus.FAILED
        tileset.save()
        return

    # Extract and save metadata
    print("Extracting metadata from PMTiles...")
    pmtiles_metadata = extract_pmtiles_metadata(local_pmtiles_path)

    if pmtiles_metadata:
        tileset.metadata = pmtiles_metadata
        tileset.save()
        print(f"Saved metadata to tileset {tileset.id}")
    else:
        print("No metadata found in PMTiles file")

    # Upload to MinIO
    print("Uploading pmtiles to MinIO ...")
    pmtiles_object_name = f"datasets/pmtiles/{dataset_name}.pmtiles"

    if upload_pmtiles_to_minio(local_pmtiles_path, pmtiles_object_name):
        tileset.pmtiles_file.name = pmtiles_object_name
        tileset.status = TaskStatus.COMPLETED
        tileset.save()

        redis_client.hset(
            redis_key,
            mapping={
                "status": TaskStatus.COMPLETED,
                "progress": 100,
            },
        )
        print(f"Updated Tileset {tileset.id} with completion status")
    else:
        tileset.status = TaskStatus.FAILED
        tileset.save()
