"""Command line interface for SSSOM.

Why does this file exist, and why not put this in ``__main__``? You might be tempted to import things from ``__main__``
later, but that will cause problems--the code will get executed twice:

- When you run ``python3 -m sssom`` python will execute``__main__.py`` as a script. That means there won't be any
  ``sssom.__main__`` in ``sys.modules``.
- When you import __main__ it will get executed again (as a module) because
  there's no ``sssom.__main__`` in ``sys.modules``.

.. seealso:: https://click.palletsprojects.com/en/8.0.x/setuptools/
"""

import logging
import sys
from typing import List, TextIO

import click

# Click input options common across commands
from tsvalid.io import validate_file

input_argument = click.argument("input", required=True, type=click.Path())

output_option = click.option(
    "-o",
    "--output",
    help="Output tsv file.",
    type=click.File(mode="w"),
    default=sys.stdout,
)


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
def main(verbose: int, quiet: bool):
    """Run the TSValid CLI."""
    if verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    if quiet:
        logging.basicConfig(level=logging.ERROR)


@main.command()
@input_argument
@click.option("--exception", "-E", multiple=True)
def validate(input: str, exception: List[str]):
    """Validate a tsv file.

    .. warning:: currently only supports conversion to RDF)

    Example:
        tsvalid validate table.tsv
    """  # noqa: DAR101
    validate_file(input_path=input, exceptions=exception)


if __name__ == "__main__":
    main()
