import logging
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Self, override

from depyty.cli.context import CliContext
from depyty.cli.framework import Command
from depyty.environment import infer_environment
from depyty.reporting import ReporterName, build_reporter
from depyty.source_file_checking import check_source_files
from depyty.source_file_module_mapping import iter_source_files_with_context

if TYPE_CHECKING:
    from _typeshed import SupportsWrite


@dataclass(frozen=True, slots=True, kw_only=True)
class AnalyzeCommand(Command):
    """Analyzes the current or given python environment, and reports undeclared imports in the given source files."""

    name: ClassVar[str] = "analyze"

    globs: list[str]
    python_path: str | None
    reporter: ReporterName

    stdout: "SupportsWrite[str] | None" = field(default_factory=lambda: None)

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
        environment = infer_environment(
            cwd=context.cwd,
            python_path=args.python_path,
            globs=args.globs,
        )

        source_files = iter_source_files_with_context(
            environment.source_projects,
            environment.top_level_stdlib_module_names,
            environment.modules_by_distribution_name,
        )

        # Then we combine what we know about the environment, and check the
        # imports statements of each source file of each package, and see if
        # the project only imports, what it has *explicitly* declared.
        violations, checked_files = check_source_files(
            source_files,
            environment.modules_by_distribution_name,
        )
        if checked_files < 1:
            logging.error("No files analyzed")
            return 2

        reporter = build_reporter(context.cwd, args.reporter, args.stdout)
        reporter.report(violations)

        if len(violations) > 0:
            return 2

        BOLD_GREEN = "\033[1;92m"
        RESET = "\033[0m"
        print(
            f"{BOLD_GREEN}Success: no issues found in {checked_files} source files{RESET}",
            file=args.stdout,
        )
        return None
