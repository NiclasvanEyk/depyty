"""
Analysis regarding the current python enviornment.

What packages are installed, from which names, etc.
"""

import importlib.metadata
import json
import os
import sys
import sysconfig
from collections import defaultdict
from dataclasses import dataclass
from importlib.machinery import FileFinder
from pathlib import Path
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
        dist_name = dist.metadata.get("Name", "")
        if not dist_name:
            continue

        # Strategy 1: Check top_level.txt
        try:
            top_level_text = dist.read_text("top_level.txt")
            if top_level_text:
                for line in top_level_text.splitlines():
                    mod = line.strip()
                    if mod:
                        module_map[mod].add(dist_name)
                continue  # Skip further checks if top_level.txt worked
        except Exception:
            pass

        # Strategy 2: Check direct_url.json for editable installs
        try:
            direct_url_text = dist.read_text("direct_url.json")
            if direct_url_text:
                direct_url = json.loads(direct_url_text)
                if "url" in direct_url and direct_url["url"].startswith("file://"):
                    package_path = Path(direct_url["url"][7:])
                    if package_path.exists():
                        for item in package_path.iterdir():
                            if item.is_dir() and (item / "__init__.py").is_file():
                                module_map[item.name].add(dist_name)
                        src_dir = package_path / "src"
                        if src_dir.exists():
                            for item in src_dir.iterdir():
                                if item.is_dir() and (item / "__init__.py").is_file():
                                    module_map[item.name].add(dist_name)
                        continue
        except Exception:
            pass

        # Strategy 3: Fallback to file structure
        try:
            for file in dist.files or []:
                if file.parts:
                    module_map[file.parts[0]].add(dist_name)
        except Exception:
            pass

        # Strategy 4: Handle egg-link files (another editable install indicator)
        try:
            egg_link_path = next(
                (p for p in sys.path if Path(p, f"{dist_name}.egg-link").exists()), None
            )
            if egg_link_path:
                egg_link = (
                    Path(egg_link_path, f"{dist_name}.egg-link").read_text().strip()
                )
                for item in Path(egg_link).iterdir():
                    if item.is_dir():
                        module_map[item.name].add(dist_name)
        except Exception as e:
            print(e)
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

    location: Path | None


def get_available_modules_by_name() -> dict[str, Module]:
    module_to_distribution_map = build_module_to_distribution_map()
    stdlib_modules = _get_stdlib_modules()

    return {
        module.name: Module(
            name=module.name,
            distribution_names=module_to_distribution_map.get(module.name, set()),
            location=Path(module.module_finder.path)
            if isinstance(module.module_finder, FileFinder)
            else None,
            belongs_to_stdlib=module.name in stdlib_modules,
        )
        for module in iter_modules()
    }
