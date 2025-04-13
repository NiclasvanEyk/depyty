import logging
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from glob import glob
from itertools import chain
from sys import executable
from typing import ClassVar, Self, override

from depyty.autoconf import autoconf
from depyty.cli.errors import PrintUsage
from depyty.cli.framework import Command
from depyty.cli.globals import CliContext
from depyty.introspection import (
    get_available_modules_by_name,
    get_available_modules_by_name_standalone,
)
from depyty.reporting import ReporterName, build_reporter
from depyty.source_file_checking import check_source_files
from depyty.source_file_collection import parse_source_packages
from depyty.source_file_module_mapping import iter_source_files_with_context


@dataclass(frozen=True, slots=True, kw_only=True)
class AnalyzeCommand(Command):
    """Analyzes the current or given python environment, and reports undeclared imports in the given source files."""

    name: ClassVar[str] = "analyze"

    globs: list[str]
    python_path: str | None
    reporter: ReporterName

    @staticmethod
    @override
    def configure_argument_parser(parser: ArgumentParser):
        _ = parser.add_argument(
            "globs",
            help="one or more glob patterns to your folders containing pyproject.toml files. Example: packages/**",
            nargs="*",
        )
        _ = parser.add_argument(
            "--python",
            help="path to a python interpreter (e.g. .venv/bin/python), that should be inspected instead of using the currently active one. Example: .venv/bin/python for uv-managed virtual environments",
        )
        _ = parser.add_argument(
            "--reporter",
            help=f"how the results should be reported. Possible values: {list(ReporterName)}",
            default=ReporterName.CONSOLE.value,
        )

    @classmethod
    @override
    def from_namespace(cls, namespace: Namespace) -> Self:
        return cls(
            globs=namespace.globs,
            python_path=namespace.python,
            reporter=ReporterName(namespace.reporter),
        )

    @classmethod
    @override
    def run(cls, args: Self, context: CliContext) -> int | None:
        inferred_config = autoconf(context.cwd)

        # First we inspect the environment, to see what packages are installed.
        python_path = args.python_path
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
        raw_globs = args.globs
        if not raw_globs and inferred_config and inferred_config.globs:
            raw_globs = inferred_config.globs
            logging.debug(
                f"Using {len(raw_globs)} detected globs from {inferred_config.origin}"
            )
        if not raw_globs:
            raise PrintUsage()
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

        reporter = build_reporter(context.cwd, args.reporter)
        reporter.report(violations)

        if len(violations) > 0:
            return 2
        return None
