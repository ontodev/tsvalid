"""Tests for conversion utilities."""
import os
import unittest

from tests.constants import data_dir
from tsvalid.io import validate_file


class TestValidate(unittest.TestCase):
    """A test case for conversion utilities."""

    def _file_path(self, test_name) -> str:
        return os.path.join(data_dir, f"test_{test_name}.tsv")

    def test_validate_no_exceptions(self):
        """Run validate test on a TSV that is all correct."""
        validate_file(self._file_path("all_correct"))

    def test_validate_line_ending(self):
        """Run validate test on a TSV that has bad line endings."""
        validate_file(self._file_path("line_ending"))

    def test_validate_missing_columns(self):
        """Run validate test on a TSV that has missing columns."""
        validate_file(self._file_path("missing_columns"))

    def test_validate_all_wrong(self):
        """Run validate test on a TSV that is broken in various ways."""
        validate_file(self._file_path("all_wrong"))

    def test_validate_row_whitespace(self):
        """Run validate test on a TSV that has illegal whitespace in some rows."""
        validate_file(self._file_path("row_whitespace"))

    def test_validate_header_section(self):
        """Run validate test on a TSV that has a header section."""
        validate_file(self._file_path("header_section"))
