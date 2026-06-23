"""Tests for PDF barcode extraction."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from document_sorter.barcode_reader import BarcodeReadError, read_barcodes


class FakeDocument:
    """Small fake rendered PDF document."""

    needs_pass = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def __iter__(self):
        pixmap = SimpleNamespace(samples=b"pixels", width=10, height=10)
        page = SimpleNamespace(get_pixmap=lambda **_kwargs: pixmap)
        return iter([page])


class ReadBarcodesTests(unittest.TestCase):
    """Verify barcode extraction and its input validation."""

    def test_returns_distinct_nonempty_barcode_values(self) -> None:
        """Duplicate and empty decoded values should not be returned."""
        fake_fitz = SimpleNamespace(
            open=lambda _path: FakeDocument(),
            Matrix=lambda x, y: (x, y),
        )
        fake_zxingcpp = SimpleNamespace(
            read_barcodes=lambda _image: [
                SimpleNamespace(text=" SAL123 "),
                SimpleNamespace(text="SAL123"),
                SimpleNamespace(text=""),
                SimpleNamespace(text="OTHER456"),
            ]
        )
        fake_image_module = SimpleNamespace(
            frombytes=lambda _mode, _size, samples: samples
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            pdf_file = Path(temporary_directory) / "document.pdf"
            pdf_file.touch()

            with patch(
                "document_sorter.barcode_reader._load_dependencies",
                return_value=(fake_fitz, fake_zxingcpp, fake_image_module),
            ):
                self.assertEqual(
                    read_barcodes(pdf_file),
                    ["SAL123", "OTHER456"],
                )

    def test_rejects_a_missing_pdf(self) -> None:
        """A missing PDF should produce barcode-read error."""
        with self.assertRaisesRegex(BarcodeReadError, "does not exist"):
            read_barcodes(Path("missing.pdf"))

    def test_rejects_an_invalid_dpi(self) -> None:
        """Rendering resolution must be a positive number."""
        with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf_file:
            with self.assertRaisesRegex(ValueError, "greater than zero"):
                read_barcodes(Path(pdf_file.name), dpi=0)


if __name__ == "__main__":
    unittest.main()
