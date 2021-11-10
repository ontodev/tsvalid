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


def error(context: Dict[str, Any]):
    """Print an error using the standard linter grammar."""
    print(
        f"tsvalid: {context[KEY_FILENAME]}:{context[KEY_CURRENT_LINE]}:{context[KEY_COLUMN]}: "
        f"{context[KEY_CURRENT_CHECK]}: {context[KEY_CURRENT_MESSAGE]}"
    )


class TSValidReport:
    """A report for a single check."""

    def __init__(self):
        """Initialise an empty TSValid report."""
        self.error_code = None
        self.message = None
        self.generic_message = None
        self.error_name = None
        self.context = None

    def add_report(self, context: Dict[str, Any]):
        """Add a report from contextual information."""
        self._add_report_no_check(
            context[KEY_CURRENT_CHECK],
            context[KEY_CURRENT_MESSAGE],
            context[KEY_CURRENT_CHECK_NAME],
            context[KEY_CURRENT_MESSAGE],
            context,
        )

    def _add_report_no_check(
        self,
        error_code: str,
        generic_message: str,
        error_name: str,
        message: str,
        context: Dict[str, Any],
    ):
        self.error_code = error_code
        self.generic_message = generic_message
        self.error_name = error_name
        self.message = message
        self.context = context.copy()

    def empty(self) -> bool:
        """Check whether report is empty, i.e has not been set yet."""
        return not self.error_code


class TSValidCheck:
    """Abstract class for individual file, line or cell level checks."""

    def __init__(self, error_code: str, error_message: str):
        """Construct a TSValid check by setting the error code and default error message."""
        self.error_code = error_code
        self.error_message = error_message

    def log_check_info(self):
        """Log some info on the check being run."""
        logging.info(f"Running check {type(self).__name__}, code {self.error_code}")

    def check(
        self, to_check: Union[str, bytes], context: Dict[str, Any]
    ) -> List[TSValidReport]:
        """Check an object (to_check), either a string or byte sequence, for failures."""
        reports: List[TSValidReport] = []
        self.collect_reports(context, to_check, reports)
        return reports

    def add_report_if_failure(
        self,
        context: Dict[str, Any],
        to_check: Union[str, bytes],
        reports: List[TSValidReport],
    ):
        """Check the failure condition. If failed, add report to reports list."""
        if self.fail_condition(to_check, context):
            report = report_failure(context=context, check=self)
            if report:
                reports.append(report)

    def fail_condition(self, to_check: Union[str, bytes], context: Dict[str, Any]):
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

    def collect_reports(
        self,
        context: Dict[str, Any],
        to_check: Union[str, bytes],
        reports: List[TSValidReport],
    ):
        """Collect the reports on the failure checks (abstract)."""
        raise NotImplementedError()


def prepare_context_with_error_information(
    context: Dict[str, Any], check: TSValidCheck
):
    """Prepare a context for the specific run of a check."""
    context[KEY_CURRENT_CHECK] = check.error_code
    context[KEY_CURRENT_MESSAGE] = check.get_message(context)
    context[KEY_CURRENT_CHECK_NAME] = type(check).__name__
    if KEY_CURRENT_LINE not in context:
        context[KEY_CURRENT_LINE] = "NA"


def report_failure(check: TSValidCheck, context: Dict[str, Any]):
    """Write out failure information from a given check in a context."""
    prepare_context_with_error_information(context, check)
    error(context)
    report = TSValidReport()
    report.add_report(context=context)
    return report


class TSValidCellLevelCheck(TSValidCheck):
    """Class to capture cell level checks (as opposed to line or file level checks). Abstract."""

    def __init__(self, error_code: str, error_message: str):
        """Build the TSValid cell level check."""
        super().__init__(error_code, error_message)

    def fail_condition(self, cell: Union[str, bytes], context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: cell: the object that should be checked for failure condition
        :param: context: the context of the current check
        :raises NotImplementedError: Should be implemented
        """
        raise NotImplementedError()

    def collect_reports(
        self,
        context: Dict[str, Any],
        to_check: Union[str, bytes],
        reports: List[TSValidReport],
    ):
        """Collect the reports on the cell level failure checks."""
        if isinstance(to_check, str):
            for idx, v in enumerate(to_check.split("\t")):
                context[KEY_COLUMN] = idx
                self.add_report_if_failure(context, v, reports)


class TSValidLineLevelCheck(TSValidCheck):
    """Class to capture line level checks (as opposed to cell or file level checks). Abstract."""

    def __init__(self, error_code: str, error_message: str):
        """Build the TSValid cell level check."""
        super().__init__(error_code, error_message)

    def fail_condition(self, line: Union[str, bytes], context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: line: the object that should be checked for failure condition
        :param: context: the context of the current check
        :raises NotImplementedError: Should be implemented
        """
        raise NotImplementedError()

    def collect_reports(
        self,
        context: Dict[str, Any],
        to_check: Union[str, bytes],
        reports: List[TSValidReport],
    ):
        """Collect the reports on the line level failure checks."""
        self.add_report_if_failure(context, to_check, reports)


# TSValid Checks


class LinebreakEncodingCheck(TSValidLineLevelCheck):
    """Error that ensures that no wrong line endings are used."""

    def __init__(self):
        """Build a Linebreak-encoding check object."""
        super().__init__("E1", "Invalid line break in line {line_number}.")
        self.endings = [
            b"\r\n",
            b"\n\r",
            b"\r",
        ]

    def fail_condition(self, line: Union[str, bytes], context: Dict[str, Any]) -> bool:
        """Check fail condidation (abstract).

        :param: line: the object that should be checked for failure condition
        :param: context: the context of the current check
        :return: True if failure condition is met, otherwise false.
        """
        for x in self.endings:
            if line.endswith(x):
                return True
        return False


class LeadingWhitespaceCheck(TSValidLineLevelCheck):
    """Error that ensures that lines dont start with a whitespace."""

    def __init__(self):
        """Build a leading whitespace check object."""
        super().__init__(
            "E2", "Illegal whitespace in the beginning of row {line_number}."
        )

    def fail_condition(self, line: Union[str, bytes], context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: line: the object that should be checked for failure condition
        :param: context: the context of the current check
        :return: True if failure condition is met, otherwise false.
        :raises ValueError: If line is not a string.
        """
        if isinstance(line, str):
            return line.startswith(" ")
        else:
            raise ValueError("Line passed in is not of type string: {line}.")


class TrailingWhitespaceCheck(TSValidLineLevelCheck):
    """Error that ensures that lines dont end with a whitespace."""

    def __init__(self):
        """Build a trailing whitespace check object."""
        super().__init__("E3", "Illegal whitespace in the end of row {line_number}.")

    def fail_condition(self, line: Union[str, bytes], context: Dict[str, Any]):
        """Check fail condidation (abstract).

        :param: line: the object that should be checked for failure condition
        :param: context: the context of the current check
        :return: True if failure condition is met, otherwise false.
        :raises ValueError: If line is not a string.
        """
        if not isinstance(line, str):
            raise ValueError(f"Line passed in is not of type string: {str(line)}.")
        return line.endswith(" ")


class NumberOfTabsCheck(TSValidLineLevelCheck):
    """Check that ensures that the number of tabs are equal in all rows."""

    def __init__(self):
        """Build a number-of-tabs check object."""
        super().__init__("E4", "Illegal number of tabs in line {line_number}.")

    def fail_condition(self, line: Union[str, bytes], context: Dict[str, Any]):
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
        super().__init__("E5", "Empty line {line_number}.")

    def fail_condition(self, line: Union[str, bytes], context: Dict[str, Any]):
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
        super().__init__("E6", "Header row has missing values, line {line_number}.")

    def fail_condition(self, cell: Union[str, bytes], context: Dict[str, Any]):
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


class RedundantWhitespaceInCell(TSValidCellLevelCheck):
    """Check that ensures that there is no redundant whitespace in an otherwise empty cell."""

    def __init__(self):
        """Build a redundant whitespace in cell check."""
        super().__init__(
            "E7",
            "Row contains redundant whitespace in column {column}, line {line_number}.",
        )

    def fail_condition(self, cell: Union[str, bytes], context=None):
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
            "E8", "TSV file contains empty column at column index {column}."
        )

    def fail_condition(self, line: Union[str, bytes], context: Dict[str, Any]):
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

    def fail_condition(self, line: Union[str, bytes], context=None):
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


def prepare_summary(reports) -> Dict[str, Any]:
    """Prepare summary report."""
    summary: Dict[str, Any] = {}
    for report in reports:
        clz = report.error_name
        if clz not in summary:
            summary[clz] = {}
            summary[clz]["count"] = 0
            summary[clz]["error_code"] = report.error_code
            summary[clz]["message"] = report.generic_message
        summary[clz]["count"] = summary[clz]["count"] + 1
    return summary


class TSValidChecker:
    """Main class to coordinate the execution flow of the validation process."""

    def __init__(self, file_path: str, exceptions: Optional[List[str]]):
        """Set up TSValid checker class with a filepath and a list of exceptions."""
        raise_for_bad_path(file_path)
        self.file_path = file_path
        if not exceptions:
            self.exceptions: List[str] = []
        else:
            self.exceptions = exceptions

    def validate(self, fail=False, summary=True) -> Dict[str, Any]:
        """Coordinate the execution of tests in TSValidateChecker."""
        # Declare all the checks that need to be run
        line_level_checks: List[TSValidCheck] = [
            TrailingWhitespaceCheck(),
            LeadingWhitespaceCheck(),
            NumberOfTabsCheck(),
            RedundantWhitespaceInCell(),
        ]
        byte_level_checks: List[TSValidCheck] = [
            LinebreakEncodingCheck(),
        ]
        empty_line_check = EmptyLinesCheck()
        empty_last_line_check = EmptyLastRowCheck()
        empty_column_check = EmptyColumnCheck()
        missing_value_in_header_check = MissingValueInHeaderCheck()

        # Declare context. This is a lightweight dictionary with minimal contextual information such as
        # filename, line number, column number, last or first line, etc
        context: Dict[str, Any] = {KEY_FILENAME: self.file_path, KEY_COLUMN: "NA"}

        reports: List[TSValidReport] = []
        line_counter = 0
        last_line_without_new_line = ""
        last_line_with_new_line = ""

        # Loop through TSV file line by line and run checks. What makes this loop look a bit unintuitive is the fact
        # that a lot of the checks need some context to run, like checks that apply only to the first line, last line
        # and others
        with open(self.file_path, "r") as f:
            for line in f:
                line_counter = line_counter + 1
                context[KEY_CURRENT_LINE] = line_counter
                line_without_new_line = replace_newline_chars(line)
                # print(f"Line {line_counter}: {line_without_new_line}")

                # We ignore all rows that start with a #. This is risky, as you may have genuine
                # cases where values in the first column start with a hash
                if not line_without_new_line.startswith("#"):

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
                            reports,
                        )

                    reports_line = self._run_checks(
                        checks=line_level_checks,
                        to_test=line_without_new_line,
                        context=context,
                        fail=fail,
                    )
                    reports.extend(reports_line)

                    if line_counter > 1:
                        # Do the empty line check on the _previous_ line, because the last line
                        # in the file is allowed to be empty.
                        context[KEY_CURRENT_LINE] = line_counter - 1
                        self._run_check_and_append_report(
                            context,
                            last_line_without_new_line,
                            empty_line_check,
                            reports,
                        )
                last_line_without_new_line = line_without_new_line
                last_line_with_new_line = line

        # Last row should be empty
        context[KEY_LAST_LINE] = context[KEY_CURRENT_LINE]
        self._run_check_and_append_report(
            context, last_line_with_new_line, empty_last_line_check, reports
        )

        # Check no empty columns
        for column in context[KEY_COLUMN_VALUE_EMPTY_COUNTS]:
            if context[KEY_COLUMN_VALUE_EMPTY_COUNTS][column] == 0:
                r = report_failure(empty_column_check, context)
                reports.append(r)

        # Loop through the bystream to run byte-level checks
        line_counter = 0
        with open(self.file_path, "rb") as fp:
            for bl in fp:
                line_counter = line_counter + 1
                context[KEY_CURRENT_LINE] = line_counter
                reports_line = self._run_checks(
                    checks=byte_level_checks, to_test=bl, context=context, fail=fail
                )
                reports.extend(reports_line)

        # Print summary
        summary_report = prepare_summary(reports)
        if summary:
            print_summary(summary_report=summary_report, context=context)
        return summary_report

    def _run_checks(
        self,
        checks: List[TSValidCheck],
        to_test: Union[str, bytes],
        context=Dict[str, Any],
        fail=False,
    ) -> List[TSValidReport]:
        reports: List[TSValidReport] = []
        for check in checks:
            self._run_check_and_append_report(
                context=context,
                to_check=to_test,
                check=check,
                reports=reports,
                fail=fail,
            )
        return reports

    def _run_check_and_append_report(
        self, context, to_check, check, reports, fail=False
    ):
        reps = self._run_check(
            check=check, to_check=to_check, context=context, fail=fail
        )
        if reps:
            reports.extend(reps)

    def _run_check(
        self, check: TSValidCheck, to_check: Union[str, bytes], context=None, fail=False
    ) -> List[TSValidReport]:
        check.log_check_info()
        reports = []
        if check.error_code not in self.exceptions:
            reps = check.check(to_check, context)
            if fail and reps:
                sys.exit(1)
            reports.extend(reps)
        return reports
