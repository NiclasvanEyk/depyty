"""
Analysis regarding the current python enviornment.

What packages are installed, from which names, etc.
"""

import importlib.metadata
import os
import sys
import sysconfig
from collections import defaultdict
from dataclasses import dataclass
from pkgutil import iter_modules


def _get_stdlib_modules() -> set[str]:
    stdlib_path = sysconfig.get_paths()["stdlib"]
    stdlib_modules = set(sys.builtin_module_names)  # start with built-ins

    for root, _, files in os.walk(stdlib_path):
        for filename in files:
            if filename.endswith((".py", ".pyc", ".so", ".pyd")):
                rel_path = os.path.relpath(os.path.join(root, filename), stdlib_path)
                parts = rel_path.split(os.sep)

                # Only consider top-level modules/packages
                if parts:
                    module = parts[0]
                    if module.endswith((".py", ".so", ".pyd", ".pyc")):
                        module = os.path.splitext(module)[0]
                    stdlib_modules.add(module)

    return stdlib_modules


def build_module_to_distribution_map() -> dict[str, set[str]]:
    module_map: defaultdict[str, set[str]] = defaultdict(set)

    for dist in importlib.metadata.distributions():
        dist_name = dist.metadata["Name"]

        # FIXME: this needs to be refactored and understood

        # Strategy 1: Check top_level.txt
        try:
            top_level_text = dist.read_text("top_level.txt")
            if top_level_text:
                for line in top_level_text.splitlines():
                    mod = line.strip()
                    if mod:
                        module_map[mod].add(dist_name)
                continue  # don't bother with files if top_level worked
        except Exception:
            pass

        # Strategy 2: Fallback to file structure
        try:
            for file in dist.files or []:
                if file.parts:
                    module_map[file.parts[0]].add(dist_name)
        except Exception:
            pass

    return dict(module_map)


@dataclass(frozen=True, slots=True)
class Module:
    name: str
    """The name of the module you'd `import` in a Python script"""

    distribution_names: set[str]
    """
    The name used to install this, e.g. 'pillow' instead of 'PIL'.

    Can be multiple in case of a namespace package.
    """

    belongs_to_stdlib: bool


def get_available_modules_by_name() -> dict[str, Module]:
    module_to_distribution_map = build_module_to_distribution_map()
    stdlib_modules = _get_stdlib_modules()

    # FIXME: this needs support for path installations

    return {
        module.name: Module(
            name=module.name,
            distribution_names=module_to_distribution_map.get(module.name, set()),
            belongs_to_stdlib=module.name in stdlib_modules,
        )
        for module in iter_modules()
    }
