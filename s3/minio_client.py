from minio import Minio
import os

minio_client = Minio(
    "minio:9000",
    access_key="JNiopcwgmzM0JLlzUpUK",
    secret_key="nUCXfaeV6VYT0ajVDqk3JD4638JBhecbPUpUGGay",
    secure=False
)

if not minio_client.bucket_exists("memes"):
    minio_client.make_bucket("memes")
