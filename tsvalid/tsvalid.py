"""I/O utilities for TSValid."""
import logging
import re
import sys
from typing import Any, Dict, List, Optional, Union

from .util import raise_for_bad_path, replace_newline_chars

KEY_LAST_LINE = "last_line"
KEY_CURRENT_LINE = "line_number"
KEY_FIRST_ROW = "first_row"
KEY_COLUMN = "column"
KEY_TAB_COUNT = "tab_count"
KEY_COLUMN_VALUE_EMPTY_COUNTS = "column_values_empty"
KEY_FILENAME = "filename"
KEY_CURRENT_CHECK = "error_code"
KEY_CURRENT_MESSAGE = "error_message"
KEY_CURRENT_CHECK_NAME = "error_name"
KEY_ERROR_SUMMARY = "summary"


def print_validation_error(context: Dict[str, Any]):
    """Print an error using the standard linter grammar."""
    print(
        f"{context[KEY_FILENAME]}:{context[KEY_CURRENT_LINE]}:{context[KEY_COLUMN]}: "
        f"{context[KEY_CURRENT_CHECK]}: {context[KEY_CURRENT_MESSAGE]}"
    )


class TSValidCheck:
    """Abstract class for individual file, line or cell level checks."""

    def __init__(self, error_code: str, error_message: str):
        """Construct a TSValid check by setting the error code and default error message."""
        self.error_code = error_code
        self.error_message = error_message

    def log_check_info(self):
        """Log some info on the check being run."""
        logging.info(f"Running check {type(self).__name__}, code {self.error_code}")

    def check(self, to_check: str, context: Dict[str, Any]) -> bool:
        """Check an object (to_check), either a string or byte sequence, for failures."""
        raise NotImplementedError()

    def check_fail_condition_and_report(
        self,
        context: Dict[str, Any],
        to_check: str,
    ):
        """Check the failure condition. If failed, add report to reports list."""
        if self._fail_condition(to_check, context):
            report_failure(context=context, check=self)
            return False
        return True

    def _fail_condition(self, to_check: str, context: Dict[str, Any]) -> bool:
        """Check fail condidation (abstract).

        :param: to_check: the object that should be checked for failure condition
        :param: context: the context of the current check
        :raises NotImplementedError: Should be implemented
        """
        raise NotImplementedError()

    def get_message(self, context: Dict[str, Any]):
        """Format the check message. Default implemenation."""
        return self.error_message.format(
            line_number=context[KEY_CURRENT_LINE], column=context[KEY_COLUMN]
        )


def prepare_context_with_error_information(
    context: Dict[str, Any], check: TSValidCheck
):
    """Prepare a context for the specific run of a check and update statistics."""
    context[KEY_CURRENT_CHECK] = check.error_code
    context[KEY_CURRENT_MESSAGE] = check.get_message(context)
    context[KEY_CURRENT_CHECK_NAME] = type(check).__name__
    if KEY_CURRENT_LINE not in context:
        context[KEY_CURRENT_LINE] = "NA"
    if KEY_COLUMN not in context:
        context[KEY_COLUMN] = "NA"

    if KEY_ERROR_SUMMARY not in context:
        context[KEY_ERROR_SUMMARY] = {}

    # Updating summary statistics
    clz = context[KEY_CURRENT_CHECK_NAME]
    if clz not in context[KEY_ERROR_SUMMARY]:
        context[KEY_ERROR_SUMMARY][clz] = {}
        context[KEY_ERROR_SUMMARY][clz]["count"] = 0
        context[KEY_ERROR_SUMMARY][clz]["error_code"] = context[KEY_CURRENT_CHECK]

    context[KEY_ERROR_SUMMARY][clz]["count"] = (
        context[KEY_ERROR_SUMMARY][clz]["count"] + 1
    )


def report_failure(check: TSValidCheck, context: Dict[str, Any]):
    """Write out failure information from a given check in a context."""
    prepare_context_with_error_information(context, check)
    print_validation_error(context)


class TSValidCellLevelCheck(TSValidCheck):
    """Class to capture cell level checks (as opposed to line or file level checks). Abstract."""

    def __init__(self, error_code: str, error_message: str):
        """Build the TSValid cell level check."""
        super().__init__(error_code, error_message)

    def _fail_condition(self, cell: str, context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: cell: the object that should be checked for failure condition
        :param: context: the context of the current check
        :raises NotImplementedError: Should be implemented
        """
        raise NotImplementedError()

    def check(
        self,
        to_check: str,
        context: Dict[str, Any],
    ) -> bool:
        """Collect the reports on the cell level failure checks."""
        success = True
        if isinstance(to_check, str):
            for idx, v in enumerate(to_check.split("\t")):
                context[KEY_COLUMN] = idx
                self.check_fail_condition_and_report(context, v)
        return success


class TSValidLineLevelCheck(TSValidCheck):
    """Class to capture line level checks (as opposed to cell or file level checks). Abstract."""

    def __init__(self, error_code: str, error_message: str):
        """Build the TSValid cell level check."""
        super().__init__(error_code, error_message)

    def _fail_condition(self, line: str, context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: line: the object that should be checked for failure condition
        :param: context: the context of the current check
        :raises NotImplementedError: Should be implemented
        """
        raise NotImplementedError()

    def check(
        self,
        to_check: str,
        context: Dict[str, Any],
    ):
        """Collect the reports on the line level failure checks."""
        self.check_fail_condition_and_report(context, to_check)


# TSValid Checks


class FileEncodingCheck(TSValidCheck):
    """Error that ensures that no wrong line endings are used."""

    def check(self, to_check: str, context: Dict[str, Any]) -> bool:
        """Check for bad file encoding (not implemented)."""
        logging.info(f"{type(self).__name__} does not implement a check.")
        return False

    def __init__(self):
        """Build a Linebreak-encoding check object."""
        super().__init__("E0", f"Invalid file encoding {{{KEY_CURRENT_LINE}}}.")

    def _fail_condition(self, line: str, context: Dict[str, Any]) -> bool:
        """Check fail condidation (abstract).

        :param: line: the object that should be checked for failure condition
        :param: context: the context of the current check
        :raises NotImplementedError: Should be implemented
        """
        raise NotImplementedError()


class LinebreakEncodingCheck(TSValidLineLevelCheck):
    """Error that ensures that no wrong line endings are used."""

    def __init__(self):
        """Build a Linebreak-encoding check object."""
        super().__init__("E1", f"Invalid line break in line {{{KEY_CURRENT_LINE}}}.")
        self.endings = [
            r"\r\n",
            r"\n\r",
            r"\r",
        ]

    def _fail_condition(self, line: str, context: Dict[str, Any]) -> bool:
        """Check fail condidation (abstract).

        :param: line: the object that should be checked for failure condition
        :param: context: the context of the current check
        :return: True if failure condition is met, otherwise false.
        """
        for x in self.endings:
            if re.search(x, line):
                return True
        return False


def _raise_if_not_string(s: str, context: Dict[str, Any]):
    if not isinstance(s, str):
        raise ValueError(
            f"String passed in is not of type string: {s}, line {context[KEY_CURRENT_LINE]}."
        )


class LeadingWhitespaceCheck(TSValidCellLevelCheck):
    """Error that ensures that lines dont start with a whitespace."""

    def __init__(self):
        """Build a leading whitespace check object."""
        super().__init__(
            "E2",
            f"Redundant leading whitespace in column {{{KEY_COLUMN}}} at line number {{{KEY_CURRENT_LINE}}}.",
        )

    def _fail_condition(self, cell: str, context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: cell: the object that should be checked for failure condition
        :param: context: the context of the current check
        :return: True if failure condition is met, otherwise false.
        :raises ValueError: If line is not a string.
        """
        if isinstance(cell, str):
            return cell.startswith(" ")
        else:
            raise ValueError(
                f"Cell passed in is not of type string: {cell}, line {context[KEY_CURRENT_LINE]}."
            )


class TrailingWhitespaceCheck(TSValidCellLevelCheck):
    """Error that ensures that lines dont end with a whitespace."""

    def __init__(self):
        """Build a trailing whitespace check object."""
        super().__init__(
            "E3",
            f"Redundant trailing whitespace in column {{{KEY_COLUMN}}} at line number {{{KEY_CURRENT_LINE}}}.",
        )

    def _fail_condition(self, cell: str, context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: cell: the object that should be checked for failure condition
        :param: context: the context of the current check
        :return: True if failure condition is met, otherwise false.
        :raises ValueError: If line is not a string.
        """
        if not isinstance(cell, str):
            raise ValueError(
                f"Cell passed in is not of type string: {cell}, line {context[KEY_CURRENT_LINE]}."
            )
        return cell.endswith(" ")


class NumberOfTabsCheck(TSValidLineLevelCheck):
    """Check that ensures that the number of tabs are equal in all rows."""

    def __init__(self):
        """Build a number-of-tabs check object."""
        super().__init__("E4", f"Wrong number of tabs in line {{{KEY_CURRENT_LINE}}}.")

    def _fail_condition(self, line: Union[str, bytes], context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: line: the object that should be checked for failure condition
        :param: context: the context of the current check
        :return: True if failure condition is met, otherwise false.
        :raises ValueError: If line is not a string.
        """
        if KEY_TAB_COUNT not in context:
            return False
        if not isinstance(line, str):
            raise ValueError(f"Line passed in is not of type string: {str(line)}.")
        return line.count("\t") != context[KEY_TAB_COUNT]


class EmptyLinesCheck(TSValidLineLevelCheck):
    """Check to make sure that no rows in the TSV are empty."""

    def __init__(self):
        """Build an empty lines check object."""
        super().__init__("E5", f"Empty line {{{KEY_CURRENT_LINE}}}.")

    def _fail_condition(self, line: Union[str, bytes], context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: line: the object that should be checked for failure condition
        :param: context: the context of the current check
        :return: True if failure condition is met, otherwise false.
        :raises ValueError: If line is not a string.
        """
        if not isinstance(line, str):
            raise ValueError(f"Line passed in is not of type string: {str(line)}.")
        return not line.strip()


class MissingValueInHeaderCheck(TSValidCellLevelCheck):
    """Check that the first row does not have any missing values."""

    def __init__(self):
        """Build a missing value in header check object."""
        super().__init__(
            "E6", f"Header row has missing values, line {{{KEY_CURRENT_LINE}}}."
        )

    def _fail_condition(self, cell: str, context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: cell: the object that should be checked for failure condition
        :param: context: the context of the current check
        :return: True if failure condition is met, otherwise false.
        :raises ValueError: If line is not a string.
        """
        if KEY_FIRST_ROW not in context:
            return False
        if not isinstance(cell, str):
            raise ValueError(f"Cell passed in is not of type string: {str(cell)}.")
        return (
            context[KEY_FIRST_ROW] == context[KEY_CURRENT_LINE]
        ) and not cell.strip()


class DuplicateValueInHeaderCheck(TSValidLineLevelCheck):
    """Check that the first row does not have any missing values."""

    def __init__(self):
        """Build a missing value in header check object."""
        super().__init__(
            "E10", f"Header row has duplicate values, line {{{KEY_CURRENT_LINE}}}."
        )

    def _fail_condition(self, line: str, context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: line: the object that should be checked for failure condition
        :param: context: the context of the current check
        :return: True if failure condition is met, otherwise false.
        :raises ValueError: If line is not a string.
        """
        if not isinstance(line, str):
            raise ValueError(f"Line passed in is not of type string: {str(line)}.")
        line_values = line.split("\t")
        return len(line_values) != len(set(line_values))


class RedundantWhitespaceInCell(TSValidCellLevelCheck):
    """Check that ensures that there is no redundant whitespace in an otherwise empty cell."""

    def __init__(self):
        """Build a redundant whitespace in cell check."""
        super().__init__(
            "E7",
            f"Row contains redundant whitespace in column {{{KEY_COLUMN}}}, line {{{KEY_CURRENT_LINE}}}.",
        )

    def _fail_condition(self, cell: str, context=None):
        """Check fail condidation (abstract).

        :param: cell: the object that should be checked for failure condition
        :param: context: the context of the current check
        :return: True if failure condition is met, otherwise false.
        :raises ValueError: If line is not a string.
        """
        if not isinstance(cell, str):
            raise ValueError(f"Cell passed in is not of type string: {str(cell)}.")
        return cell and not cell.strip()


class EmptyColumnCheck(TSValidLineLevelCheck):
    """Check to look for entirely empty columns."""

    def __init__(self):
        """Build check to look for entirely empty columns."""
        super().__init__(
            "E8", f"TSV file contains empty column at column index {{{KEY_COLUMN}}}."
        )

    def _fail_condition(self, line: str, context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: line: the object that should be checked for failure condition
        :param: context: the context of the current check
        :raises NotImplementedError: This check does not have an automatic fail condition.
        """
        raise NotImplementedError(
            "EmptyColumnCheck is checked by evaluating the context"
        )


class EmptyLastRowCheck(TSValidLineLevelCheck):
    """Check to ensure that the last line in the TSV is an empty line."""

    def __init__(self):
        """Build check to ensure last empty row."""
        super().__init__("E9", "Last row in file should be empty.")

    def _fail_condition(self, line: str, context=None):
        """Check fail condidation (abstract).

        :param: line: the object that should be checked for failure condition
        :param: context: the context of the current check
        :return: True if failure condition is met, otherwise False.
        :raises ValueError: If line is not a string.
        """
        if KEY_LAST_LINE not in context:
            return False
        if not isinstance(line, str):
            raise ValueError(f"Line passed in is not of type string: {str(line)}.")
        return (
            context[KEY_LAST_LINE] == context[KEY_CURRENT_LINE]
        ) and not line.endswith("\n")


# TSValid Checker


def _count_empty_values_in_cells(context: Dict[str, Any], line: str):
    """Detect empty cells in line and counts them up in the context."""
    if KEY_COLUMN_VALUE_EMPTY_COUNTS not in context:
        context[KEY_COLUMN_VALUE_EMPTY_COUNTS] = {}

    cell_list = line.split("\t")
    for idx, cell in enumerate(cell_list):
        if idx not in context[KEY_COLUMN_VALUE_EMPTY_COUNTS]:
            context[KEY_COLUMN_VALUE_EMPTY_COUNTS][idx] = 0
        if cell.strip():
            context[KEY_COLUMN_VALUE_EMPTY_COUNTS][idx] = (
                context[KEY_COLUMN_VALUE_EMPTY_COUNTS][idx] + 1
            )


def print_summary(summary_report: Dict[str, Any], context: Dict[str, Any]):
    """Print summary of all reports gathered by a validation run."""
    if summary_report:
        print("")
        print("##### TSValid Summary #####")
        for e, info in summary_report.items():
            print("")
            print(
                "Error: "
                + " ".join(
                    re.sub(
                        "([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", e)
                    ).split()
                )
            )
            for key, value in info.items():
                print(f" * {key}: {value}")
    else:
        print(f"tsvalid: {context[KEY_FILENAME]}: No errors found.")


class TSValidChecker:
    """Main class to coordinate the execution flow of the validation process."""

    def __init__(self, file_path: str, exceptions: Optional[List[str]], fail=False):
        """Set up TSValid checker class with a filepath and a list of exceptions."""
        raise_for_bad_path(file_path)
        self.file_path = file_path
        if not exceptions:
            self.exceptions: List[str] = []
        else:
            self.exceptions = exceptions
        self.fail = fail

    def validate(self, summary=True, encoding="UTF-8", comment=None) -> Dict[str, Any]:
        """Coordinate the execution of tests in TSValidateChecker."""
        # Declare all the checks that need to be run
        line_level_checks: List[TSValidCheck] = [
            TrailingWhitespaceCheck(),
            LeadingWhitespaceCheck(),
            NumberOfTabsCheck(),
            RedundantWhitespaceInCell(),
        ]
        empty_line_check = EmptyLinesCheck()
        duplicate_value_in_header_check = DuplicateValueInHeaderCheck()
        line_break_encoding_check = LinebreakEncodingCheck()
        empty_last_line_check = EmptyLastRowCheck()
        empty_column_check = EmptyColumnCheck()
        missing_value_in_header_check = MissingValueInHeaderCheck()
        file_encoding_check = FileEncodingCheck()

        # Declare context. This is a lightweight dictionary with minimal contextual information such as
        # filename, line number, column number, last or first line, etc
        context: Dict[str, Any] = {KEY_FILENAME: self.file_path, KEY_COLUMN: "NA"}

        line_counter = 0
        last_line_without_new_line = ""
        last_line_with_new_line = ""

        # Loop through TSV file line by line and run checks. What makes this loop look a bit unintuitive is the fact
        # that a lot of the checks need some context to run, like checks that apply only to the first line, last line
        # and others
        try:
            with open(self.file_path, "r", encoding=encoding, newline="") as f:
                for line in f:
                    line_counter = line_counter + 1
                    context[KEY_CURRENT_LINE] = line_counter
                    context[KEY_COLUMN] = 0
                    line_without_new_line = replace_newline_chars(line)
                    # print(f"Line {line_counter}: {line_without_new_line}")

                    # We ignore all rows that start with a #. This is risky, as you may have genuine
                    # cases where values in the first column start with a hash
                    if not comment or not line_without_new_line.startswith(comment):

                        # Check for empty values and document them in the context. This will later determine
                        # the outcome of the Empty Column Check
                        _count_empty_values_in_cells(context, line)

                        if KEY_TAB_COUNT not in context:
                            # If it is not in context, it means we are talking about the first row.
                            context[KEY_TAB_COUNT] = line_without_new_line.count("\t")

                        # If this is the first not-commented row, declare that in the context and
                        # run first-row related checks
                        if KEY_FIRST_ROW not in context:
                            # The Missing Value in Header Check only runs on the first row.
                            context[KEY_FIRST_ROW] = line_counter
                            self._run_check_and_append_report(
                                context,
                                line_without_new_line,
                                missing_value_in_header_check,
                            )
                            self._run_check_and_append_report(
                                context,
                                line_without_new_line,
                                duplicate_value_in_header_check,
                            )

                        self._run_checks(
                            checks=line_level_checks,
                            to_test=line_without_new_line,
                            context=context,
                        )

                        self._run_check_and_append_report(
                            context,
                            line,
                            line_break_encoding_check,
                        )

                        if line_counter > 1:
                            # Do the empty line check on the _previous_ line, because the last line
                            # in the file is allowed to be empty.
                            context[KEY_CURRENT_LINE] = line_counter - 1
                            self._run_check_and_append_report(
                                context,
                                last_line_without_new_line,
                                empty_line_check,
                            )
                    last_line_without_new_line = line_without_new_line
                    last_line_with_new_line = line
        except UnicodeEncodeError:
            prepare_context_with_error_information(
                context=context, check=file_encoding_check
            )

        context[KEY_COLUMN] = 0

        # Last row should be empty
        context[KEY_LAST_LINE] = context[KEY_CURRENT_LINE]
        self._run_check_and_append_report(
            context,
            last_line_with_new_line,
            empty_last_line_check,
        )

        # Check no empty columns
        for column in context[KEY_COLUMN_VALUE_EMPTY_COUNTS]:
            if context[KEY_COLUMN_VALUE_EMPTY_COUNTS][column] == 0:
                report_failure(check=empty_column_check, context=context)
                self._consider_failing(success=False)

        # Print summary
        if summary and KEY_ERROR_SUMMARY in context:
            summary_report = context[KEY_ERROR_SUMMARY]
            if summary_report:
                print_summary(summary_report=summary_report, context=context)
            return summary_report
        else:
            return {}

    def _run_checks(
        self,
        checks: List[TSValidCheck],
        to_test: str,
        context=Dict[str, Any],
    ):
        for check in checks:
            self._run_check_and_append_report(
                context=context,
                to_check=to_test,
                check=check,
            )

    def _run_check_and_append_report(
        self, context: Dict[str, Any], to_check: str, check: TSValidCheck
    ):
        self._run_check(check=check, to_check=to_check, context=context)

    def _run_check(self, check: TSValidCheck, to_check: str, context: Dict[str, Any]):
        check.log_check_info()
        if check.error_code not in self.exceptions:
            success = check.check(to_check=to_check, context=context)
            self._consider_failing(success)

    def _consider_failing(self, success):
        if self.fail and not success:
            logging.error("Validation failed.")
            sys.exit(1)
