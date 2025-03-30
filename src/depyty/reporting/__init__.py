from abc import ABC, abstractmethod

from depyty.source_file_checking import Violation


class Reporter(ABC):
    @abstractmethod
    def report(self, violations: list[Violation]) -> None:
        pass
