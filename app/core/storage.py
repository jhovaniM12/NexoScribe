import os
from pathlib import Path
from datetime import timedelta

from google.cloud import storage

from app.core.config import settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_google_credentials_path() -> str | None:
    if settings.google_application_credentials is None:
      return None

    credentials_path = Path(settings.google_application_credentials)

    if not credentials_path.is_absolute():
        credentials_path = PROJECT_ROOT / credentials_path

    return str(credentials_path)


def get_storage_client() -> storage.Client:
    credentials_path = get_google_credentials_path()

    if credentials_path is not None:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    return storage.Client()


def upload_bytes_to_gcs(
    *,
    file_bytes: bytes,
    destination_blob_name: str,
    content_type: str,
  ) -> str:
    client = get_storage_client()
    bucket = client.bucket(settings.gcs_bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(
        file_bytes,
        content_type=content_type,
      )

    return f"https://storage.googleapis.com/{settings.gcs_bucket_name}/{destination_blob_name}"


def get_gcs_blob_name_from_reference(reference: str) -> str:
    public_url_prefix = f"https://storage.googleapis.com/{settings.gcs_bucket_name}/"
    gs_url_prefix = f"gs://{settings.gcs_bucket_name}/"

    if reference.startswith(public_url_prefix):
        return reference.removeprefix(public_url_prefix)

    if reference.startswith(gs_url_prefix):
        return reference.removeprefix(gs_url_prefix)

    return reference


def create_signed_gcs_url(
    *,
    blob_reference: str,
    expiration_minutes: int,
) -> str:
    client = get_storage_client()
    bucket = client.bucket(settings.gcs_bucket_name)
    blob_name = get_gcs_blob_name_from_reference(blob_reference)
    blob = bucket.blob(blob_name)

    return blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET",
    )
