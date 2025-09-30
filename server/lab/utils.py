import boto3
from environ import Env
from botocore.exceptions import ClientError


class S3Service:
    def __init__(self):
        self.env = Env()
        self.env.read_env()

        self.access_key = self.env.str("MINIO_ROOT_USER", default="minio")
        self.secret_key = self.env.str("MINIO_ROOT_PASSWORD", default="minio123")
        self.bucket_name = self.env.str("MINIO_BUCKET_NAME", default="vector-tile-lab")
        self.url_protocol = self.env.str("MINIO_URL_PROTOCOL", default="http:")
        self.internal_endpoint = self.env.str(
            "MINIO_ENDPOINT_URL", default="http://vector-tile-lab-storage:9000"
        )
        self.external_endpoint = self.env.str(
            "MINIO_EXTERNAL_ENDPOINT", default="localhost:9000"
        )

        self._internal_client = None
        self._external_client = None

    @property
    def internal_client(self):
        """Client for internal operations using Docker network"""
        if self._internal_client is None:
            self._internal_client = boto3.client(
                "s3",
                endpoint_url=self.internal_endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
        return self._internal_client

    @property
    def external_client(self):
        """Client for generating presigned URLs accessible from outside Docker"""
        if self._external_client is None:
            self._external_client = boto3.client(
                "s3",
                endpoint_url=f"{self.url_protocol}//{self.external_endpoint}",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
        return self._external_client

    @property
    def client(self):
        """Backward compatibility - returns internal client"""
        return self.internal_client

    def generate_presigned_url(self, object_key, expires_in=3600):
        """Generate presigned URL using external endpoint for client access"""
        try:
            presigned_url = self.external_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_key},
                ExpiresIn=expires_in,
            )
            return presigned_url
        except ClientError as e:
            raise ClientError(f"Failed to generate presigned URL: {str(e)}")

    def check_object_exists(self, object_key):
        """Check if object exists using internal endpoint"""
        try:
            self.internal_client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError:
            return False


s3_service = S3Service()
