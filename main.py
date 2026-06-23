"""Command-line entry point for Document Sorter."""

import argparse
from pathlib import Path

from document_sorter.scanner import SourceDirectoryError
from document_sorter.sorter import sort_documents


def parse_arguments() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description="Find PDFs and read their barcodes.")
    parser.add_argument(
        "source",
        type=Path,
        help="starting folder containing the PDF files",
    )
    return parser.parse_args()


def main() -> int:
    """Run the document sorter."""
    arguments = parse_arguments()

    try:
        all_scans_succeeded = sort_documents(arguments.source)
    except SourceDirectoryError as error:
        print(f"Error: {error}")
        return 1

    return 0 if all_scans_succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
