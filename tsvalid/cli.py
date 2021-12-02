"""Command line interface for SSSOM.

Why does this file exist, and why not put this in ``__main__``? You might be tempted to import things from ``__main__``
later, but that will cause problems--the code will get executed twice:

- When you run ``python3 -m sssom`` python will execute``__main__.py`` as a script. That means there won't be any
  ``sssom.__main__`` in ``sys.modules``.
- When you import __main__ it will get executed again (as a module) because
  there's no ``sssom.__main__`` in ``sys.modules``.

.. seealso:: https://click.palletsprojects.com/en/8.0.x/setuptools/
"""

from typing import List

import click

# Click input options common across commands
from tsvalid.io import validate_file

# @click.group()
# @click.option("-v", "--verbose", count=True)
# @click.option("-q", "--quiet")
# def main(verbose: int, quiet: bool):
#     """Run the TSValid CLI."""
#     if verbose >= 2:
#         logging.basicConfig(level=logging.DEBUG)
#     elif verbose == 1:
#         logging.basicConfig(level=logging.INFO)
#     else:
#         logging.basicConfig(level=logging.WARNING)
#     if quiet:
#         logging.basicConfig(level=logging.ERROR)


@click.command()
@click.argument("input", required=True, type=click.Path())
@click.option(
    "--skip",
    multiple=True,
    help="You can skip TSValid checks, by either naming them directly "
    "or defining regular expression patterns to match groups of checks. "
    "For example `--skip E2` skips the E2 check, and `--skip W.*` "
    "skips all checks starting with a W.",
)
@click.option(
    "--encoding",
    default="utf-8",
    help="The encoding defines how the TSV file should be interpreted as a string.",
)
@click.option(
    "--comment",
    help="Many TSV files use comments, typically a hash (#) "
    "to denote that anything following a # symbol should be ignored. "
    "If a comment symbol is supplied, and a row starts with that symbol, "
    "no QC checks are run on that row.",
    type=str,
)
@click.option(
    "--summary",
    default=False,
    is_flag=True,
    help="If true, prints an error summary at the end of validation.",
    show_default=True,
)
def validate(input: str, skip: List[str], summary: bool, comment: str, encoding: str):
    """Validate a tsv file.

    Example:
        tsvalid validate table.tsv
    # noqa: DAR101
    """
    validate_file(
        input_path=input,
        exceptions=skip,
        summary=summary,
        encoding=encoding,
        comment=comment,
    )


if __name__ == "__main__":
    validate()
