"""Command-line interface for qc-utils."""

import argparse
import logging
import sys

from qc_utils.commands.clean import run_clean
from qc_utils.commands.upload import run_upload


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the application.

    Args:
        verbose: If True, set log level to DEBUG
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> None:
    """
    Main entry point for qc-to-gcp upload command.

    Usage:
        qc-to-gcp upload --qc-project-id <id> --gcp-bucket <bucket> ...
    """
    parser = argparse.ArgumentParser(
        prog="qc-to-gcp",
        description="Upload photos from QFieldCloud to Google Cloud Storage",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Upload subcommand
    upload_parser = subparsers.add_parser(
        "upload", help="Upload photos from QFieldCloud to GCP"
    )

    upload_parser.add_argument(
        "--qc-project-id",
        required=True,
        help="QFieldCloud project ID",
    )

    upload_parser.add_argument(
        "--gcp-bucket",
        required=True,
        help="GCP bucket name",
    )

    upload_parser.add_argument(
        "--gcp-bucket-directory",
        required=True,
        help="Directory path in GCP bucket",
    )

    upload_parser.add_argument(
        "--gcp-auth-file",
        required=True,
        help="Path to GCP service account JSON file",
    )

    upload_parser.add_argument(
        "--qc-filter",
        default="*.jp*g",
        help="File filter pattern (default: *.jp*g)",
    )

    upload_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Setup logging
    setup_logging(args.verbose)

    try:
        if args.command == "upload":
            result = run_upload(
                project_id=args.qc_project_id,
                gcp_bucket=args.gcp_bucket,
                gcp_bucket_directory=args.gcp_bucket_directory,
                gcp_auth_file=args.gcp_auth_file,
                file_filter=args.qc_filter,
            )

            # Exit with error if any failures
            if result.get("failed", 0) > 0:
                sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


def main_clean() -> None:
    """
    Main entry point for qc-clean command.

    Usage:
        qc-clean --qc-project-id <id> --keep-days <days> --qc-filter <pattern>
    """
    parser = argparse.ArgumentParser(
        prog="qc-clean",
        description="Clean old photos from QFieldCloud",
    )

    parser.add_argument(
        "--qc-project-id",
        required=True,
        help="QFieldCloud project ID",
    )

    parser.add_argument(
        "--keep-days",
        type=int,
        default=15,
        help="Keep files newer than this many days (default: 15)",
    )

    parser.add_argument(
        "--qc-filter",
        default="*.jp*g",
        help="File filter pattern (default: *.jp*g)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    try:
        run_clean(
            project_id=args.qc_project_id,
            keep_days=args.keep_days,
            file_filter=args.qc_filter,
            dry_run=args.dry_run,
        )

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # When run as script, default to main_clean for backward compatibility
    main_clean()
