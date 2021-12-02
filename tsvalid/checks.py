"""All tsvalid check functions."""

# A check has exactly two arguments (a string, representing the value of a line, a cell or another parameter,
# and a dictinary representing the context. A check marshals a result object, which is also a dictionary.
import re
import string
from typing import Any, Dict

from tsvalid.constants import (
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
    COLUMN_SEPARATOR,
    ILLEGAL_LINE_ENDINGS,
    KEY_COLUMN_VALUE_EMPTY_COUNTS,
    KEY_CURRENT_LINE,
    KEY_ENCODING,
    KEY_ERROR_ID,
    KEY_FAILED,
    KEY_FIRST_ROW,
    KEY_LAST_LINE,
    KEY_TAB_COUNT,
    REGEX_WHITESPACE_END_OF_STRING,
    REGEX_WHITESPACE_START_OF_STRING,
)


def _raise_if_not_string(s: str, context: Dict[str, Any]):
    if not isinstance(s, str):
        raise ValueError(
            f"String passed in is not of type string: {s}, line {context[KEY_CURRENT_LINE]}."
        )


def _before_check(s: str, context: Dict[str, Any], check: str) -> Dict[str, Any]:
    results = {KEY_ERROR_ID: check}
    _raise_if_not_string(s=s, context=context)
    return results


def unexpected_file_encoding_check(
    context: Dict[str, Any], to_check: str
) -> Dict[str, Any]:
    """Check that an encoding provided corresponds to the expected encoding."""
    encoding = to_check
    results = _before_check(s=encoding, context=context, check=CHECK_FILE_ENCODING)

    if encoding.lower() != context[KEY_ENCODING].lower():
        results[KEY_FAILED] = True

    return results


def unexpected_line_break_encoding_check(
    context: Dict[str, Any], to_check: str
) -> Dict[str, Any]:
    """Check that a line ends with the expected line break."""
    results = _before_check(
        s=to_check, context=context, check=CHECK_UNEXPECTED_LINE_BREAK_ENCODING
    )

    for x in ILLEGAL_LINE_ENDINGS:
        if re.search(x, to_check):
            results[KEY_FAILED] = True
            break

    return results


def leading_whitespace_check(context: Dict[str, Any], to_check: str) -> Dict[str, Any]:
    """Check that a cell does not contain leading whitespace."""
    results = _before_check(s=to_check, context=context, check=CHECK_LEADING_WHITESPACE)

    if re.match(REGEX_WHITESPACE_START_OF_STRING, to_check):
        results[KEY_FAILED] = True

    return results


def trailing_whitespace_check(context: Dict[str, Any], to_check: str) -> Dict[str, Any]:
    """Check that a cell does not contain trailing whitespace."""
    results = _before_check(
        s=to_check, context=context, check=CHECK_TRAILING_WHITESPACE
    )

    if re.match(REGEX_WHITESPACE_END_OF_STRING, to_check):
        results[KEY_FAILED] = True

    return results


def bad_encoding_in_char(context: Dict[str, Any], to_check: str) -> Dict[str, Any]:
    """Check that a cell does not contain any badly encoded characters."""
    results = _before_check(
        s=to_check, context=context, check=CHECK_NON_ASCII_CHARACTERS
    )

    for char in to_check:
        if char not in string.printable:
            results[KEY_FAILED] = True
            break

    return results


def irregular_number_of_tabs_check(
    context: Dict[str, Any], to_check: str
) -> Dict[str, Any]:
    """Check that a line does not contain an irregular number of tabs."""
    results = _before_check(s=to_check, context=context, check=CHECK_NUMBER_OF_TABS)

    if KEY_TAB_COUNT in context:
        if to_check.count(COLUMN_SEPARATOR) != context[KEY_TAB_COUNT]:
            results[KEY_FAILED] = True

    return results


def empty_line_check(context: Dict[str, Any], to_check: str) -> Dict[str, Any]:
    """Check to make sure that no rows in the TSV are empty."""
    results = _before_check(s=to_check, context=context, check=CHECK_EMPTY_LINE)

    if not to_check.strip():
        results[KEY_FAILED] = True

    return results


def missing_value_in_header_cell_check(
    context: Dict[str, Any], to_check: str
) -> Dict[str, Any]:
    """Check that the first row does not have any missing values."""
    results = _before_check(
        s=to_check, context=context, check=CHECK_MISSING_VALUE_IN_HEADER
    )

    if KEY_FIRST_ROW in context:
        if (
            context[KEY_FIRST_ROW] == context[KEY_CURRENT_LINE]
        ) and not to_check.strip():
            results[KEY_FAILED] = True

    return results


def empty_column_check(context: Dict[str, Any], to_check: str) -> Dict[str, Any]:
    """Check that the tsv file does not contain an entirely empty table."""
    column = to_check
    results = _before_check(s=column, context=context, check=CHECK_EMPTY_COLUMN)

    if KEY_LAST_LINE in context:
        if context[KEY_LAST_LINE] == context[KEY_CURRENT_LINE]:
            if column in context[KEY_COLUMN_VALUE_EMPTY_COUNTS]:
                if context[KEY_COLUMN_VALUE_EMPTY_COUNTS][column] == 0:
                    results[KEY_FAILED] = True

    return results


def empty_last_row_check(context: Dict[str, Any], to_check: str) -> Dict[str, Any]:
    """Check to make sure that no rows in the TSV are empty."""
    results = _before_check(s=to_check, context=context, check=CHECK_EMPTY_LAST_ROW)

    if KEY_LAST_LINE in context:
        if context[KEY_LAST_LINE] == context[
            KEY_CURRENT_LINE
        ] and not to_check.endswith("\n"):
            results[KEY_FAILED] = True

    return results


def duplicate_value_in_header_row_check(
    context: Dict[str, Any], to_check: str
) -> Dict[str, Any]:
    """Check that the first row does not have any missing values."""
    results = _before_check(
        s=to_check, context=context, check=CHECK_DUPLICATE_VALUE_IN_HEADER_ROW
    )

    line_values = to_check.split(COLUMN_SEPARATOR)
    if len(line_values) != len(set(line_values)):
        results[KEY_FAILED] = True

    return results


check_id_function_map = {
    CHECK_LEADING_WHITESPACE: leading_whitespace_check,
    CHECK_TRAILING_WHITESPACE: trailing_whitespace_check,
    CHECK_FILE_ENCODING: unexpected_file_encoding_check,
    CHECK_NUMBER_OF_TABS: irregular_number_of_tabs_check,
    CHECK_UNEXPECTED_LINE_BREAK_ENCODING: unexpected_line_break_encoding_check,
    CHECK_EMPTY_LINE: empty_line_check,
    CHECK_MISSING_VALUE_IN_HEADER: missing_value_in_header_cell_check,
    CHECK_EMPTY_COLUMN: empty_column_check,
    CHECK_EMPTY_LAST_ROW: empty_last_row_check,
    CHECK_DUPLICATE_VALUE_IN_HEADER_ROW: duplicate_value_in_header_row_check,
    CHECK_NON_ASCII_CHARACTERS: bad_encoding_in_char,
}

check_function_id_map = {v: k for k, v in check_id_function_map.items()}
