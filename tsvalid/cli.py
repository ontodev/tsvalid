"""Command line interface for TSValid."""

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
@click.option(
    "--fail",
    default=False,
    is_flag=True,
    help="If true, the validation process will fail with an error.",
    show_default=True,
)
def validate(
    input: str, skip: List[str], summary: bool, comment: str, encoding: str, fail: bool
):
    """Validate a tsv file.

    Example:
        tsvalid validate table.tsv
    # noqa: DAR101
    """
    validate_file(
        input_path=input,
        exceptions=skip,
        summary=summary,
        fail_hard=fail,
        encoding=encoding,
        comment=comment,
    )


if __name__ == "__main__":
    validate()
