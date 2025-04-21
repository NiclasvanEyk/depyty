import json
from typing import override

from depyty.reporting.abstract import Reporter
from depyty.source_file_checking import Violation


class JsonReporter(Reporter):
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
            )
        )
