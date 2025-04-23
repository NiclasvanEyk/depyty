import json
from io import StringIO

from depyty.introspection.script import (
    introspect_current_environment,
    print_serialized_introspection_result,
)


def test_it_can_find_pytest_in_current_environment() -> None:
    result = introspect_current_environment()
    assert "pytest" in result["distribution_names"]


def test_it_prints_pytest_when_introspecting_current_environment() -> None:
    with StringIO() as buffer:
        print_serialized_introspection_result(buffer)
        result = json.loads(buffer.getvalue())
        assert "pytest" in result["distribution_names"]
