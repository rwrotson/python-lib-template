import logging
from importlib.metadata import version
from typing import Annotated, Any

import typer
from pydantic import ValidationError
from typer.core import TyperGroup

from my_lib import MyLibError, greet
from my_lib.cli.settings import load_settings
from my_lib.logs import FILE_ONLY, setup_logging

EXIT_FAILURE = 1
EXIT_USAGE = 2

_logger = logging.getLogger(__name__)


class _CommandGroup(TyperGroup):
    """Typer group that maps MyLibError raised by commands to exit codes."""

    def invoke(self, ctx: Any) -> object:  # noqa: ANN401 - Typer's vendored click Context is private
        """Run the command; log and print expected errors, then exit with their code."""
        try:
            return super().invoke(ctx)
        except MyLibError as error:
            _logger.error("Command failed: %s", error, exc_info=error, extra=FILE_ONLY)
            typer.echo(f"Error: {error}", err=True)
            code = EXIT_USAGE if isinstance(error, ValueError) else EXIT_FAILURE
            raise typer.Exit(code) from error


app = typer.Typer(
    cls=_CommandGroup,
    help="Command-line interface for my-lib.",
    no_args_is_help=True,
    add_completion=False,
)


def _show_version(value: bool) -> None:
    if value:
        typer.echo(f"my-lib {version('my-lib')}")
        raise typer.Exit


@app.callback()
def root(
    verbose: Annotated[bool, typer.Option("--verbose", "-V", help="Log debug messages.")] = False,
    _version: Annotated[
        bool,
        typer.Option(
            "--version", callback=_show_version, is_eager=True, help="Show the version and exit."
        ),
    ] = False,
) -> None:
    """Load MY_LIB_* settings and configure logging for one invocation."""
    try:
        settings = load_settings()
    except ValidationError as error:
        typer.echo(f"Invalid configuration: {error}", err=True)
        raise typer.Exit(EXIT_USAGE) from error

    log_settings = settings.log.model_copy(update={"level": "DEBUG"}) if verbose else settings.log
    setup_logging(log_settings)


@app.command("greet")
def greet_command(name: str) -> None:
    """Print a greeting for NAME."""
    typer.echo(greet(name))
