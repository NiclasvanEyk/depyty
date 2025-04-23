from depyty.cli.commands import get_command_classes
from src.depyty.cli.definition import _build_cli_parser


def test_commands_have_unique_names() -> None:
    names: set[str] = set()
    for command in get_command_classes():
        assert command.name not in names
        names.add(command.name)


def test_cli_can_be_built() -> None:
    args = _build_cli_parser()
    assert args is not None
