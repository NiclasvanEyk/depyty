import json
from inspect import getsource
from subprocess import run

from depyty.introspection import script as script_module
from depyty.introspection.script import Module


def get_available_modules_by_name_standalone(
    python_path: str,
) -> dict[str, Module]:
    script = getsource(script_module)
    script += "\n\n"
    script += "import json"
    script += "\n\n"
    script += "print(json.dumps([module.to_json_dict() for module in get_available_modules_by_name().values()]))"

    # This is a _bit_ hacky, since the buffers for stdout could overflow, but
    # let's see how long this works
    process = run(
        [python_path, "-"], input=script.encode(), capture_output=True, check=True
    )

    modules: dict[str, Module] = {}
    for serialized_module in json.loads(process.stdout):
        module = Module.from_json_dict(serialized_module)
        modules[module.name] = module

    return modules
