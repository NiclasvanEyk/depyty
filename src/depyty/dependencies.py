from dataclasses import dataclass

from packaging.requirements import Requirement

from depyty.pyproject import PyprojectToml


@dataclass
class Dependencies:
    direct: set[str]
    optional: dict[str, set[str]]
    groups: dict[str, set[str]]

    def get_all(self) -> set[str]:
        return self.direct.union(*self.optional.values(), *self.groups.values())

    @staticmethod
    def from_pyproject_toml(pyproject: PyprojectToml):
        return Dependencies(
            direct={
                Requirement(specifier).name for specifier in pyproject.dependencies
            },
            optional={
                name: {Requirement(specifier).name for specifier in requirements}
                for name, requirements in pyproject.optional_dependencies.items()
            },
            groups={
                group_name: {
                    Requirement(specifier).name
                    for specifier in group_requirements
                    if isinstance(specifier, str)
                }
                for group_name, group_requirements in pyproject.dependency_groups.items()
            },
        )
