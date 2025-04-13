import logging
from pathlib import Path

from depyty.inspection.direct_url import direct_url_to_module_list
from depyty.inspection.dist_info import record_file_to_module_list
from depyty.inspection.metadata import metadata_file_to_distribution_name
from depyty.inspection.pth import get_editable_pth_installs


def site_packages_to_module_list(site_packages: Path) -> dict[str, list[str]]:
    modules_by_distribution_name: dict[str, list[str]] = {}
    pths = get_editable_pth_installs(site_packages)
    logging.debug(f"Found {len(pths)} editable pth files", extra={"pths": pths})

    for entry in site_packages.glob("*.dist-info"):
        if not entry.is_dir():
            continue

        distribution_name = metadata_file_to_distribution_name(entry / "METADATA")
        if not distribution_name:
            continue

        modules = record_file_to_module_list(entry / "RECORD") or []
        modules.extend(direct_url_to_module_list(entry / "direct_url.json", pths))
        if not modules:
            continue

        modules_by_distribution_name[distribution_name] = modules

    return modules_by_distribution_name
