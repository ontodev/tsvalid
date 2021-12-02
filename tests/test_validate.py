"""Tests for conversion utilities."""
import os
import unittest

from tests.constants import data_dir
from tsvalid.constants import (  # CHECK_FILE_ENCODING,
    CHECK_DUPLICATE_VALUE_IN_HEADER_ROW,
    CHECK_EMPTY_COLUMN,
    CHECK_EMPTY_LAST_ROW,
    CHECK_EMPTY_LINE,
    CHECK_FILE_ENCODING,
    CHECK_LEADING_WHITESPACE,
    CHECK_MISSING_VALUE_IN_HEADER,
    CHECK_NON_ASCII_CHARACTERS,
    CHECK_NUMBER_OF_TABS,
    CHECK_TRAILING_WHITESPACE,
    CHECK_UNEXPECTED_LINE_BREAK_ENCODING,
)
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
        self.assertEqual(
            summary_report[CHECK_UNEXPECTED_LINE_BREAK_ENCODING]["count"], 8
        )
        self.assertEqual(len(summary_report.keys()), 1)

    def test_validate_missing_columns(self):
        """Run validate test on a TSV that has missing columns."""
        summary_report = validate_file(self._file_path("missing_columns"))
        self._test_check(CHECK_MISSING_VALUE_IN_HEADER, summary_report, 1)
        self._test_check(CHECK_EMPTY_COLUMN, summary_report, 1)
        self.assertEqual(len(summary_report.keys()), 2)

    def test_not_utf8(self):
        """Run validate test on a TSV that has missing columns."""
        summary_report = validate_file(self._file_path("not_utf8"))
        self._test_check(CHECK_FILE_ENCODING, summary_report, 1)
        self.assertEqual(len(summary_report.keys()), 1)

    def test_not_ascii(self):
        """Run validate test on a TSV that has non-ASCII chars."""
        summary_report = validate_file(self._file_path("utf8_bad_char"))
        self._test_check(CHECK_NON_ASCII_CHARACTERS, summary_report, 2)
        self.assertEqual(len(summary_report.keys()), 1)

    def test_regex_exception(self):
        """Run validate test on a file with bad utf8 char, using a regex pattern to bypass the check."""
        summary_report = validate_file(
            self._file_path("utf8_bad_char"), exceptions=["W.*"]
        )
        self.assertEqual(len(summary_report.keys()), 0)

    def test_validate_all_wrong(self):
        """Run validate test on a TSV that is broken in various ways."""
        summary_report = validate_file(
            input_path=self._file_path("all_wrong"), comment="#"
        )
        print(summary_report)
        self._test_check(CHECK_MISSING_VALUE_IN_HEADER, summary_report, 1)
        self._test_check(CHECK_NUMBER_OF_TABS, summary_report, 15)
        self._test_check(CHECK_LEADING_WHITESPACE, summary_report, 1)
        self._test_check(CHECK_EMPTY_LINE, summary_report, 1)
        self._test_check(CHECK_EMPTY_LAST_ROW, summary_report, 1)
        self._test_check(CHECK_UNEXPECTED_LINE_BREAK_ENCODING, summary_report, 16)
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
        print(summary_report)
        self.assertEqual(summary_report[CHECK_TRAILING_WHITESPACE]["count"], 2)
        self.assertEqual(summary_report[CHECK_LEADING_WHITESPACE]["count"], 1)
        self.assertEqual(
            summary_report[CHECK_DUPLICATE_VALUE_IN_HEADER_ROW]["count"], 1
        )
        self.assertEqual(len(summary_report.keys()), 3)
