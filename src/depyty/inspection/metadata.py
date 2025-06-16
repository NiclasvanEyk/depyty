from pathlib import Path

from depyty.normalization import normalize_distribution_name


def metadata_file_to_distribution_name(metadata_file: Path) -> str | None:
    if not (metadata_file.exists() and metadata_file.is_file()):
        return None

    raw_name = _parse_name_from_metadata_file(metadata_file.read_text())
    if raw_name is None:
        return None

    return normalize_distribution_name(raw_name)


def _parse_name_from_metadata_file(contents: str) -> str | None:
    for line in contents.splitlines():
        if line.startswith("Name: "):
            return line.removeprefix("Name: ")
    return None
