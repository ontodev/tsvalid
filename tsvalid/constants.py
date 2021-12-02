"""Constants for TSValid."""
import re

KEY_LAST_LINE = "last_line"
KEY_CURRENT_LINE = "line_number"
KEY_FIRST_ROW = "first_row"
KEY_COLUMN = "column"
KEY_TAB_COUNT = "tab_count"
KEY_COLUMN_VALUE_EMPTY_COUNTS = "column_values_empty"
KEY_FILENAME = "filename"
KEY_FAILED = "failed"
KEY_ENCODING = "encoding"
KEY_ERROR_ID = "error_id"
KEY_ERROR_CODE = "error_code"
KEY_ERROR_MESSAGE = "error_message"
KEY_ERROR_NAME = "error_name"
KEY_ERROR_FUNCTION = "error_function"
KEY_ERROR_SUMMARY = "summary"
COLUMN_SEPARATOR = "\t"
EXCEPTION_MESSAGE = "exception"

CHECK_LEADING_WHITESPACE = "leadingWhitespaceCheck"
CHECK_TRAILING_WHITESPACE = "trailingWhitespaceCheck"
CHECK_NON_ASCII_CHARACTERS = "nonAsciiCharacterCheck"
CHECK_FILE_ENCODING = "fileEncodingCheck"
CHECK_NUMBER_OF_TABS = "numberOfTabsCheck"
CHECK_UNEXPECTED_LINE_BREAK_ENCODING = "unexpectedLineBreakEncoding"
CHECK_EMPTY_LINE = "emptyLine"
CHECK_MISSING_VALUE_IN_HEADER = "missingValueInHeader"
CHECK_EMPTY_COLUMN = "emptyColumn"
CHECK_EMPTY_LAST_ROW = "emptyLastRow"
CHECK_DUPLICATE_VALUE_IN_HEADER_ROW = "duplicateValueInHeaderRow"

ILLEGAL_LINE_ENDINGS = [
    r"\r\n",
    r"\n\r",
    r"\r",
]

REGEX_WHITESPACE_END_OF_STRING = re.compile(r".*\s$")
REGEX_WHITESPACE_START_OF_STRING = re.compile(r"^\s")

test_register = {
    CHECK_FILE_ENCODING: {
        KEY_ERROR_CODE: "E0",
        KEY_ERROR_NAME: "Unexpected File Encoding",
        KEY_ERROR_MESSAGE: f"Invalid file encoding {{{KEY_CURRENT_LINE}}}.",
    },
    CHECK_UNEXPECTED_LINE_BREAK_ENCODING: {
        KEY_ERROR_CODE: "E1",
        KEY_ERROR_NAME: "Line break encoding",
        KEY_ERROR_MESSAGE: f"Invalid line break in line {{{KEY_CURRENT_LINE}}}.",
    },
    CHECK_LEADING_WHITESPACE: {
        KEY_ERROR_CODE: "E2",
        KEY_ERROR_NAME: "Redundant leading whitespace",
        KEY_ERROR_MESSAGE: f"Redundant leading whitespace in column {{{KEY_COLUMN}}} "
        f"at line number {{{KEY_CURRENT_LINE}}}.",
    },
    CHECK_TRAILING_WHITESPACE: {
        KEY_ERROR_CODE: "E3",
        KEY_ERROR_NAME: "Redundant trailing whitespace",
        KEY_ERROR_MESSAGE: f"Redundant trailing whitespace in column {{{KEY_COLUMN}}} "
        f"at line number {{{KEY_CURRENT_LINE}}}.",
    },
    CHECK_NUMBER_OF_TABS: {
        KEY_ERROR_CODE: "E4",
        KEY_ERROR_NAME: "Wrong number of tabs",
        KEY_ERROR_MESSAGE: f"Number of tabs in line {{{KEY_CURRENT_LINE}}} does not match tabs in header.",
    },
    CHECK_EMPTY_LINE: {
        KEY_ERROR_CODE: "E5",
        KEY_ERROR_NAME: "Empty line",
        KEY_ERROR_MESSAGE: f"Empty line {{{KEY_CURRENT_LINE}}}.",
    },
    CHECK_MISSING_VALUE_IN_HEADER: {
        KEY_ERROR_CODE: "E6",
        KEY_ERROR_NAME: "Missing value in header",
        KEY_ERROR_MESSAGE: f"Header row has missing values, line {{{KEY_CURRENT_LINE}}}.",
    },
    CHECK_EMPTY_COLUMN: {
        KEY_ERROR_CODE: "E8",
        KEY_ERROR_NAME: "Empty column",
        KEY_ERROR_MESSAGE: f"TSV file contains empty column at column index {{{KEY_COLUMN}}}.",
    },
    CHECK_EMPTY_LAST_ROW: {
        KEY_ERROR_CODE: "E9",
        KEY_ERROR_NAME: "Empty last row",
        KEY_ERROR_MESSAGE: "Last row in file should be empty.",
    },
    CHECK_DUPLICATE_VALUE_IN_HEADER_ROW: {
        KEY_ERROR_CODE: "E10",
        KEY_ERROR_NAME: "Duplicate value in header",
        KEY_ERROR_MESSAGE: f"Header row has duplicate values, line {{{KEY_CURRENT_LINE}}}.",
    },
    CHECK_NON_ASCII_CHARACTERS: {
        KEY_ERROR_CODE: "W1",
        KEY_ERROR_NAME: "Non ASCII character in cell.",
        KEY_ERROR_MESSAGE: f"Non ASCII character in column {{{KEY_COLUMN}}} at line number {{{KEY_CURRENT_LINE}}}.",
    },
}
