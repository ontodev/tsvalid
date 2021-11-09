"""Tests for conversion utilities."""
import os
import unittest

from tests.constants import data_dir
from tsvalid.io import validate_file


class TestConvert(unittest.TestCase):
    """A test case for conversion utilities."""

    def file_path(self, test_name) -> str:
        return os.path.join(data_dir, f"test_{test_name}.tsv")

    def test_validate_no_exceptions(self):
        validate_file(self.file_path("all_correct"))

    def test_validate_line_ending(self):
        validate_file(self.file_path("line_ending"))

    def test_validate_missing_columns(self):
        validate_file(self.file_path("missing_columns"))

    def test_validate_row_whitespace(self):
        validate_file(self.file_path("row_whitespace"))

    def test_validate_header_section(self):
        validate_file(self.file_path("header_section"))
