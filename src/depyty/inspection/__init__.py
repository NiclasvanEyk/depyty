"""
Analyzes the installed distributions based on the contents of a virtual
environment on disk.

Compared to the `depyty.introspection` module, this does not require runtime code
execution.
"""

from depyty.inspection.site_packages import site_packages_to_module_list

__all__ = ["site_packages_to_module_list"]
