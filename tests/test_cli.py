"""Tests for the command line interface."""
import os
import unittest

from click.testing import CliRunner

from tests.constants import data_dir
from tsvalid.cli import validate


class TestConvert(unittest.TestCase):
    """A test case for conversion utilities."""

    def setUp(self) -> None:
        """Set up test."""
        self.tsv_path = os.path.join(data_dir, "test_missing_columns.tsv")

    def test_validate(self):
        """Test the click CLI directly (validate method)."""
        runner = CliRunner()
        result = runner.invoke(validate, self.tsv_path)
        self.assertEqual(
            result.exit_code,
            0,
            f"tsvalid validation did not as expected: {result.exception}",
        )
