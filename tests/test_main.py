import builtins
from collections.abc import Mapping, Sequence
from types import ModuleType

import pytest

import my_lib.cli.app as cli_app
from my_lib.main import main


def test_main_runs_the_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_app() -> None:
        raise SystemExit(7)

    monkeypatch.setattr(cli_app, "app", fake_app)

    with pytest.raises(SystemExit) as error:
        main()

    assert error.value.code == 7


def _fail_cli_import(monkeypatch: pytest.MonkeyPatch, missing: str) -> None:
    original_import = builtins.__import__

    def fake_import(
        name: str,
        globals: Mapping[str, object] | None = None,  # noqa: A002 - Match __import__.
        locals: Mapping[str, object] | None = None,  # noqa: A002 - Match __import__.
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> ModuleType:
        if name == "my_lib.cli.app":
            raise ModuleNotFoundError(f"No module named {missing!r}", name=missing)
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)


@pytest.mark.parametrize("missing", ["typer", "pydantic_settings", "structlog"])
def test_main_reports_missing_cli_extra(
    missing: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _fail_cli_import(monkeypatch, missing)

    with pytest.raises(SystemExit) as error:
        main()

    assert error.value.code == 1
    assert "my-lib[cli]" in capsys.readouterr().err


def test_main_reraises_unrelated_import_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    _fail_cli_import(monkeypatch, "unrelated")

    with pytest.raises(ModuleNotFoundError, match="unrelated"):
        main()
