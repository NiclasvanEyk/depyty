from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import ClassVar, Self, override

from depyty.cli.framework import Command
from depyty.cli.globals import CliContext


@dataclass(frozen=True, slots=True, kw_only=True)
class EnvCommand(Command):
    name: ClassVar[str] = "env"

    python_path: str | None

    @staticmethod
    @override
    def configure_argument_parser(parser: ArgumentParser):
        _ = parser.add_argument(
            "--python",
            help="path to a python interpreter (e.g. .venv/bin/python), that should be inspected instead of using the currently active one. Example: .venv/bin/python for uv-managed virtual environments",
        )

    @classmethod
    @override
    def from_namespace(cls, namespace: Namespace) -> Self:
        return cls(
            python_path=namespace.python,
        )

    @classmethod
    @override
    def run(cls, args: Self, context: CliContext) -> int | None:
        raise NotImplementedError()
