from typing import TypeAlias, cast, get_args

from depyty.cli.commands.analyze import AnalyzeCommand
from depyty.cli.commands.env import EnvCommand

SubCommand: TypeAlias = AnalyzeCommand | EnvCommand  # noqa: UP040
"""
A union type alias that references all existing subcommands commands.

If a command is added here, it will be automatically available in the CLI.
"""


def get_command_classes() -> tuple[type[SubCommand]]:
    """
    Returns the class `type` objects contained in the `SubCommand` union.

    This way they are actually usable.
    """
    return cast(tuple[type[SubCommand]], get_args(SubCommand))


__all__ = ["SubCommand", "get_command_classes"]
