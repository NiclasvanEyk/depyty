from argparse import ArgumentParser, RawDescriptionHelpFormatter
from dataclasses import dataclass

from depyty.reporting import ReporterName


@dataclass
class CliArgs:
    pyproject_globs: list[str]
    python_path: str | None
    reporter: ReporterName
    verbose: bool


@dataclass
class Cli:
    args: CliArgs
    parser: ArgumentParser


def parse_cli_args() -> Cli:
    parser = ArgumentParser(
        prog="depyty",
        description="Enforce proper dependency declaration in shared Python environments.",
        epilog="""Examples:
Inspect the current project using the current Python interpreter:
    depyty pyproject.toml
       
Inspect a uv workspace where you place all modules under a packages/ directory:
    depyty --python=.venv/bin/python "packages/*"
""",
        formatter_class=RawDescriptionHelpFormatter,
    )

    _ = parser.add_argument(
        "pyproject_globs",
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
    _ = parser.add_argument(
        "--verbose",
        "-v",
        help="get more logging output.",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    return Cli(
        args=CliArgs(
            pyproject_globs=args.pyproject_globs,
            python_path=args.python,
            verbose=args.verbose,
            reporter=ReporterName(args.reporter),
        ),
        parser=parser,
    )
