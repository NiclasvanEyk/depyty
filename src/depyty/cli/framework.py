"""
The mini-framework we use to build our CLI.
"""

from __future__ import annotations

from abc import abstractmethod
from argparse import (
    ArgumentParser,
    Namespace,
    _SubParsersAction,
)
from dataclasses import dataclass
from typing import ClassVar, Protocol, Self

from depyty.cli.globals import CliContext


class Command(Protocol):
    name: ClassVar[str]

    @staticmethod
    @abstractmethod
    def configure_argument_parser(parser: ArgumentParser):
        pass

    @classmethod
    @abstractmethod
    def from_namespace(cls, namespace: Namespace) -> Self:
        pass

    @classmethod
    @abstractmethod
    def run(cls, args: Self, context: CliContext) -> int | None:
        pass


@dataclass(frozen=True, slots=True, kw_only=True)
class CommandDocs:
    help: str | None
    description: str | None

    @staticmethod
    def empty() -> CommandDocs:
        return CommandDocs(help=None, description=None)


def get_command_docs(cls: type[Command]) -> CommandDocs:
    doc_comment = cls.__doc__
    if doc_comment is None:
        return CommandDocs.empty()

    doc_lines = doc_comment.splitlines()
    if len(doc_lines) <= 0:
        return CommandDocs.empty()

    return CommandDocs(
        help=doc_lines[0],
        description="\n".join(doc_lines[:1]) if len(doc_lines) > 1 else None,
    )


def add_subcommand(
    parent: _SubParsersAction[ArgumentParser],
    command: type[Command],
) -> None:
    docs = get_command_docs(command)

    parser = parent.add_parser(
        command.name,
        help=docs.help,
        description=docs.description,
    )
    command.configure_argument_parser(parser)
