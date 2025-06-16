import json
from inspect import getsource
from subprocess import run

from depyty.introspection import script as script_module
from depyty.normalization import normalize_distribution_name


def introspect(python_path: str) -> script_module.IntrospectionResult:
    script = getsource(script_module)
    script += "\n\n"
    script += "print_serialized_introspection_result()"

    # This is a _bit_ hacky, since the buffers for stdout could overflow, but
    # let's see how long this works
    process = run(
        [python_path, "-"], input=script.encode(), capture_output=True, check=True
    )

    parsed_stdout = json.loads(process.stdout)

    if not isinstance(parsed_stdout, dict):
        raise ValueError("Expected introspection to yield a dict")

    top_level_stdlib_module_names = parsed_stdout.get("top_level_stdlib_module_names")
    if not isinstance(top_level_stdlib_module_names, list):
        raise ValueError(
            "Expected introspection to yield a dict where 'top_level_stdlib_module_names' is a list"
        )

    distribution_names = parsed_stdout.get("distribution_names")
    if not isinstance(distribution_names, list):
        raise ValueError(
            "Expected introspection to yield a dict where 'distribution_names' is a list"
        )

    path = parsed_stdout.get("path")
    if not isinstance(path, list):
        raise ValueError(
            "Expected introspection to yield a dict where 'path' is a list"
        )

    return script_module.IntrospectionResult(
        top_level_stdlib_module_names=top_level_stdlib_module_names,
        distribution_names=[
            normalize_distribution_name(name) for name in distribution_names
        ],
        path=path,
    )
