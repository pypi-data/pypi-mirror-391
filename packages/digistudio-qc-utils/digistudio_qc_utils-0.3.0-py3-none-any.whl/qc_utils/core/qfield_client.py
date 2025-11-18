"""QFieldCloud client wrapper."""

import logging
import os
from pathlib import Path
from typing import Any

from qfieldcloud_sdk import sdk
from qfieldcloud_sdk.sdk import FileTransferType

logger = logging.getLogger(__name__)


class QFieldCloudClient:
    """Wrapper around QFieldCloud SDK for simplified operations."""

    def __init__(self, project_id: str):
        """
        Initialize QFieldCloud client.

        Args:
            project_id: QFieldCloud project ID
        """
        self.project_id = project_id
        self.client: sdk.Client | None = None

    def authenticate(self) -> None:
        """
        Authenticate to QFieldCloud using environment variables.

        Uses the following environment variables:
        - QFIELDCLOUD_URL: API URL (default: https://app.qfield.cloud/api/v1/)
        - QFIELDCLOUD_TOKEN: Authentication token (preferred)
        - QFIELDCLOUD_USERNAME: Username (if token not provided)
        - QFIELDCLOUD_PASSWORD: Password (if token not provided)

        Raises:
            ValueError: If authentication credentials are missing
        """
        url = os.environ.get("QFIELDCLOUD_URL", "https://app.qfield.cloud/api/v1/")
        token = os.environ.get("QFIELDCLOUD_TOKEN")
        username = os.environ.get("QFIELDCLOUD_USERNAME")
        password = os.environ.get("QFIELDCLOUD_PASSWORD")

        # Create client
        if token:
            logger.info("Authenticating with token")
            self.client = sdk.Client(url=url, token=token)
        else:
            self.client = sdk.Client(url=url)

        # Authenticate if needed
        if not self.client.token:
            if not username or not password:
                raise ValueError(
                    "Authentication required: set QFIELDCLOUD_TOKEN or "
                    "QFIELDCLOUD_USERNAME and QFIELDCLOUD_PASSWORD"
                )

            logger.info(f"Authenticating user {username}")
            self.client.login(username, password)
            logger.info("Authentication successful")

    def list_files(self, skip_metadata: bool = False) -> list[dict[str, Any]]:
        """
        List all files in the project.

        Args:
            skip_metadata: If True, skip fetching file metadata (faster)

        Returns:
            List of file metadata dictionaries

        Raises:
            RuntimeError: If client is not authenticated
        """
        if self.client is None:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")

        logger.info(f"Fetching file list for project {self.project_id}")
        files = self.client.list_remote_files(self.project_id, skip_metadata=skip_metadata)
        logger.info(f"Found {len(files)} files in project")
        return files

    def delete_files(
        self, file_names: list[str], throw_on_error: bool = False
    ) -> dict[str, Any]:
        """
        Delete files from the project.

        Args:
            file_names: List of file names to delete
            throw_on_error: If True, raise exception on deletion errors

        Returns:
            Dictionary with deletion results

        Raises:
            RuntimeError: If client is not authenticated
        """
        if self.client is None:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")

        logger.info(f"Deleting {len(file_names)} files from project {self.project_id}")

        result = self.client.delete_files(
            self.project_id, glob_patterns=file_names, throw_on_error=throw_on_error
        )

        # Count successes and failures
        success_count = 0
        failed_count = 0

        for pattern, pattern_files in result.items():
            for file in pattern_files:
                if file.get("status") == "SUCCESS":
                    success_count += 1
                else:
                    failed_count += 1
                    logger.error(f"Failed to delete {file['name']}: {file.get('error')}")

        logger.info(f"Deletion complete: {success_count} succeeded, {failed_count} failed")
        return result

    def download_file(self, file_name: str, local_path: str) -> None:
        """
        Download a file from the project.

        Args:
            file_name: Name of the file to download
            local_path: Local path where to save the file

        Raises:
            RuntimeError: If client is not authenticated
        """
        if self.client is None:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")

        logger.debug(f"Downloading {file_name} to {local_path}")
        self.client.download_file(
            self.project_id,
            remote_filename=Path(file_name),
            local_filename=Path(local_path),
            download_type=FileTransferType.PROJECT,
            show_progress=False,
        )
