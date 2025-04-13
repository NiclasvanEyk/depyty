import json

from depyty.introspection.script import Module


def test_modules_are_serializable() -> None:
    original = Module(
        name="example",
        distribution_names={"example"},
        belongs_to_stdlib=False,
        location=None,
    )
    serialized = json.dumps(original.to_json_dict())
    deserialized = Module.from_json_dict(json.loads(serialized))

    assert deserialized == original
