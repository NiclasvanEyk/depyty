from dataclasses import dataclass
from pathlib import Path

from depyty.inspection.modules import filesystem_path_to_module_path


@dataclass(frozen=True, slots=True)
class PythonModule:
    module: str
    file: Path


def record_file_to_module_list(
    record_file: Path, base_dir: Path
) -> list[PythonModule] | None:
    """
    Parses the contents of a RECORD file in *.dist-info/ directories.

    See https://packaging.python.org/en/latest/specifications/recording-installed-packages/#the-record-file
    """
    if not (record_file.exists() and record_file.is_file()):
        return None

    contents = record_file.read_text()

    modules: list[PythonModule] = []
    for line in contents.splitlines():
        parts = line.split(",")
        if len(parts) < 1:
            continue

        relative_file_path = parts[0]
        if not relative_file_path.endswith(".py"):
            continue

        file_path = base_dir / relative_file_path
        if not file_path.is_file():
            raise Exception(
                f"{record_file} listed {file_path}, but is does not exist or is not a file!"
            )

        module = PythonModule(
            module=filesystem_path_to_module_path(relative_file_path),
            file=file_path,
        )
        modules.append(module)

    return modules
