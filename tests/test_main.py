"""Tests for command-line exit results."""

import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import main as main_module
from document_sorter.sorter import DocumentResult


class MainTests(unittest.TestCase):
    """Verify that processing outcomes produce suitable exit codes."""

    def setUp(self) -> None:
        """Provide a source argument without reading the real command line."""
        arguments_patcher = patch(
            "main.parse_arguments",
            return_value=Namespace(source=Path("source")),
        )
        self.addCleanup(arguments_patcher.stop)
        arguments_patcher.start()

    @patch(
        "main.sort_documents",
        return_value=[
            DocumentResult(Path("document.pdf"), sal_barcode="SAL123")
        ],
    )
    def test_returns_success_when_every_document_succeeds(
        self,
        _sort_documents,
    ) -> None:
        """A completely successful batch should exit with zero."""
        self.assertEqual(main_module.main(), 0)

    @patch(
        "main.sort_documents",
        return_value=[DocumentResult(Path("document.pdf"), error="damaged PDF")],
    )
    def test_returns_failure_when_a_document_fails(
        self,
        _sort_documents,
    ) -> None:
        """Any failed document should produce a nonzero exit code."""
        self.assertEqual(main_module.main(), 1)


if __name__ == "__main__":
    unittest.main()

