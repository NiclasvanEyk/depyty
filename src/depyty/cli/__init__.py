"""
Defines most of what is strictly CLI related.

This encompasses
- A small wrapper around `argparse` to build the CLI
- A struct representing the CLI arguments entered by users
- All subcommands and their logic in the `commands` module

If you e.g. want to look what the `check` command does, go to
`depyty.cli.commands.check` and inspect the `run` method. This gets called
when a user runs `depyty check`.
"""
