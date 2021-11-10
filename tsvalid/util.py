"""Utilities for TSValid."""

import os
from typing import Any, Dict

import validators


def raise_for_bad_path(file_path: str) -> None:
    """Raise exception if file path is invalid.

    :param file_path: File path
    :raises ValueError: Invalid file path
    """
    if not validators.url(file_path) and not os.path.exists(file_path):
        raise ValueError(f"{file_path} is not a valid file path or url.")


def replace_newline_chars(string: str) -> str:
    """If the incoming string ends with a line break, remove it.

    :param string: String from which to prune line breaks.
    :return: The string without the line breaks
    """
    return (
        string.replace("\r\n", "")
        .replace("\n\r", "")
        .replace("\n", "")
        .replace("\r", "")
    )


def calculate_line_endings(path: str) -> Dict[Any, Any]:
    """Count the number of line endings in a file.

    From https://stackoverflow.com/questions/29695861/get-newline-stats-for-a-text-file-in-python.
    :param: path: File to analyse
    :return: a dictionary of counts
    """
    endings = [
        b"\r\n",
        b"\n\r",
        b"\n",
        b"\r",
    ]
    counts = dict.fromkeys(endings, 0)

    with open(path, "rb") as fp:
        for line in fp:
            for x in endings:
                if line.endswith(x):
                    counts[x] += 1
                    break
    return counts
