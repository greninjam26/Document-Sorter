"""Tests for SAL barcode validation."""

import unittest

from document_sorter.barcode_validator import (
    BarcodeValidationError,
    validate_sal_barcode,
)


class ValidateSalBarcodeTests(unittest.TestCase):
    """Verify that exactly one distinct SAL barcode is required."""

    def test_returns_the_sal_barcode(self) -> None:
        """A single SAL barcode should be returned."""
        self.assertEqual(
            validate_sal_barcode(["OTHER123", "SAL456"]),
            "SAL456",
        )

    def test_ignores_repeated_copies_of_the_same_barcode(self) -> None:
        """The same SAL value found more than once should remain valid."""
        self.assertEqual(
            validate_sal_barcode(["SAL456", "SAL456"]),
            "SAL456",
        )

    def test_removes_surrounding_whitespace(self) -> None:
        """Whitespace around a decoded value should not enter the filename."""
        self.assertEqual(validate_sal_barcode(["  SAL456  "]), "SAL456")

    def test_rejects_values_without_an_uppercase_sal_prefix(self) -> None:
        """Missing and lowercase SAL prefixes should be rejected."""
        with self.assertRaisesRegex(BarcodeValidationError, "No barcode"):
            validate_sal_barcode(["OTHER123", "sal456"])

    def test_rejects_multiple_different_sal_barcodes(self) -> None:
        """Different SAL values in one PDF are ambiguous and unsafe."""
        with self.assertRaisesRegex(BarcodeValidationError, "Multiple barcodes"):
            validate_sal_barcode(["SAL123", "SAL456"])

    def test_rejects_bare_sal_prefix(self) -> None:
        """The prefix by itself does not contain a usable identifier."""
        with self.assertRaisesRegex(BarcodeValidationError, "after SAL"):
            validate_sal_barcode(["SAL"])

    def test_rejects_filename_characters(self) -> None:
        """A barcode must be safe to use as a filename on common systems."""
        unsafe_values = ["SAL/123", "SAL\\123", "SAL:123", "SAL?123"]

        for value in unsafe_values:
            with self.subTest(value=value):
                with self.assertRaisesRegex(BarcodeValidationError, "unsafe"):
                    validate_sal_barcode([value])

    def test_rejects_one_string_instead_of_a_collection(self) -> None:
        """Passing one string should not silently iterate over its characters."""
        with self.assertRaisesRegex(TypeError, "collection"):
            validate_sal_barcode("SAL123")

    def test_rejects_non_string_barcode_values(self) -> None:
        """Every decoded barcode value must be text."""
        with self.assertRaisesRegex(TypeError, "must be a string"):
            validate_sal_barcode([123])  # type: ignore[list-item]


if __name__ == "__main__":
    unittest.main()
