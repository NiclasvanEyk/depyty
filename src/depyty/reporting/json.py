import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, override

from depyty.reporting.abstract import Reporter
from depyty.source_file_checking import Violation

if TYPE_CHECKING:
    from _typeshed import SupportsWrite


@dataclass
class JsonReporter(Reporter):
    stdout: "SupportsWrite | None" = field(default_factory=lambda: None)

    @override
    def report(self, violations: list[Violation]) -> None:
        print(
            json.dumps(
                [
                    {
                        "context": {
                            "distribution_name": violation.context.distribution_name,
                            "module": violation.context.module,
                        },
                        "location": {
                            "file": str(violation.location.file),
                            "line": violation.location.line,
                            "col": violation.location.col,
                        },
                        "undeclared_dependency": violation.undeclared_dependency,
                        "installation_suggestion": violation.installation_suggestion,
                    }
                    for violation in violations
                ],
                indent=4,
            ),
            file=self.stdout,
        )
