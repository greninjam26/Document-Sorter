"""Command-line entry point for Document Sorter."""

import argparse
from pathlib import Path

from document_sorter.scanner import SourceDirectoryError
from document_sorter.sorter import sort_documents


def parse_arguments() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description="Rename and move PDFs using their SAL barcodes.")
    parser.add_argument(
        "source",
        type=Path,
        help="starting folder containing the PDF files",
    )
    parser.add_argument(
        "destination",
        type=Path,
        help="folder where renamed PDF files will be moved",
    )
    return parser.parse_args()


def main() -> int:
    """Run the document sorter."""
    arguments = parse_arguments()

    try:
        results = sort_documents(arguments.source, arguments.destination)
    except SourceDirectoryError as error:
        print(f"Error: {error}")
        return 1

    return 0 if all(result.succeeded for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
