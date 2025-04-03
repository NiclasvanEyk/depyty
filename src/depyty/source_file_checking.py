import logging
from ast import Import, ImportFrom, Module, parse, walk
from collections.abc import Iterator
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

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


def _get_module_from_import_path(import_path: str) -> str:
    name = import_path
    if "." in name:
        name = name.split(".")[0]
    return name


@dataclass(frozen=True, slots=True)
class ModuleImport:
    location: Location
    module: str


def _iterate_imports(ast: Module, file: Path):
    for node in walk(ast):
        if isinstance(node, Import):
            for alias in node.names:
                yield ModuleImport(
                    module=_get_module_from_import_path(alias.name),
                    location=Location.from_stmt(node, file),
                )
        if isinstance(node, ImportFrom):
            if node.module is None:
                # this happens for 'from . import xyz', which we don't really care about atm
                continue
            yield ModuleImport(
                module=_get_module_from_import_path(node.module),
                location=Location.from_stmt(node, file),
            )


def _check_source_file(file: SourceFileWithContext) -> list[Violation]:
    violations: list[Violation] = []

    logging.debug(f"Checking {file.path}")
    contents = file.path.read_text()
    ast = parse(contents)

    for imported_module in _iterate_imports(ast, file.path):
        if imported_module.module == file.module:
            continue

        if imported_module.module in file.stdlib_modules:
            continue

        if imported_module.module in file.declared_dependencies:
            continue

        violations.append(
            Violation(
                context=Context(
                    distribution_name=file.distribution_name, module=file.module
                ),
                location=imported_module.location,
                undeclared_dependency=imported_module.module,
            )
        )

    return violations


def check_source_files(
    source_files: Iterator[SourceFileWithContext],
) -> list[Violation]:
    violations: list[Violation] = []
    with ThreadPoolExecutor() as executor:
        violations_by_file = [
            executor.submit(_check_source_file, file) for file in source_files
        ]

        if len(violations_by_file) == 0:
            raise Exception("No files analyzed")

        for future in violations_by_file:
            violations.extend(future.result())

    return violations
