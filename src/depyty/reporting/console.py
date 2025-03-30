from itertools import groupby
from typing import override

from depyty.reporting import Reporter
from depyty.source_file_checking import Violation


class ConsoleReporter(Reporter):
    @override
    def report(self, violations: list[Violation]) -> None:
        for distribution_name, grouped_violations in groupby(
            violations, key=lambda v: v.context.distribution_name
        ):
            print(distribution_name)

            for undeclared_dependency, occurrences in groupby(
                grouped_violations, key=lambda v: v.undeclared_dependency
            ):
                print(f"\t{undeclared_dependency}")
                for occurrence in occurrences:
                    print(f"\t\t{occurrence.location.as_location_str()}")
