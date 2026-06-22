"""Main document-sorting workflow."""

from pathlib import Path

from document_sorter.scanner import find_pdf_files


def sort_documents(source_directory: Path) -> list[Path]:
    """Process PDFs that will be moved."""
    pdf_files = find_pdf_files(source_directory)

    print(f"Found {len(pdf_files)} PDF file(s) in {source_directory}:")
    for pdf_file in pdf_files:
        print(f"- {pdf_file.name}")

    return pdf_files
