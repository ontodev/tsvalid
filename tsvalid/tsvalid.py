"""Checks TSValid."""
import logging
import re
import sys
from typing import Any, Dict, List, Optional

from tsvalid.checks import check_id_function_map
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
    EXCEPTION_MESSAGE,
    KEY_COLUMN,
    KEY_COLUMN_VALUE_EMPTY_COUNTS,
    KEY_CURRENT_LINE,
    KEY_ENCODING,
    KEY_ERROR_CODE,
    KEY_ERROR_ID,
    KEY_ERROR_MESSAGE,
    KEY_ERROR_NAME,
    KEY_ERROR_SUMMARY,
    KEY_FAILED,
    KEY_FILENAME,
    KEY_FIRST_ROW,
    KEY_LAST_LINE,
    KEY_TAB_COUNT,
    test_register,
)
from tsvalid.util import print_summary, print_validation_error, replace_newline_chars


def _handle_check_result(
    result: Dict[str, Any], context=Dict[str, Any], fail_hard=False
):
    if KEY_FAILED in result and result[KEY_FAILED]:
        report_failure(result=result, context=context)
        if fail_hard:
            logging.error("tsvalid: Validation failed: " + str(context))
            sys.exit(1)


def prepare_context_with_error_information(
    result: Dict[str, Any], context: Dict[str, Any]
):
    """Prepare a context for the specific run of a check and update statistics."""
    # TODO Maybe this stuff is better added to the result instead of the context
    check_data = test_register[result[KEY_ERROR_ID]]
    context[KEY_ERROR_ID] = result[KEY_ERROR_ID]
    context[KEY_ERROR_CODE] = check_data[KEY_ERROR_CODE]
    context[KEY_ERROR_MESSAGE] = check_data[KEY_ERROR_MESSAGE].format(
        line_number=context[KEY_CURRENT_LINE], column=context[KEY_COLUMN]
    )
    context[KEY_ERROR_NAME] = check_data[KEY_ERROR_NAME]
    if KEY_CURRENT_LINE not in context:
        context[KEY_CURRENT_LINE] = "NA"
    if KEY_COLUMN not in context:
        context[KEY_COLUMN] = "NA"
    if KEY_ERROR_SUMMARY not in context:
        context[KEY_ERROR_SUMMARY] = {}

    # Updating summary statistics
    error_id = context[KEY_ERROR_ID]
    if error_id not in context[KEY_ERROR_SUMMARY]:
        context[KEY_ERROR_SUMMARY][error_id] = {}
        context[KEY_ERROR_SUMMARY][error_id]["count"] = 0
        context[KEY_ERROR_SUMMARY][error_id]["error_code"] = context[KEY_ERROR_CODE]

    context[KEY_ERROR_SUMMARY][error_id]["count"] = (
        context[KEY_ERROR_SUMMARY][error_id]["count"] + 1
    )


def report_failure(result: Dict[str, Any], context: Dict[str, Any]):
    """Write out failure information from a given check in a context."""
    prepare_context_with_error_information(context=context, result=result)
    print_validation_error(context=context)


def _should_check(check, exceptions):
    for e in exceptions:
        if e == check:
            return False
        else:
            pattern = re.compile(f"^{e}$")
            if pattern.match(check):
                return False
    return True


def validate(
    file_path: str,
    exceptions: Optional[List[str]],
    encoding: str = "utf-8",
    summary=False,
    comment=None,
    fail=False,
) -> Dict[str, Any]:
    """Validate a tsv file and run the hole suite of tests."""
    # Declare context. This is a lightweight dictionary with minimal contextual information such as
    # filename, line number, column number, last or first line, etc
    context: Dict[str, Any] = {
        KEY_CURRENT_LINE: 0,
        KEY_COLUMN: 0,
        KEY_FILENAME: file_path,
        KEY_ENCODING: encoding,
        KEY_COLUMN_VALUE_EMPTY_COUNTS: {},
    }

    line_counter = 0
    last_line_without_new_line = ""
    last_line_with_new_line = ""

    if not exceptions:
        exceptions = []

    # Loop through TSV file line by line and run checks. What makes this loop look a bit unintuitive is the fact
    # that a lot of the checks need some context to run, like checks that apply only to the first line, last line
    # and others

    try:
        with open(file_path, "r", encoding=encoding, newline="") as f:
            for line in f:
                line_counter = line_counter + 1
                context[KEY_CURRENT_LINE] = line_counter
                context[KEY_COLUMN] = 0
                line_without_new_line = replace_newline_chars(line)
                # print(f"Line {line_counter}: {line_without_new_line}")

                # We ignore all rows that start with a #. This is risky, as you may have genuine
                # cases where values in the first column start with a hash
                if not comment or not line_without_new_line.startswith(comment):

                    if KEY_FIRST_ROW not in context:
                        # The Missing Value in Header Check only runs on the first row.
                        context[KEY_FIRST_ROW] = line_counter
                    # Check for empty values and document them in the context. This will later determine
                    # the outcome of the Empty Column Check
                    cell_list = line_without_new_line.split(COLUMN_SEPARATOR)
                    for idx, cell in enumerate(cell_list):
                        context[KEY_COLUMN] = (
                            idx + 1
                        )  # We reserve column 0 for line-level errors

                        for check in [
                            CHECK_LEADING_WHITESPACE,
                            CHECK_TRAILING_WHITESPACE,
                            CHECK_NON_ASCII_CHARACTERS,
                        ]:
                            _run_check(
                                s=cell,
                                check=check,
                                context=context,
                                fail=fail,
                                exceptions=exceptions,
                            )
                            _count_empty_cells(cell, context, str(idx))
                        if context[KEY_FIRST_ROW] == line_counter:
                            _run_check(
                                s=cell,
                                check=CHECK_MISSING_VALUE_IN_HEADER,
                                context=context,
                                fail=fail,
                                exceptions=exceptions,
                            )

                    context[KEY_COLUMN] = 0

                    if KEY_TAB_COUNT not in context:
                        # If it is not in context, it means we are talking about the first row.
                        context[KEY_TAB_COUNT] = line_without_new_line.count(
                            COLUMN_SEPARATOR
                        )
                    else:
                        _run_check(
                            s=line_without_new_line,
                            check=CHECK_NUMBER_OF_TABS,
                            context=context,
                            fail=fail,
                            exceptions=exceptions,
                        )

                    # If this is the first not-commented row, declare that in the context and
                    # run first-row related checks
                    if context[KEY_FIRST_ROW] == line_counter:
                        _run_check(
                            line_without_new_line,
                            check=CHECK_DUPLICATE_VALUE_IN_HEADER_ROW,
                            context=context,
                            fail=fail,
                            exceptions=exceptions,
                        )

                    _run_check(
                        s=line,
                        check=CHECK_UNEXPECTED_LINE_BREAK_ENCODING,
                        context=context,
                        fail=fail,
                        exceptions=exceptions,
                    )

                    if line_counter > 1:
                        # Do the empty line check on the _previous_ line, because the last line
                        # in the file is allowed to be empty.
                        context[KEY_CURRENT_LINE] = line_counter - 1
                        _run_check(
                            s=last_line_without_new_line,
                            check=CHECK_EMPTY_LINE,
                            context=context,
                            fail=fail,
                            exceptions=exceptions,
                        )

                last_line_without_new_line = line_without_new_line
                last_line_with_new_line = line
        context[KEY_COLUMN] = 0

        # Last row should be empty
        context[KEY_LAST_LINE] = context[KEY_CURRENT_LINE]
        _run_check(
            s=last_line_with_new_line,
            check=CHECK_EMPTY_LAST_ROW,
            context=context,
            fail=fail,
            exceptions=exceptions,
        )

        # Check no empty columns
        for column in context[KEY_COLUMN_VALUE_EMPTY_COUNTS]:
            _run_check(
                s=column,
                check=CHECK_EMPTY_COLUMN,
                context=context,
                fail=fail,
                exceptions=exceptions,
            )
    except UnicodeDecodeError as e:
        context[EXCEPTION_MESSAGE] = str(e)
        _run_check(
            s="x",
            check=CHECK_FILE_ENCODING,
            context=context,
            fail=fail,
            exceptions=exceptions,
        )

    # Print summary
    if summary and KEY_ERROR_SUMMARY in context:
        summary_report = context[KEY_ERROR_SUMMARY]
        if summary_report:
            print_summary(summary_report=summary_report, context=context)
        return summary_report
    else:
        return {}


def _run_check(
    s: str, check: str, context: Dict[str, Any], fail=False, exceptions=None
):
    if exceptions is None:
        exceptions = []
    if _should_check(test_register[check][KEY_ERROR_CODE], exceptions):
        result = check_id_function_map[check](context=context, to_check=s)
        _handle_check_result(result=result, context=context, fail_hard=fail)
    else:
        logging.info(f"Check {check} skipped.")


def _count_empty_cells(cell: str, context: Dict[str, Any], idx: str):
    if idx not in context[KEY_COLUMN_VALUE_EMPTY_COUNTS]:
        context[KEY_COLUMN_VALUE_EMPTY_COUNTS][idx] = 0
    if cell.strip():
        context[KEY_COLUMN_VALUE_EMPTY_COUNTS][idx] = (
            context[KEY_COLUMN_VALUE_EMPTY_COUNTS][idx] + 1
        )
