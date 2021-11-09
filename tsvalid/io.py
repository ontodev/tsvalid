"""I/O utilities for TSValid."""

import sys
from typing import List, Optional

from tsvalid.tsvalid import TSValidChecker


def validate_file(
        input_path: str,
        exceptions: Optional[List[str]] = None,
        fail_hard=False,
) -> None:
    """Convert a file.

    :param input_path: The path to the input tsv file
    :param exceptions: list of exceptions
    :param fail_hard: if True, validation will fail when error is encountered.
    """
    checker = TSValidChecker(input_path, exceptions)
    checker.validate_file_level_characteristics(fail=fail_hard)
    checker.validate_line_level_characteristics(fail=fail_hard)
    return
