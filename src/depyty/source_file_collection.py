from collections.abc import Collection, Iterable
from dataclasses import dataclass
from pathlib import Path

from depyty.dependencies import Dependencies
from depyty.inspection.dist_info import PythonModule
from depyty.pyproject import PyprojectToml


@dataclass
class SourceProject:
    distribution_name: str

    root: Path

    dependencies: Collection[str]

    files: Collection[Path]


def discover_source_packages(
    source_package_project_toml_paths: Iterable[str],
    modules_by_distribution_name: dict[str, list[PythonModule]],
) -> list[SourceProject]:
    source_projects: list[SourceProject] = []
    for pyproject_path in source_package_project_toml_paths:
        pyproject = PyprojectToml.from_file(pyproject_path)
        distribution_name = pyproject.project_name
        dependencies = Dependencies.from_pyproject_toml(pyproject)

        modules = modules_by_distribution_name.get(distribution_name)
        if modules is None:
            raise Exception(f"Could not find source files for '{distribution_name}'")

        source_projects.append(
            SourceProject(
                distribution_name=distribution_name,
                root=Path(pyproject_path).parent,
                dependencies=dependencies.get_all(),
                files=[module.file for module in modules],
            )
        )

    return source_projects
