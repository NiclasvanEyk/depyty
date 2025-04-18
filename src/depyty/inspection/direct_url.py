import json
from pathlib import Path

from depyty.inspection.dist_info import PythonModule
from depyty.inspection.modules import filesystem_path_to_module_path


def direct_url_to_module_list(
    direct_url_file: Path, pths: list[Path]
) -> list[PythonModule] | None:
    if not (direct_url_file.exists() and direct_url_file.is_file()):
        return None

    metadata = json.loads(direct_url_file.read_text())
    if not isinstance(metadata, dict):
        raise Exception(
            f"Expected contents of {direct_url_file} to be a dict, got {metadata}"
        )

    direct_url = metadata.get("url")
    if not isinstance(direct_url, str):
        raise Exception(
            f"Expected 'url' field in {direct_url_file} to be a string, got {direct_url}"
        )

    if not direct_url.startswith("file://"):
        raise Exception("depyty currently only supports file://-based direct urls")

    modules: list[PythonModule] = []
    distribution_directory = Path(direct_url.removeprefix("file://"))
    for pth in pths:
        if pth.is_relative_to(distribution_directory):
            for source_file in pth.rglob("*.py"):
                relative_path = source_file.relative_to(pth)
                modules.append(
                    PythonModule(
                        module=filesystem_path_to_module_path(relative_path),
                        file=source_file,
                    )
                )

    return modules
