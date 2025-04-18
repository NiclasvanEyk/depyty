"""
Performs introspection into external Python environments, or the current one.

This is mostly intended to gather information, that is easy to extract by
executing functions at runtime, such as getting all stdlib modules, or all
installed distributions.

Compared to the `depyty.inspection` module, this does execute code in the
context of the Python environment.
"""

from depyty.introspection.external import introspect
from depyty.introspection.script import introspect_current_environment

__all__ = [
    "introspect",
    "introspect_current_environment",
]
