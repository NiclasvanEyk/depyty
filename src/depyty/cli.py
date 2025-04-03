from argparse import ArgumentParser, RawDescriptionHelpFormatter
from dataclasses import dataclass


@dataclass
class Cli:
    pyproject_globs: list[str]
    python_path: str | None


def parse_cli_args() -> Cli:
    parser = ArgumentParser(
        prog="depyty",
        description="Enforce proper dependency declaration in shared Python environments.",
        epilog="""Examples:
Inspect the current project using the current Python interpreter:
    depyty pyproject.toml
       
Inspect a uv workspace where you place all modules under a packages/ directory:
    depyty --python=.venv/bin/python "packages/*/pyproject.toml"
""",
        formatter_class=RawDescriptionHelpFormatter,
    )

    _ = parser.add_argument(
        "pyproject_globs",
        help="one or more glob patterns to your pyproject.toml files. Example: packages/**/pyproject.toml",
        nargs="+",
        default=["pyproject.toml"],
    )
    _ = parser.add_argument(
        "--python",
        help="path to a python interpreter (e.g. .venv/bin/python), that should be inspected instead of using the currently active one. Example: .venv/bin/python for uv-managed virtual environments",
    )

    args = parser.parse_args()

    return Cli(pyproject_globs=args.pyproject_globs, python_path=args.python)
