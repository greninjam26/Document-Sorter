"""Tests for the barcode-scanning workflow."""

import unittest
from pathlib import Path
from unittest.mock import patch

from document_sorter.barcode_reader import BarcodeReadError
from document_sorter.file_mover import FileMoveError
from document_sorter.sorter import sort_documents


class SortDocumentsTests(unittest.TestCase):
    """Verify success and failure results for a batch of PDFs."""

    def setUp(self) -> None:
        """Hide normal command output while testing returned results."""
        print_patcher = patch("builtins.print")
        self.addCleanup(print_patcher.stop)
        print_patcher.start()

    @patch(
        "document_sorter.sorter.move_pdf_to_destination",
        return_value=Path("destination/SAL123.pdf"),
    )
    @patch(
        "document_sorter.sorter.read_barcodes",
        return_value=["OTHER456", "SAL123"],
    )
    @patch(
        "document_sorter.sorter.find_pdf_files",
        return_value=[Path("document.pdf")],
    )
    def test_succeeds_when_every_pdf_is_read(
        self,
        _find_pdf_files,
        _read_barcodes,
        _move_pdf_to_destination,
    ) -> None:
        """A batch should succeed when every PDF is renamed and moved."""
        result = sort_documents(Path("source"), Path("destination"))[0]

        self.assertTrue(result.succeeded)
        self.assertEqual(result.source_file, Path("document.pdf"))
        self.assertEqual(result.sal_barcode, "SAL123")
        self.assertEqual(result.destination_file,
                         Path("destination/SAL123.pdf"))
        self.assertIsNone(result.error)

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
        result = sort_documents(Path("source"), Path("destination"))[0]

        self.assertFalse(result.succeeded)
        self.assertEqual(result.error, "damaged PDF")

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
        result = sort_documents(Path("source"), Path("destination"))[0]

        self.assertFalse(result.succeeded)
        self.assertIn("No barcode", result.error or "")

    @patch(
        "document_sorter.sorter.read_barcodes",
        return_value=["SAL123", "SAL456"],
    )
    @patch(
        "document_sorter.sorter.find_pdf_files",
        return_value=[Path("document.pdf")],
    )
    def test_fails_when_a_pdf_has_multiple_sal_barcodes(
        self,
        _find_pdf_files,
        _read_barcodes,
    ) -> None:
        """A PDF with conflicting SAL values should make the batch fail."""
        result = sort_documents(Path("source"), Path("destination"))[0]

        self.assertFalse(result.succeeded)
        self.assertIn("Multiple barcodes", result.error or "")

    @patch(
        "document_sorter.sorter.move_pdf_to_destination",
        side_effect=FileMoveError("destination file already exists"),
    )
    @patch(
        "document_sorter.sorter.read_barcodes",
        return_value=["SAL123"],
    )
    @patch(
        "document_sorter.sorter.find_pdf_files",
        return_value=[Path("document.pdf")],
    )
    def test_fails_when_a_pdf_cannot_be_moved(
        self,
        _find_pdf_files,
        _read_barcodes,
        _move_pdf_to_destination,
    ) -> None:
        """A move error should make the document fail without crashing."""
        result = sort_documents(Path("source"), Path("destination"))[0]

        self.assertFalse(result.succeeded)
        self.assertEqual(result.sal_barcode, "SAL123")
        self.assertIsNone(result.destination_file)
        self.assertIn("destination file already exists", result.error or "")


if __name__ == "__main__":
    unittest.main()
