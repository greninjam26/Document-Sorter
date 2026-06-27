"""Write processing results to a CSV log file."""

import csv
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from document_sorter.sorter import DocumentResult


LOG_HEADERS = (
    "timestamp",
    "status",
    "source_file",
    "sal_barcode",
    "destination_file",
    "error_file",
    "error",
)


class LogWriteError(OSError):
    """Used when the processing log cannot be written."""


def write_processing_log(
    results: list["DocumentResult"],
    destination_directory: Path,
    log_file_name: str = "processing_log.csv",
) -> Path:
    """Append processing results to a CSV log in the destination folder."""
    destination_directory = destination_directory.expanduser()
    log_file = destination_directory / log_file_name

    try:
        destination_directory.mkdir(parents=True, exist_ok=True)
        should_write_headers = (
            not log_file.exists() or log_file.stat().st_size == 0
        )

        with log_file.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=LOG_HEADERS)
            if should_write_headers:
                writer.writeheader()

            timestamp = datetime.now().isoformat(timespec="seconds")
            for result in results:
                writer.writerow(_result_to_log_row(result, timestamp))
    except OSError as error:
        raise LogWriteError(f"Could not write processing log: {error}") from error

    return log_file


def _result_to_log_row(
    result: "DocumentResult",
    timestamp: str,
) -> dict[str, str]:
    """Convert one document result to a CSV row."""
    return {
        "timestamp": timestamp,
        "status": "success" if result.succeeded else "error",
        "source_file": str(result.source_file),
        "sal_barcode": result.sal_barcode or "",
        "destination_file": _optional_path_to_string(result.destination_file),
        "error_file": _optional_path_to_string(result.error_file),
        "error": result.error or "",
    }


def _optional_path_to_string(path: Path | None) -> str:
    """Return a path as text, or an empty string when there is no path."""
    if path is None:
        return ""

    return str(path)
