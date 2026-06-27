"""Tests for writing processing logs."""

import csv
import tempfile
import unittest
from pathlib import Path

from document_sorter.processing_log import write_processing_log
from document_sorter.sorter import DocumentResult


class ProcessingLogTests(unittest.TestCase):
    """Verify CSV logging for document processing results."""

    def test_writes_success_and_error_rows(self) -> None:
        """The log should record what happened to each processed PDF."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination_directory = Path(temporary_directory)
            results = [
                DocumentResult(
                    Path("source/good.pdf"),
                    sal_barcode="SAL123",
                    destination_file=destination_directory / "SAL123.pdf",
                ),
                DocumentResult(
                    Path("source/bad.pdf"),
                    error_file=destination_directory / "errors" / "bad.pdf",
                    error="No barcode beginning with SAL was found",
                ),
            ]

            log_file = write_processing_log(results, destination_directory)

            with log_file.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["status"], "success")
            self.assertEqual(rows[0]["source_file"], "source/good.pdf")
            self.assertEqual(rows[0]["sal_barcode"], "SAL123")
            self.assertEqual(
                rows[0]["destination_file"],
                str(destination_directory / "SAL123.pdf"),
            )
            self.assertEqual(rows[0]["error"], "")

            self.assertEqual(rows[1]["status"], "error")
            self.assertEqual(rows[1]["source_file"], "source/bad.pdf")
            self.assertEqual(
                rows[1]["error_file"],
                str(destination_directory / "errors" / "bad.pdf"),
            )
            self.assertEqual(
                rows[1]["error"],
                "No barcode beginning with SAL was found",
            )

    def test_appends_without_repeating_headers(self) -> None:
        """A second log write should add rows without a second header row."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination_directory = Path(temporary_directory)
            result = DocumentResult(
                Path("source/good.pdf"),
                sal_barcode="SAL123",
                destination_file=destination_directory / "SAL123.pdf",
            )

            log_file = write_processing_log([result], destination_directory)
            write_processing_log([result], destination_directory)

            lines = log_file.read_text(encoding="utf-8").splitlines()

            self.assertEqual(len(lines), 3)
            self.assertEqual(lines[0].count("timestamp"), 1)
            self.assertFalse(lines[1].startswith("timestamp"))
            self.assertFalse(lines[2].startswith("timestamp"))


if __name__ == "__main__":
    unittest.main()
