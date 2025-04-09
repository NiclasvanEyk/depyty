from pathlib import Path


def site_packages_to_module_list(site_packages: Path) -> dict[str, list[str]]:
    modules_by_distribution_name: dict[str, list[str]] = {}

    for entry in site_packages.glob("*.dist-info"):
        if not entry.is_dir():
            continue

        metadata_file = entry / "METADATA"
        if not (metadata_file.exists() and metadata_file.is_file()):
            continue

        distribution_name = parse_name_from_metadata_file(metadata_file.read_text())
        if not distribution_name:
            continue

        record_file = entry / "RECORD"
        if not (record_file.exists() and record_file.is_file()):
            continue

        modules = parse_record_file(record_file.read_text())
        if not modules:
            continue

        modules_by_distribution_name[distribution_name] = modules

    return modules_by_distribution_name


def parse_name_from_metadata_file(contents: str) -> str | None:
    for line in contents.splitlines():
        if line.startswith("Name: "):
            return line.removeprefix("Name: ")


def parse_record_file(contents: str) -> list[str]:
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
        if relative_file_path.endswith("/__init__.py"):
            module = relative_file_path.removesuffix("/__init__.py").replace("/", ".")
            modules.append(module)
        elif relative_file_path.endswith(".py"):
            module = relative_file_path.removesuffix(".py").replace("/", ".")
            modules.append(module)

    return modules
