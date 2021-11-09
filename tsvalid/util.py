"""Utilities for TSValid."""

import os
from typing import Dict, Any

import validators


def raise_for_bad_path(file_path: str) -> None:
    """Raise exception if file path is invalid.

    :param file_path: File path
    :raises ValueError: Invalid file path
    """
    if not validators.url(file_path) and not os.path.exists(file_path):
        raise ValueError(f"{file_path} is not a valid file path or url.")


def calculate_line_endings(path) -> Dict[Any, Any]:
    # From https://stackoverflow.com/questions/29695861/get-newline-stats-for-a-text-file-in-python
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
