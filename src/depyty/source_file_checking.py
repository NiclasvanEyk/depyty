import logging
from ast import Import, ImportFrom, Module, parse, walk
from collections.abc import Iterator
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from depyty.inspection.dist_info import PythonModule
from depyty.source_file_module_mapping import SourceFileWithContext


@dataclass(frozen=True, slots=True)
class Location:
    file: Path
    line: int
    col: int

    def as_location_str(self) -> str:
        return f"{self.file!s}:{self.line}:{self.col}"

    @staticmethod
    def from_stmt(stmt: Import | ImportFrom, file: Path):
        return Location(
            file=file,
            line=stmt.lineno,
            col=stmt.col_offset,
        )


@dataclass(frozen=True, slots=True)
class Context:
    distribution_name: str
    module: str


@dataclass
class Violation:
    context: Context
    location: Location
    undeclared_dependency: str
    installation_suggestion: str | None


@dataclass(frozen=True, slots=True)
class ModuleImport:
    location: Location
    module: str


def _iterate_imports(ast: Module, file: Path):
    # TODO: Skip relative imports
    for node in walk(ast):
        if isinstance(node, Import):
            for alias in node.names:
                yield ModuleImport(
                    module=alias.name,
                    location=Location.from_stmt(node, file),
                )
        if isinstance(node, ImportFrom):
            if node.module is None:
                # this happens for 'from . import xyz', which we don't really care about atm
                continue
            yield ModuleImport(
                module=node.module,
                location=Location.from_stmt(node, file),
            )


def _check_source_file(
    file: SourceFileWithContext,
    modules_by_distribution_name: dict[str, list[PythonModule]],
) -> list[Violation]:
    violations: list[Violation] = []

    logging.debug(f"Checking {file.path}")
    contents = file.path.read_text()
    ast = parse(contents)

    for imported_module in _iterate_imports(ast, file.path):
        if imported_module.module == file.module:
            continue

        if imported_module.module in file.top_level_stdlib_modules:
            continue

        paths = imported_module.module.split(".")
        if len(paths) > 1:
            top_level_module = paths[0]
            if top_level_module in file.top_level_stdlib_modules:
                continue

        if imported_module.module in file.dependency_modules:
            continue

        undeclared_dependency = imported_module.module
        installation_suggestion = None
        for distribution_name, modules in modules_by_distribution_name.items():
            for entry in modules:
                if undeclared_dependency == entry.module:
                    installation_suggestion = distribution_name
                    break

        violations.append(
            Violation(
                context=Context(
                    distribution_name=file.distribution_name, module=file.module
                ),
                location=imported_module.location,
                undeclared_dependency=undeclared_dependency,
                installation_suggestion=installation_suggestion,
            )
        )

    return violations


def check_source_files(
    source_files: Iterator[SourceFileWithContext],
    modules_by_distribution_name: dict[str, list[PythonModule]],
) -> tuple[list[Violation], int]:
    violations: list[Violation] = []
    checked_files = 0
    with ThreadPoolExecutor() as executor:
        violations_by_file = {
            file.path: executor.submit(
                _check_source_file, file, modules_by_distribution_name
            )
            for file in source_files
        }

        for file, future in violations_by_file.items():
            checked_files += 1
            try:
                violations.extend(future.result())
            except Exception as exception:
                logging.exception(f"{file}: {exception}", exc_info=exception)

    return violations, checked_files
