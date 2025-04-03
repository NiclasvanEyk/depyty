from enum import StrEnum
from pathlib import Path

from depyty.reporting.abstract import Reporter
from depyty.reporting.console import ConsoleReporter


class ReporterName(StrEnum):
    CONSOLE = "console"
    GITLAB = "gitlab"


def build_reporter(base: Path, name: ReporterName) -> Reporter:
    if name == ReporterName.GITLAB:
        from depyty.reporting.gitlab import GitLabReporter

        return GitLabReporter(base)

    return ConsoleReporter(base)


__all__ = ["Reporter", "ReporterName", "build_reporter"]
