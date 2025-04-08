import logging
from glob import glob
from itertools import chain
from pathlib import Path
from sys import executable

from depyty.autoconf import autoconf
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

    setup_cli_logging(cli.args.verbose)
    cwd = Path.cwd()

    inferred_config = autoconf(cwd)
    try:
        # First we inspect the environment, to see what packages are installed.
        python_path = cli.args.python_path
        if not python_path and inferred_config and inferred_config.python:
            python_path = inferred_config.python
            logging.debug(
                f"Using detected Python interpreter from {inferred_config.origin} at {python_path}"
            )
        if python_path:
            available_modules = get_available_modules_by_name_standalone(python_path)
        else:
            logging.debug(f"Using current Python interpreter at {executable}")
            available_modules = get_available_modules_by_name()
        logging.debug(f"Found {len(available_modules)} modules in the environment")

        # Now, we'll check each of the given first-party packages to see what they
        # import, and if their imprts are properly declared.
        raw_globs = cli.args.pyproject_globs
        if not raw_globs and inferred_config and inferred_config.globs:
            raw_globs = inferred_config.globs
            logging.debug(
                f"Using {len(raw_globs)} detected globs from {inferred_config.origin}"
            )
        if not raw_globs:
            cli.parser.print_usage()
            exit(1)
        globs = chain(
            *(
                glob(f"{pyproject_glob}/pyproject.toml")
                if not pyproject_glob.endswith("pyproject.toml")
                else pyproject_glob
                for pyproject_glob in raw_globs
            )
        )
        source_packages = parse_source_packages(globs)
        logging.debug(
            f"Found the following source packages: {', '.join(package.distribution_name for package in source_packages)}"
        )

        source_files = iter_source_files_with_context(
            source_packages, available_modules
        )
        violations = check_source_files(source_files)

        reporter = build_reporter(cwd, cli.args.reporter)
        reporter.report(violations)

        if len(violations) > 0:
            exit(2)
    except Exception as exception:
        if cli.args.verbose:
            raise
        else:
            logging.error(str(exception))
            exit(1)


if __name__ == "__main__":
    main(parse_cli_args())
