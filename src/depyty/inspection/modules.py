from pathlib import Path


def filesystem_path_to_module_path(fs_path: str | Path) -> str:
    fs_path = str(fs_path)
    if fs_path.endswith("/__init__.py"):
        return fs_path.removesuffix("/__init__.py").replace("/", ".")
    return fs_path.removesuffix(".py").replace("/", ".")
