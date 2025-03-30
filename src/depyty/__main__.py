import sys
from glob import glob
from itertools import chain
from os import getcwd
from pathlib import Path

from depyty.environment import get_available_modules_by_name
from depyty.reporting.console import ConsoleReporter
from depyty.source_file_checking import check_source_files
from depyty.source_file_collection import parse_source_packages
from depyty.source_file_module_mapping import iter_source_files_with_context


def print_usage():
    print("""Usage:

    depyty "packages/*/pyproject.toml" "lambdas/*/pyproject.toml"

or wherever else you store your deployment artifacts in your monorepo.
""")


def main():
    # First we inspect the environment, to see what packages are installed.
    available_modules = get_available_modules_by_name()

    if (
        len(sys.argv) <= 1
        or "help" in sys.argv
        or "--help" in sys.argv
        or "-h" in sys.argv
    ):
        print_usage()
        exit(1)

    # Now, we'll check each of the given first-party packages to see what they
    # import, and if their imprts are properly declared.
    globs = chain(*(glob(pyproject_glob) for pyproject_glob in sys.argv[1:]))
    source_packages = parse_source_packages(globs)
    source_files = iter_source_files_with_context(source_packages, available_modules)
    violations = check_source_files(source_files)

    ConsoleReporter(Path(getcwd())).report(violations)

    if len(violations) > 0:
        exit(2)


if __name__ == "__main__":
    main()
