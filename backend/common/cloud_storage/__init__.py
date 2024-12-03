from .cloud_storage import MinioStorage
from backend.core.conf import settings



mstorage = MinioStorage(
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    endpoint_url=settings.MINIO_ENDPOINT,
    bucket_name=settings.MINIO_BUCKET_NAME,
)
