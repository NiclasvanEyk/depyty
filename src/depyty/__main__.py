from glob import glob
from itertools import chain
from os import getcwd
from pathlib import Path

from depyty.cli import Cli, parse_cli_args
from depyty.environment import get_available_modules_by_name
from depyty.environment_standalone import get_available_modules_by_name_standalone
from depyty.reporting.console import ConsoleReporter
from depyty.source_file_checking import check_source_files
from depyty.source_file_collection import parse_source_packages
from depyty.source_file_module_mapping import iter_source_files_with_context


def main(cli: Cli | None = None):
    if cli is None:
        cli = parse_cli_args()

    # First we inspect the environment, to see what packages are installed.
    available_modules = (
        get_available_modules_by_name()
        if cli.python_path is None
        else get_available_modules_by_name_standalone(cli.python_path)
    )

    # Now, we'll check each of the given first-party packages to see what they
    # import, and if their imprts are properly declared.
    globs = chain(*(glob(pyproject_glob) for pyproject_glob in cli.pyproject_globs))
    source_packages = parse_source_packages(globs)
    source_files = iter_source_files_with_context(source_packages, available_modules)
    violations = check_source_files(source_files)

    ConsoleReporter(Path(getcwd())).report(violations)

    if len(violations) > 0:
        exit(2)


if __name__ == "__main__":
    main(parse_cli_args())
