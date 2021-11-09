"""I/O utilities for TSValid."""
import logging
import sys
from typing import List

from tsvalid.util import calculate_line_endings
from .util import raise_for_bad_path


class TSValidReport:

    def __init__(self):
        self.report = {}

    def add_report(self, error_code, message):
        if error_code not in self.report:
            self.report[error_code] = []
        self.report[error_code].append(message)


class TSValidCheck:
    """ """

    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message

    def error(self, msg):
        logging.error(msg + f" ({self.error_code})")

    def check(self, to_check: str):
        raise NotImplementedError()


class TSValidLineLevelCheck(TSValidCheck):
    def __init__(self, error_code, error_message):
        super().__init__(error_code, error_message)

    def check(self, line, context=None):
        if context is None:
            context = dict()

        report = TSValidReport()

        if 'line_number' not in context:
            context['line_number'] = "Unknown"

        if self.fail_condition(line):
            message = self.get_message(context)
            self.error(message)
            report.add_report(self.error_code, message)
        return report

    def fail_condition(self, line):
        pass

    def get_message(self, context):
        return self.error_message.format(line_number=context['line_number'])


class TSValidFileLevelCheck(TSValidCheck):
    def __init__(self, error_code, error_message):
        super().__init__(error_code, error_message)

    def check(self, file: str):
        raise NotImplementedError()


# Actual checks

class InvalidLineEndingCheck(TSValidFileLevelCheck):
    """
    Error that ensures that no wrong line endings are used.
    """

    def __init__(self):
        super().__init__("E1", "Invalid usage of {0} line ending, with {1} ocurrences overall.")

    def check(self, file):
        report = TSValidReport()
        line_endings = calculate_line_endings(file)
        for line_ending in line_endings:
            if line_ending != b"\n":
                message = self.error_message.format(line_ending, line_endings[line_ending])
                self.error(
                    msg=message
                )
                report.add_report(self.error_code, message)
        return report


class LeadingWhitespaceCheck(TSValidLineLevelCheck):
    """
    Error that ensures that no wrong line endings are used.
    """

    def __init__(self):
        super().__init__("E2", "Illegal whitespace in the beginning of row {line_number}.")

    def fail_condition(self, line):
        return line.startswith(" ")


class TrailingWhitespaceCheck(TSValidLineLevelCheck):
    """
    Error that ensures that no wrong line endings are used.
    """

    def __init__(self):
        super().__init__("E3", "Illegal whitespace in the end of row {line_number}.")

    def fail_condition(self, line: str):
        return line.endswith(" ")


def get_all_file_level_checks() -> List[TSValidFileLevelCheck]:
    return [InvalidLineEndingCheck()]


def get_all_line_level_checks() -> List[TSValidLineLevelCheck]:
    return [TrailingWhitespaceCheck(), LeadingWhitespaceCheck()]


class TSValidChecker:

    def __init__(self, file_path, exceptions):
        raise_for_bad_path(file_path)
        self.file_path = file_path

        if exceptions is None:
            self.exceptions = []

    def validate_file_level_characteristics(self, fail=False):
        checks = get_all_file_level_checks()
        self.run_checks(checks, self.file_path, fail=fail)

    def validate_line_level_characteristics(self, fail=False):
        checks = get_all_line_level_checks()
        with open(self.file_path) as f:
            for line in f:
                self.run_checks(checks, line, fail)

    def run_checks(self, checks: List[TSValidCheck], to_test: str, fail=False):
        for check in checks:
            self.run_check(check, to_test, fail)

    def run_check(self, check: TSValidCheck, to_test, fail=False):
        if check.error_code not in self.exceptions:
            report = check.check(to_test)
            if fail:
                if not report.empty():
                    sys.exit(1)
