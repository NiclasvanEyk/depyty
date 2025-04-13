from pathlib import Path


def metadata_file_to_distribution_name(metadata_file: Path) -> str | None:
    if not (metadata_file.exists() and metadata_file.is_file()):
        return None

    return _parse_name_from_metadata_file(metadata_file.read_text())


def _parse_name_from_metadata_file(contents: str) -> str | None:
    for line in contents.splitlines():
        if line.startswith("Name: "):
            return line.removeprefix("Name: ")
    return None
