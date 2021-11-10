"""I/O utilities for TSValid."""

from typing import List, Optional

from tsvalid.tsvalid import TSValidChecker


def validate_file(
    input_path: str,
    exceptions: Optional[List[str]] = None,
    fail_hard=False,
    summary=True,
) -> None:
    """Convert a file.

    :param input_path: The path to the input tsv file
    :param exceptions: list of exceptions
    :param fail_hard: if True, validation will fail when error is encountered.
    :param summary: If True, a summary of the validation will be printed at the end of the process
    """
    checker = TSValidChecker(input_path, exceptions)
    checker.validate(fail=fail_hard, summary=summary)
