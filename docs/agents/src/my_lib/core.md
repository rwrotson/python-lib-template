# Core

- The core uses only Pydantic among third-party packages and imports no other layer. See [the layers](../../../architecture.md#layers).
- Expected failures raise a `MyLibError` subclass. Subclass a built-in exception as well when callers would reasonably catch it (`InvalidInputError` is also a `ValueError`). Add the new error to [the error table](../../../architecture.md#errors).
- To add functionality: put it in `src/my_lib/core/`, export it from `core/__init__.py` and `my_lib/__init__.py` (`__all__`), test it in `tests/core/`, and list it in `docs/reference/index.md`. To expose it on the command line, see the [CLI guide](cli.md). `core/example.py` shows the pattern; see [adding functionality](../../../architecture.md#adding-functionality).
- Settings-like models used as default argument values are frozen and registered in `[tool.ruff.lint.flake8-bugbear] extend-immutable-calls` in `pyproject.toml`.
- Log through stdlib `logging.getLogger(__name__)`; see the [logging guide](logs.md).
