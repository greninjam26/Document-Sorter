"""Move processed PDF files to their final destination."""

import shutil
from pathlib import Path


class FileMoveError(OSError):
    """Used when a PDF cannot be moved to its destination."""


def _create_directory(directory: Path, description: str) -> None:
    """Create a directory and raise a project error if it fails."""
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise FileMoveError(
            f"Could not create {description} {directory}: {error}"
        ) from error


def _available_path(directory: Path, file_name: str) -> Path:
    """Return a path that will not overwrite an existing file."""
    candidate = directory / file_name
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 1

    while True:
        candidate = directory / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def move_pdf_to_destination(
    pdf_file: Path,
    destination_directory: Path,
    new_name: str,
) -> Path:
    """Rename the file and move it to the destination."""
    destination_directory = destination_directory.expanduser()
    _create_directory(destination_directory, "destination directory")

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


def move_pdf_to_error_folder(
    pdf_file: Path,
    destination_directory: Path,
    error_folder_name: str = "errors",
) -> Path:
    """Move a failed PDF into an error folder inside the destination."""
    error_directory = destination_directory.expanduser() / error_folder_name
    _create_directory(error_directory, "error directory")
    error_file = _available_path(error_directory, pdf_file.name)

    try:
        shutil.move(str(pdf_file), str(error_file))
    except OSError as error:
        raise FileMoveError(
            f"Could not move {pdf_file.name} to {error_file}: {error}"
        ) from error

    return error_file
