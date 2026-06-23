"""Tests for the barcode-scanning workflow."""

import unittest
from pathlib import Path
from unittest.mock import patch

from document_sorter.barcode_reader import BarcodeReadError
from document_sorter.sorter import sort_documents


class SortDocumentsTests(unittest.TestCase):
    """Verify success and failure results for a batch of PDFs."""

    @patch("document_sorter.sorter.read_barcodes", return_value=["SAL123"])
    @patch(
        "document_sorter.sorter.find_pdf_files",
        return_value=[Path("document.pdf")],
    )
    def test_succeeds_when_every_pdf_is_read(
        self,
        _find_pdf_files,
        _read_barcodes,
    ) -> None:
        """A batch should succeed when every PDF has a barcode."""
        self.assertTrue(sort_documents(Path("source")))

    @patch(
        "document_sorter.sorter.read_barcodes",
        side_effect=BarcodeReadError("damaged PDF"),
    )
    @patch(
        "document_sorter.sorter.find_pdf_files",
        return_value=[Path("document.pdf")],
    )
    def test_fails_when_a_pdf_cannot_be_read(
        self,
        _find_pdf_files,
        _read_barcodes,
    ) -> None:
        """A barcode-reading exception should make the batch fail."""
        self.assertFalse(sort_documents(Path("source")))

    @patch("document_sorter.sorter.read_barcodes", return_value=[])
    @patch(
        "document_sorter.sorter.find_pdf_files",
        return_value=[Path("document.pdf")],
    )
    def test_fails_when_a_pdf_has_no_barcode(
        self,
        _find_pdf_files,
        _read_barcodes,
    ) -> None:
        """A PDF without a barcode should make the batch fail."""
        self.assertFalse(sort_documents(Path("source")))


if __name__ == "__main__":
    unittest.main()
