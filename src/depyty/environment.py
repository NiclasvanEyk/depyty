import logging
from collections.abc import Collection
from dataclasses import dataclass
from glob import glob
from itertools import chain
from pathlib import Path
from sys import executable

from depyty.autoconf import InferredConfiguration, autoconf
from depyty.cli.framework import PrintUsage
from depyty.inspection.dist_info import PythonModule
from depyty.inspection.site_packages import site_packages_to_module_list
from depyty.introspection import (
    introspect,
    introspect_current_environment,
)
from depyty.introspection.script import IntrospectionResult
from depyty.source_file_collection import SourceProject, discover_source_packages


@dataclass
class Environment:
    source_projects: list[SourceProject]
    modules_by_distribution_name: dict[str, list[PythonModule]]
    top_level_stdlib_module_names: Collection[str]


def infer_environment(
    cwd: Path,
    python_path: str | None,
    globs: Collection[str] | None,
) -> Environment:
    inferred_config = autoconf(cwd)

    # First we inspect the environment, to see what packages are installed.
    introspection_result = _introspect_interpreter(python_path, inferred_config)

    modules_by_distribution_name: dict[str, list[PythonModule]] = {}
    for raw_directory in introspection_result["path"]:
        directory = Path(raw_directory)
        if not directory.is_dir():
            logging.debug(
                f"Skipping path entry '{directory}', since it is not a directory..."
            )
            continue

        module_list = site_packages_to_module_list(directory)
        logging.debug(
            f"Found {len(module_list)} distribution packages in {raw_directory}"
        )
        for distribution_name, files in module_list.items():
            modules_by_distribution_name[distribution_name] = files

    # Then we build up a list of projects to check, containing a list of
    # dependencies that were explicitly declared by each project, and a
    # list of its Python source files.
    source_projects = _get_project_sources(
        globs, inferred_config, modules_by_distribution_name
    )

    return Environment(
        source_projects=source_projects,
        modules_by_distribution_name=modules_by_distribution_name,
        top_level_stdlib_module_names=introspection_result[
            "top_level_stdlib_module_names"
        ],
    )


def _introspect_interpreter(
    python_path: str | None, inferred_config: InferredConfiguration | None
) -> IntrospectionResult:
    if not python_path and inferred_config and inferred_config.python:
        python_path = inferred_config.python
        logging.debug(
            f"Using detected Python interpreter from {inferred_config.origin} at {python_path}"
        )

    if python_path:
        return introspect(python_path)

    logging.debug(f"Using current Python interpreter at {executable}")
    result = introspect_current_environment()

    logging.debug(
        f"Found {len(result['distribution_names'])} distribution packages and {len(result['top_level_stdlib_module_names'])} top-lebel standard library modules in the environment"
    )
    return result


def _get_project_sources(
    raw_globs: Collection[str] | None,
    inferred_config: InferredConfiguration | None,
    modules_by_distribution_name: dict[str, list[PythonModule]],
) -> list[SourceProject]:
    if not raw_globs and inferred_config and inferred_config.globs:
        raw_globs = inferred_config.globs
        logging.debug(
            f"Using {len(raw_globs)} detected globs from {inferred_config.origin}"
        )

    if not raw_globs:
        raise PrintUsage()

    globs = chain(
        *(
            glob(f"{pyproject_glob}/pyproject.toml")
            if not pyproject_glob.endswith("pyproject.toml")
            else pyproject_glob
            for pyproject_glob in raw_globs
        )
    )

    source_packages = discover_source_packages(globs, modules_by_distribution_name)
    logging.debug(
        f"Found the following source packages: {', '.join(package.distribution_name for package in source_packages)}"
    )
    return source_packages
