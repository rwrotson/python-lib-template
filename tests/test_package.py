import logging
import subprocess
import sys

import my_lib


def test_package_logger_has_null_handler() -> None:
    handlers = logging.getLogger("my_lib").handlers
    assert any(isinstance(handler, logging.NullHandler) for handler in handlers)


def test_public_api_names_exist() -> None:
    assert all(hasattr(my_lib, name) for name in my_lib.__all__)


def test_import_leaves_global_logging_unconfigured() -> None:
    code = (
        "import logging, structlog, my_lib; "
        "print(len(logging.getLogger().handlers), structlog.is_configured())"
    )

    # Run in a fresh interpreter: this process already configured logging in other tests.
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )

    assert result.stdout.split() == ["0", "False"]


def test_import_does_not_load_optional_dependencies() -> None:
    code = (
        "import sys, my_lib; "
        "print(*(name in sys.modules for name in ('structlog', 'pydantic_settings', 'typer')))"
    )

    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )

    assert result.stdout.split() == ["False", "False", "False"]


def test_logs_package_reports_missing_extra() -> None:
    # A None entry in sys.modules makes the import fail as if the package were not installed.
    code = (
        "import sys; sys.modules['structlog'] = None\n"
        "try:\n    import my_lib.logs\n"
        "except ModuleNotFoundError as error:\n    print(error.name, error)"
    )

    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )

    assert result.stdout.startswith("structlog ")
    assert "my-lib[logs]" in result.stdout
