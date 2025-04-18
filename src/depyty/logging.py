"""
Handles logging and the global `--verbose` flag.

Basically, if you don't want to display something by default, but have it
available when using the `--verbose` flag, use `logging.debug`. Otherwise
the log levels are shown by default and get prepended to each log message
on stderr.
"""

from logging import DEBUG, INFO
from logging import basicConfig as configure_logging
from sys import stderr


def setup_cli_logging(verbose: bool) -> None:
    configure_logging(
        level=DEBUG if verbose else INFO,
        format="%(levelname)-7s %(message)s",
        stream=stderr,
    )
