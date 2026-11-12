from importlib.metadata import version
from typing import Annotated

import typer
from pydantic import ValidationError

from my_lib import MyLibError, greet
from my_lib.cli.settings import load_settings
from my_lib.logs import setup_logging

app = typer.Typer(
    help="Command-line interface for my-lib.", no_args_is_help=True, add_completion=False
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
        raise typer.Exit(2) from error

    log_settings = settings.log.model_copy(update={"level": "DEBUG"}) if verbose else settings.log
    setup_logging(log_settings)


@app.command("greet")
def greet_command(name: str) -> None:
    """Print a greeting for NAME."""
    try:
        message = greet(name)
    except MyLibError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(1) from error
    typer.echo(message)
