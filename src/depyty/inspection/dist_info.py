from pathlib import Path

from depyty.inspection.modules import filesystem_path_to_module_path


def record_file_to_module_list(record_file: Path) -> list[str] | None:
    if not (record_file.exists() and record_file.is_file()):
        return None

    return _parse_record_file_to_module_list(record_file.read_text())


def _parse_record_file_to_module_list(contents: str) -> list[str]:
    """
    Parses the contents of a RECORD file in *.dist-info/ directories.

    See https://packaging.python.org/en/latest/specifications/recording-installed-packages/#the-record-file
    """
    modules: list[str] = []

    for line in contents.splitlines():
        parts = line.split(",")
        if len(parts) < 1:
            continue

        relative_file_path = parts[0]
        if not relative_file_path.endswith(".py"):
            continue

        modules.append(filesystem_path_to_module_path(relative_file_path))

    return modules
