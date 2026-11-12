import logging
from importlib.metadata import version

import pytest
from typer.testing import CliRunner

from my_lib.cli.app import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == f"my-lib {version('my-lib')}"


def test_no_command_shows_help() -> None:
    result = runner.invoke(app, [])

    assert "Usage" in result.output
    assert "greet" in result.output


def test_greet_prints_greeting() -> None:
    result = runner.invoke(app, ["greet", "Ada"])

    assert result.exit_code == 0
    assert result.stdout == "Hello, Ada!\n"


def test_greet_reports_library_errors() -> None:
    result = runner.invoke(app, ["greet", " "])

    assert result.exit_code == 1
    assert result.stderr == "Error: name must not be empty\n"


def test_settings_configure_logging(
    monkeypatch: pytest.MonkeyPatch, clean_root_logger: logging.Logger
) -> None:
    monkeypatch.setenv("MY_LIB_LOG__LEVEL", "ERROR")

    runner.invoke(app, ["greet", "Ada"])

    assert clean_root_logger.level == logging.ERROR


def test_verbose_enables_debug_logging(
    monkeypatch: pytest.MonkeyPatch, clean_root_logger: logging.Logger
) -> None:
    monkeypatch.setenv("MY_LIB_LOG__LEVEL", "ERROR")

    runner.invoke(app, ["--verbose", "greet", "Ada"])

    assert clean_root_logger.level == logging.DEBUG


def test_invalid_configuration_is_a_usage_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_LIB_LOG__LEVEL", "LOUD")

    result = runner.invoke(app, ["greet", "Ada"])

    assert result.exit_code == 2
    assert result.stderr.startswith("Invalid configuration:")
