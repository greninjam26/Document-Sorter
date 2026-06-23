"""Main document-sorting workflow."""

from pathlib import Path

from document_sorter.barcode_reader import BarcodeReadError, read_barcodes
from document_sorter.scanner import find_pdf_files


def sort_documents(source_directory: Path) -> bool:
    """Read each PDF's barcodes and return whether every scan succeeded."""
    pdf_files = find_pdf_files(source_directory)
    all_scans_succeeded = True

    print(f"Found {len(pdf_files)} PDF file(s) in {source_directory}:")
    for pdf_file in pdf_files:
        try:
            barcodes = read_barcodes(pdf_file)
        except BarcodeReadError as error:
            print(f"- {pdf_file.name}: ERROR - {error}")
            all_scans_succeeded = False
            continue

        if barcodes:
            print(f"- {pdf_file.name}: {', '.join(barcodes)}")
        else:
            print(f"- {pdf_file.name}: no barcode found")
            all_scans_succeeded = False

    return all_scans_succeeded
