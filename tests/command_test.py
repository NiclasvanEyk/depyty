from depyty.cli.commands import get_command_classes


def test_commands_have_unique_names() -> None:
    names: set[str] = set()
    for command in get_command_classes():
        assert command.name not in names
        names.add(command.name)
