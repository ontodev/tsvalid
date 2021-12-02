"""I/O utilities for TSValid."""

from typing import Any, Dict, List, Optional

from tsvalid.tsvalid import validate


def validate_file(
    input_path: str,
    exceptions: Optional[List[str]] = None,
    fail_hard=False,
    summary=True,
    encoding="UTF-8",
    comment=None,
) -> Dict[str, Any]:
    """Convert a file.

    :param input_path: The path to the input tsv file
    :param exceptions: list of exceptions
    :param fail_hard: if True, validation will fail when error is encountered.
    :param summary: If True, a summary of the validation will be printed at the end of the process
    :param encoding: Encoding for TSV file
    :param comment: Char denoting a comment character. If and only if a row starts with that comment character,
                        it is not included in the validation process.
    :returns: a dictionary with a summary of the validation run
    """
    return validate(
        file_path=input_path,
        exceptions=exceptions,
        fail=fail_hard,
        summary=summary,
        encoding=encoding,
        comment=comment,
    )
