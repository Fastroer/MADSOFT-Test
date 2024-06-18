import os
from minio import Minio

MINIO_URL = os.getenv("MINIO_URL", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "P3EsC8v7iXIQoUmbI2iu")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "SSvfCilnm48t5Vri83B67HOHiUwSx6znQW6heL3J")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "memes")

minio_client = Minio(
    MINIO_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)
