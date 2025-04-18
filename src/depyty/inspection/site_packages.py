import logging
from pathlib import Path

from depyty.inspection.direct_url import direct_url_to_module_list
from depyty.inspection.dist_info import PythonModule, record_file_to_module_list
from depyty.inspection.metadata import metadata_file_to_distribution_name
from depyty.inspection.pth import get_editable_pth_installs


def site_packages_to_module_list(site_packages: Path) -> dict[str, list[PythonModule]]:
    modules_by_distribution_name: dict[str, list[PythonModule]] = {}
    pths = get_editable_pth_installs(site_packages)
    logging.debug(f"Found {len(pths)} editable pth files", extra={"pths": pths})

    for entry in site_packages.glob("*.dist-info"):
        if not entry.is_dir():
            continue

        distribution_name = metadata_file_to_distribution_name(entry / "METADATA")
        if not distribution_name:
            continue

        # If a `direct_url.json` file is present, we may deal with
        # with an editable install.
        # See https://packaging.python.org/en/latest/specifications/direct-url
        # for more information.
        modules = direct_url_to_module_list(entry / "direct_url.json", pths) or []

        # Otherwise the `RECORD` file should have every file / module that was
        # contained in the distribution.
        modules.extend(
            record_file_to_module_list(
                record_file=entry / "RECORD", base_dir=site_packages
            )
            or []
        )

        if modules:
            modules_by_distribution_name[distribution_name] = modules
        else:
            logging.debug(
                f"Could not find any sources for distribution '{distribution_name}'"
            )

    return modules_by_distribution_name
