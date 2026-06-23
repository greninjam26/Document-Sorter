"""Tests for PDF discovery."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from document_sorter.scanner import SourceDirectoryError, find_pdf_files


class FindPdfFilesTests(unittest.TestCase):
    """Verify safe discovery of top-level PDF files."""

    def test_returns_only_pdf_files_in_name_order(self) -> None:
        """Only PDF files should be returned in predictable name order."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            second_pdf = directory / "B-form.PDF"
            first_pdf = directory / "a-form.pdf"
            ignored_text = directory / "notes.txt"

            second_pdf.touch()
            first_pdf.touch()
            ignored_text.touch()

            self.assertEqual(find_pdf_files(directory),
                             [first_pdf, second_pdf])

    def test_does_not_scan_subdirectories(self) -> None:
        """PDFs inside nested folders should not be included."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            nested_directory = directory / "nested"
            nested_directory.mkdir()
            (nested_directory / "nested.pdf").touch()

            self.assertEqual(find_pdf_files(directory), [])

    def test_rejects_a_missing_source_directory(self) -> None:
        """A source folder that does not exist should be rejected."""
        missing_directory = Path(tempfile.gettempdir()) / \
            "missing-document-sorter-dir"

        with self.assertRaisesRegex(SourceDirectoryError, "does not exist"):
            find_pdf_files(missing_directory)

    def test_rejects_a_source_path_that_is_a_file(self) -> None:
        """The source path must identify a directory, not a file."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "not-a-directory.pdf"
            file_path.touch()

            with self.assertRaisesRegex(SourceDirectoryError, "not a directory"):
                find_pdf_files(file_path)

    def test_reports_an_inaccessible_source_directory(self) -> None:
        """Folder permission failures should produce a friendly error."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)

            with patch.object(Path, "iterdir", side_effect=PermissionError):
                with self.assertRaisesRegex(
                    SourceDirectoryError,
                    "Cannot access source directory",
                ):
                    find_pdf_files(directory)


if __name__ == "__main__":
    unittest.main()
