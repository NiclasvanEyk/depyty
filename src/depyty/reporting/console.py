from collections import defaultdict
from pathlib import Path
from typing import override

from depyty.reporting.abstract import Reporter
from depyty.source_file_checking import Location, Violation


class ConsoleReporter(Reporter):
    def __init__(self, base: Path) -> None:
        self.base: Path = base

    @override
    def report(self, violations: list[Violation]) -> None:
        grouped: defaultdict[str, defaultdict[str, list[Violation]]] = defaultdict(
            lambda: defaultdict(list)
        )

        for violation in violations:
            grouped[violation.context.distribution_name][
                violation.undeclared_dependency
            ].append(violation)

        for distribution_name in sorted(grouped.keys()):
            v = grouped[distribution_name]
            print(f"{bold(distribution_name)} is missing")
            for undeclared_dependency in sorted(v.keys()):
                print(f"\t{bold(undeclared_dependency)} which is imported in")
                for occurrence in v[undeclared_dependency]:
                    relative_location = Location(
                        file=occurrence.location.file.relative_to(self.base),
                        line=occurrence.location.line,
                        col=occurrence.location.col,
                    )
                    print(f"\t\t{relative_location.as_location_str()}")
                s = occurrence.installation_suggestion
                if s:
                    print(
                        f"\t\tHINT: This can be fixed by explicitly declaring {bold(s)} as a dependency"
                    )


def bold(text: str) -> str:
    bold_prefix = "\033[1m"
    reset = "\033[0m"
    return f"{bold_prefix}{text}{reset}"
