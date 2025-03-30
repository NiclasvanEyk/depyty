from collections.abc import Iterable
from dataclasses import dataclass

from depyty.dependencies import Dependencies
from depyty.pyproject import PyprojectToml


@dataclass
class SourceProject:
    distribution_name: str

    dependencies: set[str]


def parse_source_packages(
    source_package_project_toml_paths: Iterable[str],
) -> list[SourceProject]:
    source_projects: list[SourceProject] = []
    for pyproject_path in source_package_project_toml_paths:
        pyproject = PyprojectToml.from_file(pyproject_path)
        distribution_name = pyproject.project_name
        dependencies = Dependencies.from_pyproject_toml(pyproject)
        source_projects.append(
            SourceProject(
                distribution_name=distribution_name,
                dependencies=dependencies.get_all(),
            )
        )

    return source_projects
