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
        summary_report = validate_file(self._file_path("all_correct"))
        print(summary_report)
        self.assertFalse(summary_report)

    def test_validate_line_ending(self):
        """Run validate test on a TSV that has bad line endings."""
        summary_report = validate_file(self._file_path("line_ending"))
        self.assertEqual(summary_report["LinebreakEncodingCheck"]["count"], 157)
        self.assertEqual(len(summary_report.keys()), 1)

    def test_validate_missing_columns(self):
        """Run validate test on a TSV that has missing columns."""
        summary_report = validate_file(self._file_path("missing_columns"))
        self.assertEqual(summary_report["NumberOfTabsCheck"]["count"], 2)
        self.assertEqual(len(summary_report.keys()), 1)

    def test_validate_all_wrong(self):
        """Run validate test on a TSV that is broken in various ways."""
        summary_report = validate_file(self._file_path("all_wrong"))
        self.assertEqual(summary_report["MissingValueInHeaderCheck"]["count"], 1)
        self.assertEqual(summary_report["NumberOfTabsCheck"]["count"], 15)
        self.assertEqual(summary_report["LeadingWhitespaceCheck"]["count"], 1)
        self.assertEqual(summary_report["EmptyLinesCheck"]["count"], 1)
        self.assertEqual(summary_report["EmptyLastRowCheck"]["count"], 1)
        self.assertEqual(summary_report["LinebreakEncodingCheck"]["count"], 31)
        self.assertEqual(len(summary_report.keys()), 6)

    def test_validate_row_whitespace(self):
        """Run validate test on a TSV that has illegal whitespace in some rows."""
        summary_report = validate_file(self._file_path("row_whitespace"))
        self.assertEqual(summary_report["TrailingWhitespaceCheck"]["count"], 1)
        self.assertEqual(summary_report["LeadingWhitespaceCheck"]["count"], 1)
        self.assertEqual(len(summary_report.keys()), 2)
