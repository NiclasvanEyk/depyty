import logging
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path

from depyty.inspection.dist_info import PythonModule
from depyty.source_file_collection import SourceProject


@dataclass(frozen=True, slots=True)
class SourceFileWithContext:
    path: Path
    module: str
    distribution_name: str
    declared_dependencies: Collection[str]
    top_level_stdlib_modules: Collection[str]
    dependency_modules: Collection[str]


def iter_source_files_with_context(
    source_project: list[SourceProject],
    stdlib_modules: Collection[str],
    modules_by_distribution_name: dict[str, list[PythonModule]],
):
    for project in source_project:
        modules = modules_by_distribution_name.get(project.distribution_name, [])
        if len(modules) < 1:
            logging.warning(
                f"Package '{project.distribution_name}' not found in environment"
            )
            continue

        # A module has access to all modules in its distribution package...
        dependency_modules = {module.module for module in modules}

        # ... as well as all dependencies the project declares.
        for dependency in project.dependencies:
            dependency_modules.update(
                {
                    module.module
                    for module in modules_by_distribution_name.get(dependency, [])
                }
            )

        for module in modules:
            yield SourceFileWithContext(
                path=module.file,
                distribution_name=project.distribution_name,
                declared_dependencies=project.dependencies,
                module=module.module,
                top_level_stdlib_modules=stdlib_modules,
                dependency_modules=dependency_modules,
            )
