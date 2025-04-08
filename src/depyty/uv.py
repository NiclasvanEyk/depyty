import fnmatch
from typing import Any, cast

from depyty.pyproject import InvalidPyProjectToml


def get_uv_workspace_member_globs(pyproject: dict[str, Any]) -> None | list[str]:
    """
    Note: The exclude portion is already applied.
    """
    tools_section = pyproject.get("tool")
    if tools_section is None:
        return None
    if not isinstance(tools_section, dict):
        raise InvalidPyProjectToml("pyproject tool section needs to be a dict")

    uv_section = tools_section.get("uv")
    if uv_section is None:
        return None
    if not isinstance(uv_section, dict):
        raise InvalidPyProjectToml("pyproject tool.uv section needs to be a dict")

    workspace_section = uv_section.get("workspace")
    if workspace_section is None:
        return None
    if not isinstance(workspace_section, dict):
        raise InvalidPyProjectToml(
            "pyproject tool.uv.workspace section needs to be a dict"
        )

    members = workspace_section.get("members")
    if members is None:
        return None
    if not isinstance(members, list):
        raise InvalidPyProjectToml(
            "pyproject tool.uv.workspace.members section needs to be a dict"
        )
    for member in members:
        if not isinstance(member, str):
            raise InvalidPyProjectToml()

    members = cast(list[str], members)

    exclude = pyproject.get("exclude")
    if exclude is not None:
        if not isinstance(exclude, list):
            raise InvalidPyProjectToml()
        for exclude_glob in exclude:
            if not isinstance(exclude_glob, str):
                raise InvalidPyProjectToml()
            members = fnmatch.filter(members, exclude_glob)

    return members
