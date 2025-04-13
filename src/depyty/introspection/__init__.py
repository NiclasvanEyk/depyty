"""
Performs introspection into external Python environments, or the current one.

This is mostly intended to gather information, that is easy to extract by
executing functions at runtime, such as getting all stdlib modules, or all
installed distributions.

Compared to the `depyty.inspection` module, this does execute code in the
context of the Python environment.
"""

from depyty.introspection.external import get_available_modules_by_name_standalone
from depyty.introspection.script import get_available_modules_by_name

__all__ = [
    "get_available_modules_by_name",
    "get_available_modules_by_name_standalone",
]
