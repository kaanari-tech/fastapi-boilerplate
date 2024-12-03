import io
import json
import re
import uuid
from abc import ABC
from abc import abstractmethod
from typing import Any

import boto3

# from google.cloud import storage
from minio import Minio
from minio.error import S3Error

from backend.core.conf import settings



class CloudStorage(ABC):
    @abstractmethod
    def upload_file(self, file_content: bytes, filename: str) -> Any:
        pass

    @abstractmethod
    def delete_file(self, identifier: str) -> None:
        pass


# GCS ( Google Cloud Storage)
# class GoogleCloudStorage(CloudStorage):
#     def __init__(self, bucket_name):
#         self.bucket_name = bucket_name
#         self.client = storage.Client()

#     def upload_file(self, file_content: bytes, filename: str) -> str:
#         bucket = self.client.get_bucket(self.bucket_name)
#         blob = bucket.blob(filename)
#         blob.upload_from_string(file_content)
#         return blob.public_url

#     def delete_file(self, filename: str) -> None:
#         blob = self.client.get_bucket(self.bucket_name).blob(filename)
#         blob.delete()


# Amazon S3
class AmazonS3Storage(CloudStorage):
    def __init__(
        self, bucket_name, aws_access_key_id, aws_secret_access_key, region_name
    ):
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    def upload_file(self, file_content: bytes, filename: str) -> str:
        self.s3.upload_fileobj(file_content, self.bucket_name, filename)
        file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{filename}"
        return file_url

    def delete_file(self, filename: str) -> None:
        self.s3.delete_object(Bucket=self.bucket_name, Key=filename)


# Cloudinary
# class CloudinaryStorage(CloudStorage):
#     def __init__(self, cloud_name, api_key, api_secret):
#         cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)

#     def upload_file(self, file_content: bytes, filename: str) -> Any:
#         result = uploader.upload(
#             file_content,
#             folder="test",
#             resource_type="raw",
#             filename=filename,
#             use_filename=True,
#         )
#         return result

#     def delete_file(self, public_id: str) -> None:
#         uploader.destroy(public_id=public_id, resource_type="raw")


class MinioStorage(CloudStorage):
    def __init__(self, endpoint_url, access_key, secret_key, bucket_name):
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name

        # Initialisation du client MinIO
        self.client = Minio(
            endpoint=self.endpoint_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,  # En local, on utilise HTTP (pas HTTPS)
        )

        # Définition de la politique de bucket pour l'accès public en lecture
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
                }
            ],
        }

        # Vérification et configuration du bucket
        try:
            if not self.client.bucket_exists(bucket_name):
                # Création du bucket
                self.client.make_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' created successfully.")

                # Application de la politique d'accès public
                self.client.set_bucket_policy(bucket_name, json.dumps(policy))
                print(f"Public access policy applied to bucket '{bucket_name}'.")
            else:
                print(f"Bucket '{bucket_name}' already exists.")

        except S3Error as e:
            print(f"Error occurred: {e}")

    def exists(self, filename: str) -> bool:
        try:
            self.client.stat_object(self.bucket_name, filename)
            return True
        except S3Error:
            return False

    def generate_filename(self, filename: str) -> str:

        filename, ext = filename.rsplit(".", 1)

        # Remplacer tous les caractères non alphanumériques (sauf les tirets bas) par des tirets bas
        refilename = re.sub(r"[^\w\-_()]+", "_", filename)
        finalefilename = f"{refilename}.{ext}"
        while self.exists(finalefilename):
            return self.generate_filename(f"{filename}_{uuid.uuid4()}.{ext}")
        return finalefilename

    def download_file(self, filename: str) -> bytes:
        obj = self.client.get_object(self.bucket_name, filename)
        return obj.read()

    def delete_file(self, filename: str) -> None:
        self.client.remove_object(self.bucket_name, filename)

    def list_files(self) -> list[str]:
        objects = self.client.list_objects(self.bucket_name)
        return [obj.object_name for obj in objects]

    def create_bucket(self) -> None:
        self.client.make_bucket(self.bucket_name)

    def delete_bucket(self) -> None:
        self.client.remove_bucket(self.bucket_name)

    def list_buckets(self) -> list[str]:
        buckets = self.client.list_buckets()
        return [bucket.name for bucket in buckets]

    def upload_file(self, file_content: bytes, filename: str) -> str:
        gen_filename = self.generate_filename(filename)
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=gen_filename,
            data=io.BytesIO(file_content),
            length=-1,
            part_size=100 * 1024 * 1024,
        )
        file_url = f"{settings.MINIO_CLOUD_URL}/{self.bucket_name}/{gen_filename}"
        return {"file_url": file_url, "filename": gen_filename}
