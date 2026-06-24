"""Move processed PDF files to their final destination."""

import shutil
from pathlib import Path


class FileMoveError(OSError):
    """Used when a PDF cannot be moved to its destination."""


def move_pdf_to_destination(
    pdf_file: Path,
    destination_directory: Path,
    new_name: str,
) -> Path:
    """Rename the file and move it to the destination."""
    destination_directory = destination_directory.expanduser()

    try:
        destination_directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise FileMoveError(
            f"Could not create destination directory "
            f"{destination_directory}: {error}"
        ) from error

    destination_file = destination_directory / f"{new_name}.pdf"
    if destination_file.exists():
        raise FileMoveError(
            f"Destination file already exists: {destination_file}"
        )

    try:
        shutil.move(str(pdf_file), str(destination_file))
    except OSError as error:
        raise FileMoveError(
            f"Could not move {pdf_file.name} to {destination_file}: {error}"
        ) from error

    return destination_file
