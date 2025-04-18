from argparse import ArgumentParser, Namespace
from dataclasses import asdict, dataclass
from pprint import pprint
from typing import ClassVar, Self, override

from depyty.cli.context import CliContext
from depyty.cli.framework import Command
from depyty.environment import infer_environment


@dataclass(frozen=True, slots=True, kw_only=True)
class EnvCommand(Command):
    name: ClassVar[str] = "env"

    globs: list[str]

    python_path: str | None

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

    @classmethod
    @override
    def from_namespace(cls, namespace: Namespace) -> Self:
        return cls(
            globs=namespace.globs,
            python_path=namespace.python,
        )

    @classmethod
    @override
    def run(cls, args: Self, context: CliContext) -> int | None:
        environment = infer_environment(
            cwd=context.cwd,
            python_path=args.python_path,
            globs=args.globs,
        )

        pprint(asdict(environment))

        return None
