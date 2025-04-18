import logging

from depyty.cli.commands import SubCommand
from depyty.cli.definition import Cli, parse_cli_args
from depyty.cli.framework import PrintUsage
from depyty.logging import setup_cli_logging


def main(cli: Cli[SubCommand] | None = None):
    """
    The main entrypoint. This is what gets run when you execute `depyty`.
    """
    if cli is None:
        cli = parse_cli_args()

    setup_cli_logging(cli.args.context.verbose)

    try:
        exit_code = cli.args.command.run(
            cli.args.command,  # type: ignore
            cli.args.context,
        )

        if isinstance(exit_code, int):
            exit(exit_code)
    except PrintUsage:
        cli.parser.print_usage()
        exit(1)

    except Exception as exception:
        if cli.args.context.verbose:
            raise
        else:
            logging.error(str(exception))
            exit(1)


if __name__ == "__main__":
    main(parse_cli_args())
