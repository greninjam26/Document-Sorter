"""Main document-sorting workflow."""

from dataclasses import dataclass
from pathlib import Path

from document_sorter.barcode_reader import BarcodeReadError, read_barcodes
from document_sorter.barcode_validator import (
    BarcodeValidationError,
    validate_sal_barcode,
)
from document_sorter.file_mover import (
    FileMoveError,
    move_pdf_to_destination,
    move_pdf_to_error_folder,
)
from document_sorter.scanner import find_pdf_files


@dataclass(frozen=True)
class DocumentResult:
    """Processing result for one PDF."""

    source_file: Path
    sal_barcode: str | None = None
    destination_file: Path | None = None
    error_file: Path | None = None
    error: str | None = None

    @property
    def succeeded(self) -> bool:
        """Return whether the PDF was renamed and moved successfully."""
        return (
            self.error is None
            and self.sal_barcode is not None
            and self.destination_file is not None
        )


def sort_documents(
    source_directory: Path,
    destination_directory: Path,
) -> list[DocumentResult]:
    """Find, rename, and move PDFs using each file's SAL barcode."""
    pdf_files = find_pdf_files(source_directory)
    results: list[DocumentResult] = []

    print(f"Found {len(pdf_files)} PDF file(s) in {source_directory}:")
    for pdf_file in pdf_files:
        try:
            barcodes = read_barcodes(pdf_file)
            sal_barcode = validate_sal_barcode(barcodes)
        except (BarcodeReadError, BarcodeValidationError) as error:
            results.append(
                _record_error_result(
                    pdf_file,
                    destination_directory,
                    str(error),
                )
            )
            continue

        try:
            destination_file = move_pdf_to_destination(
                pdf_file,
                destination_directory,
                sal_barcode,
            )
        except FileMoveError as error:
            results.append(
                _record_error_result(
                    pdf_file,
                    destination_directory,
                    str(error),
                    sal_barcode,
                )
            )
            continue

        print(f"- {pdf_file.name}: moved to {destination_file}")
        results.append(
            DocumentResult(
                pdf_file,
                sal_barcode=sal_barcode,
                destination_file=destination_file,
            )
        )

    return results


def _record_error_result(
    pdf_file: Path,
    destination_directory: Path,
    error_message: str,
    sal_barcode: str | None = None,
) -> DocumentResult:
    """Move a failed PDF to the error folder and return its result."""
    try:
        error_file = move_pdf_to_error_folder(pdf_file, destination_directory)
    except FileMoveError as move_error:
        combined_error = (
            f"{error_message}; also could not move to error folder: "
            f"{move_error}"
        )
        print(f"- {pdf_file.name}: ERROR - {combined_error}")
        return DocumentResult(
            pdf_file,
            sal_barcode=sal_barcode,
            error=combined_error,
        )

    print(f"- {pdf_file.name}: ERROR - {error_message}; moved to {error_file}")
    return DocumentResult(
        pdf_file,
        sal_barcode=sal_barcode,
        error_file=error_file,
        error=error_message,
    )
