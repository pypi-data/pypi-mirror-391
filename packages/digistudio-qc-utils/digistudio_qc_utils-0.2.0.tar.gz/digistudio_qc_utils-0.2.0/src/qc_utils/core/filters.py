"""File filtering utilities for QFieldCloud files."""

import fnmatch
from datetime import datetime, timedelta, timezone
from typing import Any


def matches_pattern(filename: str, pattern: str) -> bool:
    """
    Check if a filename matches a glob pattern.

    Args:
        filename: The filename to check
        pattern: The glob pattern (e.g., "*.jpg", "*.png")

    Returns:
        True if the filename matches the pattern
    """
    return fnmatch.fnmatch(filename.lower(), pattern.lower())


def parse_qfield_date(date_str: str) -> datetime:
    """
    Parse QFieldCloud date format to datetime.

    QFieldCloud returns dates in format "DD.MM.YYYY HH:MM:SS UTC"

    Args:
        date_str: Date string from QFieldCloud

    Returns:
        Datetime object with UTC timezone

    Raises:
        ValueError: If date format is invalid
    """
    if date_str.endswith(" UTC"):
        # Extract date/time part and parse
        datetime_part = date_str[:-4]  # Remove " UTC"
        file_date = datetime.strptime(datetime_part, "%d.%m.%Y %H:%M:%S")
        # Add UTC timezone
        return file_date.replace(tzinfo=timezone.utc)
    # Fallback: try ISO 8601 format
    return datetime.fromisoformat(date_str)


def is_file_older_than(file_date: datetime, days: int) -> bool:
    """
    Check if a file is older than a certain number of days.

    Args:
        file_date: The file's last modified date
        days: Number of days threshold

    Returns:
        True if file is older than the threshold
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    return file_date < cutoff_date


def filter_files_by_age_and_pattern(
    files: list[dict[str, Any]], pattern: str, days: int
) -> list[dict[str, Any]]:
    """
    Filter files by pattern and age.

    Args:
        files: List of file metadata from QFieldCloud
        pattern: Glob pattern to match filenames (e.g., "*.jpg")
        days: Keep files newer than this many days

    Returns:
        List of files to delete (matching pattern and older than threshold)
    """
    filtered_files = []

    for file in files:
        filename = file["name"]

        # Check pattern match
        if not matches_pattern(filename, pattern):
            continue

        # Parse and check date
        try:
            file_date_str = file["last_modified"]
            file_date = parse_qfield_date(file_date_str)

            if is_file_older_than(file_date, days):
                filtered_files.append(
                    {
                        "name": filename,
                        "updated_at": file_date,
                        "size": file.get("size", 0),
                    }
                )
        except (ValueError, KeyError):
            # Skip files with invalid dates
            continue

    return filtered_files


def filter_files_by_pattern(
    files: list[dict[str, Any]], pattern: str
) -> list[dict[str, Any]]:
    """
    Filter files by pattern only (no age filtering).

    Args:
        files: List of file metadata from QFieldCloud
        pattern: Glob pattern to match filenames (e.g., "*.jpg")

    Returns:
        List of files matching the pattern
    """
    return [file for file in files if matches_pattern(file["name"], pattern)]
