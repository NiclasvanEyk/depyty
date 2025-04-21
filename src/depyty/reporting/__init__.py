"""
Defines the interfaces and available formats for reporting analysis results.

Each specific report format (e.g. `gitlab`) has its own submodule. This way, we
can easily install and import it only when specifically requested. This in turn
enables us installing these as [extras / `optional-dependencies`](https://packaging.python.org/en/latest/specifications/dependency-specifiers/#extras).
Some users will install `depyty` as a dev-dependency, which e.g. in `uv`
monorepos means, that the dependencies can conflict with other runtime
dependencies to have as little conflicts as possible, we try to require the
smallest possible set of dependencies by default.
"""

from enum import StrEnum
from pathlib import Path

from depyty.reporting.abstract import Reporter
from depyty.reporting.console import ConsoleReporter


class ReporterName(StrEnum):
    CONSOLE = "console"
    JSON = "json"
    GITLAB = "gitlab"


def build_reporter(base: Path, name: ReporterName) -> Reporter:
    if name == ReporterName.GITLAB:
        from depyty.reporting.gitlab import GitLabReporter

        return GitLabReporter(base)

    if name == ReporterName.JSON:
        from depyty.reporting.json import JsonReporter

        return JsonReporter()

    return ConsoleReporter(base)


__all__ = ["Reporter", "ReporterName", "build_reporter"]
