"""
Some global configuration options passed to the `run` method of each subcommand
as the second parameter.

This can not be located in `depyty.cli.framework`, since it would create cyclic
dependencies.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True, kw_only=True)
class CliContext:
    cwd: Path
    verbose: bool
