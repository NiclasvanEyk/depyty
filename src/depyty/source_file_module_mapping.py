import logging
import warnings
from dataclasses import dataclass
from pathlib import Path

from depyty.introspection.script import Module
from depyty.source_file_collection import SourceProject


@dataclass(frozen=True, slots=True)
class SourceFileWithContext:
    path: Path
    module: str
    distribution_name: str
    declared_dependencies: set[str]
    stdlib_modules: set[str]


def iter_source_files_with_context(
    source_packages: list[SourceProject], available_modules_by_name: dict[str, Module]
):
    stdlib_modules: set[str] = {
        m.name for m in available_modules_by_name.values() if m.belongs_to_stdlib
    }

    for package in source_packages:
        modules = [
            m
            for m in available_modules_by_name.values()
            if package.distribution_name in m.distribution_names
        ]
        if len(modules) < 1:
            logging.warning(
                f"Package '{package.distribution_name}' not found in environment"
            )
            continue
        if len(modules) > 1:
            logging.warning(
                f"Package '{package.distribution_name}' found in environment multiple times (not supported atm)"
            )
            continue

        module = modules[0]

        location = module.location
        if location is None:
            warnings.warn(
                f"Cannot find source file location for module '{module.name}' belonging to package '{package.distribution_name}'. Skipping..."
            )
            continue

        base = location / module.name
        for source_file in base.rglob("*.py"):
            yield SourceFileWithContext(
                path=base / source_file,
                distribution_name=package.distribution_name,
                declared_dependencies=package.dependencies,
                module=module.name,
                stdlib_modules=stdlib_modules,
            )
