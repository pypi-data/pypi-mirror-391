"""Google Cloud Storage client wrapper."""

import logging
from pathlib import Path

from google.cloud import storage
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


class GCPStorageClient:
    """Wrapper around Google Cloud Storage for simplified operations."""

    def __init__(self, auth_file: str):
        """
        Initialize GCP Storage client.

        Args:
            auth_file: Path to GCP service account JSON file

        Raises:
            FileNotFoundError: If auth file doesn't exist
            ValueError: If auth file is invalid
        """
        auth_path = Path(auth_file)
        if not auth_path.exists():
            raise FileNotFoundError(f"GCP auth file not found: {auth_file}")

        logger.info(f"Initializing GCP Storage client with {auth_file}")

        # Create credentials from service account file
        credentials = service_account.Credentials.from_service_account_file(auth_file)

        # Create storage client
        self.client = storage.Client(credentials=credentials, project=credentials.project_id)
        logger.info(f"GCP client initialized for project: {credentials.project_id}")

    def upload_file(
        self, local_path: str, bucket_name: str, destination_path: str
    ) -> None:
        """
        Upload a file to GCS bucket.

        Args:
            local_path: Local file path to upload
            bucket_name: GCS bucket name
            destination_path: Destination path in bucket (including filename)

        Raises:
            FileNotFoundError: If local file doesn't exist
            Exception: If upload fails
        """
        local_file = Path(local_path)
        if not local_file.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        logger.debug(f"Uploading {local_path} to gs://{bucket_name}/{destination_path}")

        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_path)

            # Upload with retry
            blob.upload_from_filename(local_path)

            logger.info(f"Uploaded {local_file.name} to gs://{bucket_name}/{destination_path}")
        except Exception as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            raise

    def file_exists(self, bucket_name: str, file_path: str) -> bool:
        """
        Check if a file exists in GCS bucket.

        Args:
            bucket_name: GCS bucket name
            file_path: File path in bucket

        Returns:
            True if file exists, False otherwise
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(file_path)
            return blob.exists()
        except Exception as e:
            logger.warning(f"Error checking if file exists: {e}")
            return False

    def list_files(self, bucket_name: str, prefix: str = "") -> list[str]:
        """
        List files in a GCS bucket.

        Args:
            bucket_name: GCS bucket name
            prefix: Optional prefix to filter files

        Returns:
            List of file paths in the bucket
        """
        logger.debug(f"Listing files in gs://{bucket_name}/{prefix}")

        try:
            bucket = self.client.bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            file_list = [blob.name for blob in blobs]
            logger.info(f"Found {len(file_list)} files in bucket")
            return file_list
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            raise
