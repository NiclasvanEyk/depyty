import logging
from glob import glob
from itertools import chain
from os import getcwd
from pathlib import Path
from sys import executable

from depyty.cli import Cli, parse_cli_args
from depyty.environment import get_available_modules_by_name
from depyty.environment_standalone import get_available_modules_by_name_standalone
from depyty.logging import setup_cli_logging
from depyty.reporting import build_reporter
from depyty.source_file_checking import check_source_files
from depyty.source_file_collection import parse_source_packages
from depyty.source_file_module_mapping import iter_source_files_with_context


def main(cli: Cli | None = None):
    if cli is None:
        cli = parse_cli_args()

    setup_cli_logging(cli.verbose)

    try:
        # First we inspect the environment, to see what packages are installed.
        if cli.python_path is None:
            logging.debug(f"Using Python interpreter at {executable}")
            available_modules = get_available_modules_by_name()
        else:
            logging.debug(f"Using Python interpreter at {cli.python_path}")
            available_modules = get_available_modules_by_name_standalone(
                cli.python_path
            )
        logging.debug(f"Found {len(available_modules)} modules in the environment")

        # Now, we'll check each of the given first-party packages to see what they
        # import, and if their imprts are properly declared.
        globs = chain(*(glob(pyproject_glob) for pyproject_glob in cli.pyproject_globs))
        source_packages = parse_source_packages(globs)
        logging.debug(
            f"Found the following source packages: {', '.join(package.distribution_name for package in source_packages)}"
        )

        source_files = iter_source_files_with_context(
            source_packages, available_modules
        )
        violations = check_source_files(source_files)

        reporter = build_reporter(Path(getcwd()), cli.reporter)
        reporter.report(violations)

        if len(violations) > 0:
            exit(2)
    except Exception as exception:
        if cli.verbose:
            raise
        else:
            logging.error(str(exception))
            exit(1)


if __name__ == "__main__":
    main(parse_cli_args())
