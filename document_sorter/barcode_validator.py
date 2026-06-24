"""Validate barcode values used by Document Sorter."""

from collections.abc import Iterable


SAL_PREFIX = "SAL"
INVALID_FILENAME_CHARACTERS = frozenset('<>:"/\\|?*')


class BarcodeValidationError(ValueError):
    """Used when a PDF does not contain exactly one valid SAL barcode."""


def validate_sal_barcode(barcodes: Iterable[str]) -> str:
    """Return the one distinct barcode beginning with uppercase ``SAL``.

    Values that do not begin with ``SAL`` are ignored. 
    Repeated copies of the same SAL value count as one barcode.
    """
    if isinstance(barcodes, str):
        raise TypeError(
            "barcodes must be a collection of strings, even if the collection only have one string")

    sal_barcodes: list[str] = []

    for barcode in barcodes:
        if not isinstance(barcode, str):
            raise TypeError("every barcode value must be a string")

        value = barcode.strip()
        if value.startswith(SAL_PREFIX) and value not in sal_barcodes:
            sal_barcodes.append(value)

    if not sal_barcodes:
        raise BarcodeValidationError(
            f"No barcode beginning with {SAL_PREFIX} was found"
        )
    if len(sal_barcodes) > 1:
        raise BarcodeValidationError(
            f"Multiple barcodes beginning with {SAL_PREFIX} were found: "
            f"{', '.join(sal_barcodes)}"
        )

    sal_barcode = sal_barcodes[0]
    if sal_barcode == SAL_PREFIX:
        raise BarcodeValidationError(
            f"Barcode must contain a value after {SAL_PREFIX}"
        )
    if any(
        character in INVALID_FILENAME_CHARACTERS or ord(character) < 32
        for character in sal_barcode
    ):
        raise BarcodeValidationError(
            "Barcode contains a character that is unsafe in a filename"
        )
    if sal_barcode.endswith((".", " ")):
        raise BarcodeValidationError(
            "Barcode cannot end with a period or space"
        )

    return sal_barcode
