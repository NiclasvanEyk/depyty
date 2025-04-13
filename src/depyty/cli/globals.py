from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True, kw_only=True)
class CliContext:
    cwd: Path
    verbose: bool
