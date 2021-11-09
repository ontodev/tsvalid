"""I/O utilities for TSValid."""
import logging
import re
import sys
from typing import List, Any, Dict, Union

from .util import raise_for_bad_path


class TSValidCheck:
    """ """

    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message

    def error(self, msg):
        print(msg)

    def log_check_info(self):
        logging.info(f"Running check {type(self).__name__}, code {self.error_code}")

    def check(self, to_check: Union[str, bytes], context: Dict[str, Any]):
        raise NotImplementedError()


class TSValidReport:
    """
    A report for a single check
    """

    def __init__(self):
        self.error_code = None
        self.message = None
        self.generic_message = None
        self.error_name = None
        self.context = None

    def add_report(self, check: TSValidCheck, message, context):
        self.error_code = check.error_code
        self.generic_message = check.error_message
        self.error_name = type(check).__name__
        self.message = message
        self.context = context

    def empty(self) -> bool:
        return not self.error_code


class TSValidLineLevelCheck(TSValidCheck):
    def __init__(self, error_code, error_message):
        super().__init__(error_code, error_message)

    def check(self, line, context=None):
        if context is None:
            context = dict()

        report = TSValidReport()

        if 'line_number' not in context:
            context['line_number'] = "Unknown"

        if self.fail_condition(line, context):
            report = self.report_failure(report=report, context=context)
        return report

    def report_failure(self, context, report):
        message = self.get_message(context)
        self.error(message)
        report.add_report(self, message, context=context)
        return report

    def fail_condition(self, line, context=None):
        pass

    def get_message(self, context):
        message = self.error_message.format(line_number=context['line_number'])
        template = f"tsvalid: {context['filename']}:{context['line_number']}:NA: {self.error_code}: {message}"
        return template


class LinebreakEncodingCheck(TSValidLineLevelCheck):
    """
    Error that ensures that no wrong line endings are used.
    """

    def __init__(self):
        super().__init__("E1", "Invalid line break in line {line_number}.")
        self.endings = [
            b"\r\n",
            b"\n\r",
            b"\r",
        ]

    def fail_condition(self, line, context=None):
        for x in self.endings:
            if line.endswith(x):
                return True
        return False


class LeadingWhitespaceCheck(TSValidLineLevelCheck):
    """
    Error that ensures that no wrong line endings are used.
    """

    def __init__(self):
        super().__init__("E2", "Illegal whitespace in the beginning of row {line_number}.")

    def fail_condition(self, line, context=None):
        return line.startswith(" ")


class TrailingWhitespaceCheck(TSValidLineLevelCheck):
    """
    Error that ensures that no wrong line endings are used.
    """

    def __init__(self):
        super().__init__("E3", "Illegal whitespace in the end of row {line_number}.")

    def fail_condition(self, line: str, context=None):
        return line.endswith(" ")


class NumberOfTabsCheck(TSValidLineLevelCheck):
    """
    Error that ensures that no wrong line endings are used.
    """

    def __init__(self):
        super().__init__("E4", "Illegal number of tabs in line {line_number}.")

    def fail_condition(self, line: str, context=None):
        if 'tab_count' not in context:
            return False
        return line.count('\t') != context['tab_count']


class EmptyLinesCheck(TSValidLineLevelCheck):
    """
    Error that ensures that there are no empty lines in the TSV file.
    """

    def __init__(self):
        super().__init__("E5", "Empty line {line_number}.")

    def fail_condition(self, line: str, context=None):
        return not line.strip()


def get_all_line_level_checks_incl_line_break() -> List[TSValidLineLevelCheck]:
    return [LinebreakEncodingCheck()]


def get_all_line_level_checks() -> List[TSValidLineLevelCheck]:
    return [TrailingWhitespaceCheck(), LeadingWhitespaceCheck(), NumberOfTabsCheck()]


def replace_newline_chars(line):
    return line.replace("\r\n", "").replace("\n\r", "").replace("\n", "").replace("\r", "")


def print_summary(reports: List[TSValidReport]):
    summary = {}
    for report in reports:
        clz = report.error_name
        if clz not in summary:
            summary[clz] = {}
            summary[clz]['count'] = 0
            summary[clz]['error_code'] = report.error_code
            summary[clz]['message'] = report.generic_message
        summary[clz]['count'] = summary[clz]['count'] + 1

    print("")
    print("##### TSValid Summary #####")
    for error, report in summary.items():
        print("")
        print("Error: " + " ".join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', error)).split()))
        for key, value in report.items():
            print(f" * {key}: {value}")


class TSValidChecker:

    def __init__(self, file_path, exceptions):
        raise_for_bad_path(file_path)
        self.file_path = file_path

        if exceptions is None:
            self.exceptions = []
        else:
            self.exceptions = exceptions

    def validate(self, fail=False):
        checks = get_all_line_level_checks()
        checks_incl_breaks = get_all_line_level_checks_incl_line_break()
        empty_line_check = EmptyLinesCheck()

        context = {'filename': self.file_path}
        reports = []
        line_counter = 0
        last_line_without_new_line = ""
        with open(self.file_path, "r") as f:
            for line in f:
                line_counter = line_counter + 1
                context['line_number'] = line_counter
                line_without_new_line = replace_newline_chars(line)
                if 'tab_count' not in context and not line_without_new_line.startswith("#"):
                    context['tab_count'] = line_without_new_line.count('\t')
                reports_line = self.run_checks(checks=checks, to_test=line_without_new_line, context=context, fail=fail)
                reports.extend(reports_line)
                if line_counter > 1:
                    empty_line_report = self.run_check(empty_line_check, last_line_without_new_line, {'filename': self.file_path, 'line_number': (line_counter - 1)})
                    if empty_line_report and not empty_line_report.empty():
                        reports.append(empty_line_report)
                last_line_without_new_line = line_without_new_line

        line_counter = 0
        with open(self.file_path, "rb") as fp:
            for line in fp:
                line_counter = line_counter + 1
                context['line_number'] = line_counter
                reports_line = self.run_checks(checks=checks_incl_breaks, to_test=line, context=context, fail=fail)
                reports.extend(reports_line)

        print_summary(reports)

    def run_checks(self, checks: List[TSValidCheck], to_test: Union[str, bytes], context=None, fail=False) \
            -> List[TSValidReport]:
        reports = []
        for check in checks:
            report = self.run_check(check, to_test, context, fail)
            if report and not report.empty():
                reports.append(report)
        return reports

    def run_check(self, check: TSValidCheck, to_test: Union[str, bytes], context=None, fail=False):
        check.log_check_info()
        if check.error_code not in self.exceptions:
            report = check.check(to_test, context)
            if fail and not report.empty:
                sys.exit(1)
            return report
        return None
