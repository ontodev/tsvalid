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
        summary_report = validate_file(self._file_path("line_ending"), comment="#")
        self.assertEqual(summary_report["LinebreakEncodingCheck"]["count"], 8)
        self.assertEqual(len(summary_report.keys()), 1)

    def test_validate_missing_columns(self):
        """Run validate test on a TSV that has missing columns."""
        summary_report = validate_file(self._file_path("missing_columns"))
        self._test_check("MissingValueInHeaderCheck", summary_report, 1)
        self._test_check("EmptyColumnCheck", summary_report, 1)
        self.assertEqual(len(summary_report.keys()), 2)

    def test_validate_all_wrong(self):
        """Run validate test on a TSV that is broken in various ways."""
        summary_report = validate_file(
            input_path=self._file_path("all_wrong"), comment="#"
        )
        print(summary_report)
        self._test_check("MissingValueInHeaderCheck", summary_report, 1)
        self._test_check("NumberOfTabsCheck", summary_report, 15)
        self._test_check("LeadingWhitespaceCheck", summary_report, 1)
        self._test_check("EmptyLinesCheck", summary_report, 1)
        self._test_check("EmptyLastRowCheck", summary_report, 1)
        self._test_check("LinebreakEncodingCheck", summary_report, 16)
        self.assertEqual(len(summary_report.keys()), 6)

    def _test_check(self, check_name, report, count):
        self.assertTrue(check_name in report, msg=f"{check_name} not in report.")
        ct_measured = report[check_name]["count"]
        self.assertEqual(
            ct_measured,
            count,
            msg=f"{check_name} does not have the expected number of occurrences: "
            f"{ct_measured}. Expected: {count}.",
        )

    def test_validate_row_whitespace(self):
        """Run validate test on a TSV that has illegal whitespace in some rows."""
        summary_report = validate_file(self._file_path("row_whitespace"), comment="#")
        self.assertEqual(summary_report["TrailingWhitespaceCheck"]["count"], 1)
        self.assertEqual(summary_report["LeadingWhitespaceCheck"]["count"], 1)
        self.assertEqual(summary_report["DuplicateValueInHeaderCheck"]["count"], 1)
        self.assertEqual(len(summary_report.keys()), 3)
