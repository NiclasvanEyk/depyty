"""
Small wrapper around the `dict` returned from parsing a `pyproject.toml` file.
"""

import tomllib
from functools import cached_property
from typing import Any


class InvalidPyProjectToml(Exception):
    """
    Raised when the pyproject.toml file is invalid.

    E.g. when the "project" key is not a table/map/dict, but a list of strings.
    """


class PyprojectToml:
    def __init__(self, path: str, values: dict[str, Any]) -> None:
        self.path: str = path
        self.values: dict[str, Any] = values

    @staticmethod
    def from_file(path: str) -> "PyprojectToml":
        with open(path, "rb") as pyproject_file:
            return PyprojectToml(path, tomllib.load(pyproject_file))

    @cached_property
    def project(self) -> dict[str, Any]:
        project_section = self.values.get("project", "")
        if not isinstance(project_section, dict):
            raise InvalidPyProjectToml(
                f"'{self.path}' has an invalid 'project' section"
            )
        return project_section

    @cached_property
    def project_name(self) -> str:
        name = self.project.get("name", "")
        if not (isinstance(name, str) and name):
            raise InvalidPyProjectToml(f"'{self.path}' has an invalid name '{name}'")
        return name

    @cached_property
    def dependencies(self) -> list[str]:
        return [
            specifier
            for specifier in self.project.get("dependencies", [])
            if isinstance(specifier, str)
        ]

    @cached_property
    def dependency_groups(self) -> dict[str, list[Any]]:
        section = self.values.get("dependency-groups", {})
        if not isinstance(section, dict):
            raise InvalidPyProjectToml(
                f"Invalid 'dependency-groups' section in '{self.path}'"
            )

        return {
            group_name: group_requirements
            for group_name, group_requirements in section.items()
            if isinstance(group_name, str) and isinstance(group_requirements, list)
        }

    @cached_property
    def optional_dependencies(self) -> dict[str, list[str]]:
        section = self.values.get("dependency-groups", {})
        if not isinstance(section, dict):
            raise InvalidPyProjectToml(
                f"Invalid 'dependency-groups' section in '{self.path}'"
            )

        return {
            group_name: [
                specifier
                for specifier in group_requirements
                if isinstance(specifier, str)
            ]
            for group_name, group_requirements in section.items()
            if isinstance(group_name, str) and isinstance(group_requirements, list)
        }
