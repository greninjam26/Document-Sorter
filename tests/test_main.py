"""Tests for command-line exit results."""

import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import main as main_module
from document_sorter.processing_log import LogWriteError
from document_sorter.sorter import DocumentResult


class MainTests(unittest.TestCase):
    """Verify that processing outcomes produce suitable exit codes."""

    def setUp(self) -> None:
        """Provide a source argument without reading the real command line."""
        print_patcher = patch("builtins.print")
        self.addCleanup(print_patcher.stop)
        print_patcher.start()

        arguments_patcher = patch(
            "main.parse_arguments",
            return_value=Namespace(
                source=Path("source"),
                destination=Path("destination"),
            ),
        )
        self.addCleanup(arguments_patcher.stop)
        arguments_patcher.start()

    @patch(
        "main.write_processing_log",
        return_value=Path("destination/processing_log.csv"),
    )
    @patch(
        "main.sort_documents",
        return_value=[
            DocumentResult(
                Path("document.pdf"),
                sal_barcode="SAL123",
                destination_file=Path("destination/SAL123.pdf"),
            )
        ],
    )
    def test_returns_success_when_every_document_succeeds(
        self,
        _sort_documents,
        _write_processing_log,
    ) -> None:
        """A completely successful batch should exit with zero."""
        self.assertEqual(main_module.main(), 0)

    @patch(
        "main.write_processing_log",
        return_value=Path("destination/processing_log.csv"),
    )
    @patch(
        "main.sort_documents",
        return_value=[DocumentResult(
            Path("document.pdf"), error="damaged PDF")],
    )
    def test_returns_failure_when_a_document_fails(
        self,
        _sort_documents,
        _write_processing_log,
    ) -> None:
        """Any failed document should produce a nonzero exit code."""
        self.assertEqual(main_module.main(), 1)

    @patch(
        "main.write_processing_log",
        side_effect=LogWriteError("disk is full"),
    )
    @patch(
        "main.sort_documents",
        return_value=[
            DocumentResult(
                Path("document.pdf"),
                sal_barcode="SAL123",
                destination_file=Path("destination/SAL123.pdf"),
            )
        ],
    )
    def test_returns_failure_when_log_cannot_be_written(
        self,
        _sort_documents,
        _write_processing_log,
    ) -> None:
        """A log-writing problem should produce a nonzero exit code."""
        self.assertEqual(main_module.main(), 1)


if __name__ == "__main__":
    unittest.main()
