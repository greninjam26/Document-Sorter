"""Find PDF files that are ready to be processed."""

from pathlib import Path


class SourceDirectoryError(ValueError):
    """Used when the source directory cannot be scanned."""


def find_pdf_files(source_directory: Path) -> list[Path]:
    """Return top-level PDF files in *source_directory*, sorted by name.

    This function only locates the files.
    File extensions are matched without regard to capitalization.
    """
    source_directory = source_directory.expanduser()

    if not source_directory.exists():
        raise SourceDirectoryError(
            f"Source directory does not exist: {source_directory}"
        )
    if not source_directory.is_dir():
        raise SourceDirectoryError(
            f"Source path is not a directory: {source_directory}"
        )

    try:
        return sorted(
            (
                path
                for path in source_directory.iterdir()
                if path.is_file() and path.suffix.lower() == ".pdf"
            ),
            key=lambda path: path.name.lower(),
        )
    except OSError as error:
        raise SourceDirectoryError(
            f"Cannot access source directory: {source_directory}"
        ) from error
