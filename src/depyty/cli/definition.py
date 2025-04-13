from __future__ import annotations

from argparse import (
    ArgumentParser,
    Namespace,
    RawDescriptionHelpFormatter,
)
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from depyty.cli.commands import SubCommand, commands
from depyty.cli.framework import add_subcommand
from depyty.cli.globals import CliContext


@dataclass(frozen=True, slots=True, kw_only=True)
class Cli[T: SubCommand]:
    args: CliArgs[T]
    parser: ArgumentParser


@dataclass(frozen=True, slots=True, kw_only=True)
class CliArgs[T: SubCommand]:
    context: CliContext
    command: T


def _build_cli_parser() -> ArgumentParser:
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
        "--verbose",
        "-v",
        help="get more logging output.",
        action="store_true",
        default=False,
    )

    subcommands = parser.add_subparsers(title="commands", dest="command", required=True)
    for command in commands():
        add_subcommand(subcommands, command)

    return parser


def _parse_command(args: Namespace) -> SubCommand:
    name = args.command
    if not isinstance(name, str):
        raise ValueError("Please provide a command name")

    for command in commands():
        if command.name == name:
            return command.from_namespace(args)

    raise ValueError(f"Unknown subcommand '{name}'")


def _parse_into_cli_struct(args: Namespace) -> CliArgs[Any]:
    return CliArgs(
        context=CliContext(verbose=args.verbose, cwd=Path.cwd()),
        command=_parse_command(args),
    )


def parse_cli_args() -> Cli[Any]:
    parser = _build_cli_parser()
    args = parser.parse_args()

    return Cli(args=_parse_into_cli_struct(args), parser=parser)
