from logging import DEBUG, INFO
from logging import basicConfig as configure_logging
from sys import stderr


def setup_cli_logging(verbose: bool) -> None:
    configure_logging(
        level=DEBUG if verbose else INFO,
        format="%(levelname)-7s %(message)s",
        stream=stderr,
    )
