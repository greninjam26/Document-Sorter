"""Command-line entry point for Document Sorter."""

import argparse
from pathlib import Path

from document_sorter.scanner import SourceDirectoryError
from document_sorter.sorter import sort_documents


def parse_arguments() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description="Find PDFs ready to be sorted.")
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
        sort_documents(arguments.source)
    except SourceDirectoryError as error:
        print(f"Error: {error}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
