import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from packaging.requirements import Requirement


class InvalidPyProjectToml(Exception): ...


@dataclass
class Dependencies:
    direct: set[str]
    optional: dict[str, set[str]]
    groups: dict[str, set[str]]

    def get_all(self) -> set[str]:
        return self.direct.union(*self.optional.values(), *self.groups.values())

    @staticmethod
    def from_pyproject_toml(pyproject: dict[str, Any], file_path: str):
        project_section = pyproject.get("project", {})
        if not isinstance(project_section, dict):
            raise InvalidPyProjectToml(
                f"'{file_path}' has an invalid 'project' section"
            )

        direct_dependencies: set[str] = {
            Requirement(specifier).name
            for specifier in project_section.get("dependencies", set())
            if isinstance(specifier, str)
        }

        dependency_groups_section = project_section.get("dependency-groups", {})
        if not isinstance(dependency_groups_section, dict):
            raise InvalidPyProjectToml(
                f"Invalid 'dependency-groups' section in '{file_path}'"
            )
        dependency_groups = {
            group_name: {
                Requirement(specifier).name
                for specifier in group_requirements
                if isinstance(specifier, str)
            }
            for group_name, group_requirements in dependency_groups_section.items()
            if isinstance(group_name, str) and isinstance(group_requirements, list)
        }

        optional_dependencies_section = project_section.get("optional-dependencies", {})
        if not isinstance(dependency_groups_section, dict):
            raise InvalidPyProjectToml(
                f"Invalid 'optional-dependencies' section in '{file_path}'"
            )
        optional_dependencies = {
            group_name: {
                Requirement(specifier).name
                for specifier in group_requirements
                if isinstance(specifier, str)
            }
            for group_name, group_requirements in optional_dependencies_section.items()
            if isinstance(group_name, str) and isinstance(group_requirements, list)
        }

        return Dependencies(
            direct=direct_dependencies,
            optional=optional_dependencies,
            groups=dependency_groups,
        )


@dataclass
class SourceProject:
    distribution_name: str

    dependencies: set[str]


def parse_source_packages(
    source_package_project_toml_paths: Iterable[str],
) -> list[SourceProject]:
    source_projects: list[SourceProject] = []
    for pyproject_path in source_package_project_toml_paths:
        with open(pyproject_path, "rb") as pyproject_file:
            pyproject = tomllib.load(pyproject_file)
            project_section = pyproject.get("project", "")
            if not isinstance(project_section, dict):
                raise InvalidPyProjectToml(
                    f"'{pyproject_path}' has an invalid 'project' section"
                )
            distribution_name = project_section.get("name", "")
            if not (isinstance(distribution_name, str) and distribution_name):
                raise InvalidPyProjectToml(
                    f"'{pyproject_path}' has an invalid name '{distribution_name}'"
                )
            dependencies = Dependencies.from_pyproject_toml(pyproject, pyproject_path)
            source_projects.append(
                SourceProject(
                    distribution_name=distribution_name,
                    dependencies=dependencies.get_all(),
                )
            )

    return source_projects
