"""Clean old photos from QFieldCloud."""

import logging
from datetime import datetime, timezone
from typing import Any

from qc_utils.core.filters import filter_files_by_age_and_pattern
from qc_utils.core.qfield_client import QFieldCloudClient

logger = logging.getLogger(__name__)


def format_size_mb(size_bytes: int) -> str:
    """Format size in bytes to MB string."""
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def display_summary(files: list[dict[str, Any]], days: int) -> None:
    """
    Display summary of files to delete.

    Args:
        files: List of files to delete
        days: Days threshold used for filtering
    """
    if not files:
        print("No files to delete.")
        return

    print(f"\nFiles older than {days} days to delete:")
    print("-" * 80)
    print(f"Number of files: {len(files)}")

    total_size = sum(f.get("size", 0) for f in files)
    print(f"Total space to free: {format_size_mb(total_size)}")

    # Show detailed list if in debug mode
    if logger.isEnabledFor(logging.DEBUG):
        print("\nDetailed list:")
        print("-" * 80)
        for file in sorted(files, key=lambda x: x["updated_at"]):
            age_days = (datetime.now(timezone.utc) - file["updated_at"]).days
            logger.debug(f"  {file['name']}")
            logger.debug(
                f"    Modified: {file['updated_at'].strftime('%d/%m/%Y %H:%M:%S')} "
                f"({age_days} days ago)"
            )
            logger.debug(f"    Size: {format_size_mb(file['size'])}")
            logger.debug("")

    print()


def run_clean(
    project_id: str,
    keep_days: int = 15,
    file_filter: str = "*.jpg",
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Clean old photos from QFieldCloud.

    Args:
        project_id: QFieldCloud project ID
        keep_days: Keep files newer than this many days
        file_filter: Glob pattern for files to clean (default: *.jpg)
        dry_run: If True, only show what would be deleted

    Returns:
        Dictionary with operation results

    Raises:
        ValueError: If authentication fails
        RuntimeError: If operation fails
    """
    logger.info(f"Starting cleanup for project {project_id}")
    logger.info(f"Keep threshold: {keep_days} days")
    logger.info(f"File filter: {file_filter}")
    logger.info(f"Dry run: {dry_run}")

    # Initialize client and authenticate
    client = QFieldCloudClient(project_id)
    client.authenticate()

    # List files with metadata
    logger.info("Fetching file list...")
    files = client.list_files(skip_metadata=False)
    logger.info(f"Total files in project: {len(files)}")

    # Filter files by age and pattern
    logger.info(f"Filtering files older than {keep_days} days matching '{file_filter}'")
    files_to_delete = filter_files_by_age_and_pattern(files, file_filter, keep_days)

    # Display summary
    display_summary(files_to_delete, keep_days)

    # Delete files if not dry run
    if not dry_run and files_to_delete:
        print("Deleting files...")
        file_names = [f["name"] for f in files_to_delete]
        result = client.delete_files(file_names, throw_on_error=False)
        print("Deletion complete!")
        return result
    elif dry_run:
        print("Dry run mode - no files were deleted")
        return {"dry_run": True, "files_to_delete": len(files_to_delete)}
    else:
        print("No files to delete")
        return {"no_files": True}
