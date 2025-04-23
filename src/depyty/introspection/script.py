"""
Analysis regarding the current python enviornment.

What packages are installed, from which names, etc.

NOTE: This file may not depend upon anything that is not available in the stdlib!
      It is executed in the context of unknown Python environments, to check what
      packages/modules are available in them.
"""

import json
import sys
from importlib import metadata
from typing import TypedDict


class IntrospectionResult(TypedDict):
    top_level_stdlib_module_names: list[str]
    distribution_names: list[str]
    path: list[str]


def introspect_current_environment() -> IntrospectionResult:
    # This is only available since Python 3.10!
    top_level_stdlib_module_names = list(sys.stdlib_module_names)

    # This acts as a safety mechanism. We should definitely find information
    # for all of them somewhere later.
    distribution_names = list(
        {dist.metadata["Name"] for dist in metadata.distributions()}
    )

    return IntrospectionResult(
        top_level_stdlib_module_names=top_level_stdlib_module_names,
        distribution_names=distribution_names,
        path=sys.path,
    )


def print_serialized_introspection_result(file=None) -> None:
    """This is what used when introspecting another env"""
    print(json.dumps(introspect_current_environment()), file=file)
