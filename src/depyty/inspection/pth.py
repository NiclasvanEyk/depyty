from pathlib import Path


def get_editable_pth_installs(site_packages: Path) -> list[Path]:
    """
    In a virtual environments site-packages, one can find `_MODULENAME.pth` files.
    At least from what I've observed, they contain paths to modules, that were
    installed with `--editable` (took a look at `pip` and `uv` on MacOS).

    These can than be matched with the `*.dist-info/direct_url.json` file, to
    get a list of source files from an editable package.
    """
    pths: list[Path] = []
    for pth_file in site_packages.glob("*.pth"):
        for line in pth_file.read_text().splitlines():
            # Sometimes these can contain dynamic imports, which we'll skip for
            # now to start with a simple implementation.
            if line.startswith("import "):
                continue

            target_pth = Path(line.strip())
            if not target_pth.exists():
                raise ValueError(
                    f"Path '{target_pth}' referenced by '{pth_file}' does not exist"
                )
            pths.append(target_pth)
    return pths
