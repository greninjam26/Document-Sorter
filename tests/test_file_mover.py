"""Tests for moving renamed PDF files."""

import tempfile
import unittest
from pathlib import Path

from document_sorter.file_mover import (
    FileMoveError,
    move_pdf_to_destination,
    move_pdf_to_error_folder,
)


class FileMoverTests(unittest.TestCase):
    """Verify PDF rename-and-move behavior."""

    def test_moves_pdf_to_destination_with_sal_name(self) -> None:
        """A PDF should be moved and renamed to the barcode value."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            source_file = workspace / "source" / "original.pdf"
            destination_directory = workspace / "destination"
            source_file.parent.mkdir()
            source_file.write_bytes(b"fake pdf")

            destination_file = move_pdf_to_destination(
                source_file,
                destination_directory,
                "SAL123",
            )

            self.assertEqual(destination_file,
                             destination_directory / "SAL123.pdf")
            self.assertTrue(destination_file.exists())
            self.assertFalse(source_file.exists())

    def test_does_not_overwrite_existing_destination_file(self) -> None:
        """An existing destination file should make the move fail safely."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            source_file = workspace / "source" / "original.pdf"
            destination_file = workspace / "destination" / "SAL123.pdf"
            source_file.parent.mkdir()
            destination_file.parent.mkdir()
            source_file.write_bytes(b"new pdf")
            destination_file.write_bytes(b"existing pdf")

            with self.assertRaises(FileMoveError):
                move_pdf_to_destination(
                    source_file,
                    destination_file.parent,
                    "SAL123",
                )

            self.assertTrue(source_file.exists())
            self.assertEqual(destination_file.read_bytes(), b"existing pdf")

    def test_rejects_destination_path_that_is_a_file(self) -> None:
        """A destination path that is already a file should fail cleanly."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            source_file = workspace / "source" / "original.pdf"
            destination_path = workspace / "not-a-folder"
            source_file.parent.mkdir()
            source_file.write_bytes(b"fake pdf")
            destination_path.write_bytes(b"I am a file")

            with self.assertRaisesRegex(FileMoveError, "Could not create"):
                move_pdf_to_destination(
                    source_file, destination_path, "SAL123")

            self.assertTrue(source_file.exists())

    def test_moves_pdf_to_error_folder(self) -> None:
        """A failed PDF should be moved into the destination error folder."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            source_file = workspace / "source" / "original.pdf"
            destination_directory = workspace / "destination"
            source_file.parent.mkdir()
            source_file.write_bytes(b"bad pdf")

            error_file = move_pdf_to_error_folder(
                source_file,
                destination_directory,
            )

            self.assertEqual(
                error_file,
                destination_directory / "errors" / "original.pdf",
            )
            self.assertTrue(error_file.exists())
            self.assertFalse(source_file.exists())

    def test_error_folder_move_does_not_overwrite_existing_file(self) -> None:
        """A repeated error filename should receive a numbered name."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            source_file = workspace / "source" / "original.pdf"
            existing_error_file = (
                workspace / "destination" / "errors" / "original.pdf"
            )
            source_file.parent.mkdir()
            existing_error_file.parent.mkdir(parents=True)
            source_file.write_bytes(b"new bad pdf")
            existing_error_file.write_bytes(b"old bad pdf")

            error_file = move_pdf_to_error_folder(
                source_file,
                workspace / "destination",
            )

            self.assertEqual(
                error_file,
                workspace / "destination" / "errors" / "original-1.pdf",
            )
            self.assertEqual(existing_error_file.read_bytes(), b"old bad pdf")
            self.assertEqual(error_file.read_bytes(), b"new bad pdf")


if __name__ == "__main__":
    unittest.main()
