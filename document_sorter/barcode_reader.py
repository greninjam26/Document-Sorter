"""Scan PDF for the barcodes."""

from pathlib import Path
from typing import Any


class BarcodeReadError(RuntimeError):
    """Used when barcodes cannot be read from a PDF."""


def _load_dependencies() -> tuple[Any, Any, Any]:
    """Load PDF and barcode libraries and check for error."""
    try:
        import fitz  # PyMuPDF
        import zxingcpp
        from PIL import Image
    except ImportError as error:
        raise BarcodeReadError(
            "Barcode tools are not installed. Run: "
            "python3 -m pip install -r requirements.txt"
        ) from error

    return fitz, zxingcpp, Image


def read_barcodes(pdf_file: Path, dpi: int = 300) -> list[str]:
    """Return the distinct barcode values found on every page of a PDF.

    The PDF is rendered in memory and is never modified. Validation of the expected ``SAL`` prefix belongs to the next processing stage.
    """
    pdf_file = pdf_file.expanduser()
    if not pdf_file.is_file():
        raise BarcodeReadError(f"PDF file does not exist: {pdf_file}")
    if dpi <= 0:
        raise ValueError("dpi must be greater than zero")

    fitz, zxingcpp, image_module = _load_dependencies()
    barcode_values: list[str] = []

    try:
        with fitz.open(pdf_file) as document:
            if document.needs_pass:
                raise BarcodeReadError(
                    f"PDF is password-protected: {pdf_file.name}")

            zoom = dpi / 72
            matrix = fitz.Matrix(zoom, zoom)

            for page in document:
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                image = image_module.frombytes(
                    "RGB",
                    (pixmap.width, pixmap.height),
                    pixmap.samples,
                )

                for barcode in zxingcpp.read_barcodes(image):
                    value = barcode.text.strip()
                    if value and value not in barcode_values:
                        barcode_values.append(value)
    except BarcodeReadError:
        raise
    except Exception as error:
        raise BarcodeReadError(
            f"Could not read barcodes from {pdf_file.name}: {error}"
        ) from error

    return barcode_values
