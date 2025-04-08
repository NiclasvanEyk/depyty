import logging
import tomllib
from dataclasses import dataclass
from pathlib import Path

from depyty.uv import get_uv_workspace_member_globs


@dataclass
class InferredConfiguration:
    globs: list[str]
    python: str | None
    origin: str


def autoconf(path: Path) -> InferredConfiguration | None:
    _from_uv = None
    try:
        _from_uv = _uv(path)
    except Exception as e:
        logging.exception("Failed to automatically infer config for uv", exc_info=e)
    if _from_uv is not None:
        return _from_uv

    return None


def _uv(path: Path) -> InferredConfiguration | None:
    pyproject_path = path / "pyproject.toml"
    if not pyproject_path.exists():
        return None

    pyproject = tomllib.loads(pyproject_path.read_text())
    member_globs = get_uv_workspace_member_globs(pyproject)
    default_venv_path = path / ".venv/bin/python"

    return InferredConfiguration(
        globs=member_globs or [],
        python=str(default_venv_path) if default_venv_path.exists() else None,
        origin="uv",
    )
