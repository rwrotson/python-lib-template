import logging
from importlib.metadata import version
from pathlib import Path

import pytest
from rich.text import Text
from typer.testing import CliRunner

import my_lib.cli.app as cli_app
from my_lib import MyLibError
from my_lib.cli.app import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == f"my-lib {version('my-lib')}"


def test_no_command_shows_help() -> None:
    result = runner.invoke(app, [])

    output = Text.from_ansi(result.output).plain
    assert "Usage" in output
    assert "greet" in output
    assert "--verbose" in output


def test_greet_prints_greeting() -> None:
    result = runner.invoke(app, ["greet", "Ada"])

    assert result.exit_code == 0
    assert result.stdout == "Hello, Ada!\n"


def test_value_error_subclass_is_a_usage_error() -> None:
    result = runner.invoke(app, ["greet", " "])

    assert result.exit_code == 2
    assert result.stderr == "Error: name must not be empty\n"


def test_other_library_error_is_a_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(name: str) -> str:
        raise MyLibError("boom")

    monkeypatch.setattr(cli_app, "greet", fail)

    result = runner.invoke(app, ["greet", "Ada"])

    assert result.exit_code == 1
    assert result.stderr == "Error: boom\n"


def test_unexpected_errors_are_not_mapped(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(name: str) -> str:
        raise RuntimeError("bug")

    monkeypatch.setattr(cli_app, "greet", fail)

    result = runner.invoke(app, ["greet", "Ada"])

    assert isinstance(result.exception, RuntimeError)


def test_error_goes_to_log_file_not_console(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("MY_LIB_LOG__DIR", str(tmp_path))

    result = runner.invoke(app, ["greet", " "])

    assert result.output.count("name must not be empty") == 1
    log = (tmp_path / "my-lib.log").read_text()
    assert "name must not be empty" in log


def test_settings_configure_logging(
    monkeypatch: pytest.MonkeyPatch,
    clean_root_logger: logging.Logger,
) -> None:
    monkeypatch.setenv("MY_LIB_LOG__LEVEL", "ERROR")

    runner.invoke(app, ["greet", "Ada"])

    assert clean_root_logger.level == logging.ERROR


def test_verbose_enables_debug_logging(
    monkeypatch: pytest.MonkeyPatch,
    clean_root_logger: logging.Logger,
) -> None:
    monkeypatch.setenv("MY_LIB_LOG__LEVEL", "ERROR")

    runner.invoke(app, ["--verbose", "greet", "Ada"])

    assert clean_root_logger.level == logging.DEBUG


def test_invalid_configuration_is_a_usage_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_LIB_LOG__LEVEL", "LOUD")

    result = runner.invoke(app, ["greet", "Ada"])

    assert result.exit_code == 2
    assert result.stderr.startswith("Invalid configuration:")
