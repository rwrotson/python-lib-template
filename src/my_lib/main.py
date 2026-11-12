import sys


def main() -> None:
    """Run the command-line interface."""
    try:
        # The console script exists in base installs, so import the optional CLI here.
        from my_lib.cli.app import app  # noqa: PLC0415
    except ModuleNotFoundError as error:
        if error.name not in {"typer", "pydantic_settings", "structlog"}:
            raise
        sys.stderr.write("CLI dependencies are missing. Install 'my-lib[cli]'.\n")
        raise SystemExit(1) from error
    app()
