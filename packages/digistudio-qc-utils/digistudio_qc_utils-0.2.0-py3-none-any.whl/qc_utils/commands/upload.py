"""Upload photos from QFieldCloud to GCP Storage."""

import logging
import tempfile
from pathlib import Path
from typing import Any

from qc_utils.core.filters import filter_files_by_pattern
from qc_utils.core.gcp_client import GCPStorageClient
from qc_utils.core.qfield_client import QFieldCloudClient

logger = logging.getLogger(__name__)


def run_upload(
    project_id: str,
    gcp_bucket: str,
    gcp_bucket_directory: str,
    gcp_auth_file: str,
    file_filter: str = "*.jpg",
) -> dict[str, Any]:
    """
    Upload photos from QFieldCloud to GCP Storage.

    Args:
        project_id: QFieldCloud project ID
        gcp_bucket: GCP bucket name
        gcp_bucket_directory: Directory path in GCP bucket
        gcp_auth_file: Path to GCP service account JSON file
        file_filter: Glob pattern for files to upload (default: *.jpg)

    Returns:
        Dictionary with operation results

    Raises:
        ValueError: If authentication fails
        RuntimeError: If operation fails
    """
    logger.info(f"Starting upload from QFieldCloud project {project_id}")
    logger.info(f"Target: gs://{gcp_bucket}/{gcp_bucket_directory}")
    logger.info(f"File filter: {file_filter}")

    # Initialize clients
    logger.info("Initializing QFieldCloud client...")
    qfield_client = QFieldCloudClient(project_id)
    qfield_client.authenticate()

    logger.info("Initializing GCP Storage client...")
    gcp_client = GCPStorageClient(gcp_auth_file)

    # List files from QFieldCloud
    print("\nAnalyzing files...")
    logger.info("Fetching file list from QFieldCloud...")
    all_files = qfield_client.list_files(skip_metadata=True)

    # Filter files by pattern
    qfield_files = filter_files_by_pattern(all_files, file_filter)
    logger.info(f"Found {len(qfield_files)} files matching '{file_filter}' in QFieldCloud")

    if not qfield_files:
        print(f"No files matching '{file_filter}' found in QFieldCloud project")
        return {"no_files": True}

    # List files from GCP bucket
    logger.info(f"Fetching file list from GCP bucket gs://{gcp_bucket}/{gcp_bucket_directory}")
    gcp_files = gcp_client.list_files(gcp_bucket, prefix=gcp_bucket_directory)
    logger.debug(f"GCP files (first 5): {gcp_files[:5]}")

    # Create a set of existing GCP relative paths (remove bucket directory prefix)
    # GCP returns: 'test-cli/DCIM/photo.jpg' -> we want: 'DCIM/photo.jpg'
    prefix_to_remove = gcp_bucket_directory.rstrip("/") + "/"
    gcp_relative_paths = set()
    for gcp_file in gcp_files:
        if gcp_file.startswith(prefix_to_remove):
            relative_path = gcp_file[len(prefix_to_remove) :]
            gcp_relative_paths.add(relative_path)
        elif gcp_file.startswith(gcp_bucket_directory):
            # Handle case without trailing slash
            relative_path = gcp_file[len(gcp_bucket_directory) :].lstrip("/")
            gcp_relative_paths.add(relative_path)

    logger.info(f"Found {len(gcp_relative_paths)} files in GCP bucket")
    logger.debug(f"GCP relative paths (first 5): {list(gcp_relative_paths)[:5]}")
    logger.debug(f"QField filenames (first 5): {[f['name'] for f in qfield_files[:5]]}")

    # Filter out files that already exist in GCP
    files_to_upload = [f for f in qfield_files if f["name"] not in gcp_relative_paths]

    # Display analysis summary
    print("\n" + "=" * 80)
    print("File Analysis:")
    print(f"  QFieldCloud files (matching '{file_filter}'): {len(qfield_files)}")
    print(f"  GCP bucket files:                             {len(gcp_relative_paths)}")
    print(f"  Files to upload:                              {len(files_to_upload)}")
    already_exist_count = len(qfield_files) - len(files_to_upload)
    print(f"  Files already in GCP (skipped):               {already_exist_count}")
    print("=" * 80)

    if not files_to_upload:
        print("\nAll files already exist in GCP bucket. Nothing to upload.")
        return {"no_files": True, "all_exist": True}

    print(f"\nDestination: gs://{gcp_bucket}/{gcp_bucket_directory}/")
    print("-" * 80)

    # Upload files
    success_count = 0
    failed_count = 0
    skipped_count = len(qfield_files) - len(files_to_upload)  # Already calculated

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        for idx, file in enumerate(files_to_upload, 1):
            file_name = file["name"]
            print(f"[{idx}/{len(files_to_upload)}] Uploading {file_name}...")

            try:
                # Construct GCP destination path
                gcp_destination = f"{gcp_bucket_directory}/{file_name}".strip("/")

                # Download from QFieldCloud to temp directory
                local_file_path = temp_path / file_name

                # Create parent directories if file is in a subdirectory
                local_file_path.parent.mkdir(parents=True, exist_ok=True)

                logger.debug(f"Downloading {file_name} to {local_file_path}")
                qfield_client.download_file(file_name, str(local_file_path))

                # Upload to GCP
                logger.debug(f"Uploading {file_name} to GCP")
                gcp_client.upload_file(str(local_file_path), gcp_bucket, gcp_destination)

                # Clean up temp file
                local_file_path.unlink()

                print("  → Uploaded successfully")
                success_count += 1

            except Exception as e:
                logger.error(f"Failed to process {file_name}: {e}")
                print(f"  → Failed: {e}")
                failed_count += 1
                continue

    # Print summary
    print("\n" + "=" * 80)
    print("Upload Summary:")
    print(f"  Total files in QFieldCloud: {len(qfield_files)}")
    print(f"  Successfully uploaded: {success_count}")
    print(f"  Skipped (already exist): {skipped_count}")
    print(f"  Failed: {failed_count}")
    print("=" * 80)

    return {
        "total": len(qfield_files),
        "success": success_count,
        "skipped": skipped_count,
        "failed": failed_count,
    }
