from typing import TypeAlias, cast, get_args

from depyty.cli.commands.analyze import AnalyzeCommand
from depyty.cli.commands.env import EnvCommand

SubCommand: TypeAlias = AnalyzeCommand | EnvCommand  # noqa: UP040


def commands() -> tuple[type[SubCommand]]:
    return cast(tuple[type[SubCommand]], get_args(SubCommand))
