import json
from hashlib import md5
from pathlib import Path
from typing import override

from depyty.reporting.abstract import Reporter
from depyty.source_file_checking import Violation


class GitLabReporter(Reporter):
    def __init__(self, base: Path) -> None:
        self.base: Path = base

    @override
    def report(self, violations: list[Violation]) -> None:
        print("[")

        for violation in violations:
            path = str(violation.location.file.relative_to(self.base))

            fingerprint = md5(usedforsecurity=False)
            fingerprint.update(path.encode("utf-8"))
            fingerprint.update(violation.undeclared_dependency.encode("utf-8"))

            issue = {
                "description": f"Module '{violation.undeclared_dependency}' was not declared explicitly",
                "check_name": "depyty",
                "fingerprint": fingerprint.hexdigest(),
                "severity": "major",
                "location": {
                    "path": path,
                    "lines": {
                        "begin": violation.location.line,
                    },
                },
            }

            print("    " + json.dumps(issue))

        print("]")
