# Tests

- `tests/` mirrors the package (`core/`, `logs/`, `cli/`, `test_main.py`); `tests/test_package.py` covers the public API, import-time behaviour, and the missing-extra message.
- Tests run in parallel (pytest-xdist) and in random order (pytest-randomly); warnings are errors and each test has a 30-second timeout. `poe test` enforces 95% branch coverage. Reproduce an order-dependent failure with `uv run pytest -p randomly --randomly-seed=<seed>`.
- Autouse fixtures in `tests/conftest.py` remove `MY_LIB_*` variables, run each test in a temporary working directory (so a local `.env` is not read), and restore logging and structlog configuration.
- pytest adds its own capture handlers to the root logger, so assert on the library's handlers only.
- Test functions and fixtures need type annotations (mypy strict covers `tests/`) but no docstrings.
- Run a focused file or `-k` selection before the full suite.
- Tests never use the network: pytest-socket disables sockets (Unix sockets stay allowed for xdist). Only `tests/integration/` may use it, with `@pytest.mark.enable_socket`.
- `tests/integration/` is collected only with `--live` (`tests/conftest.py`), so `poe test` and `poe check` skip it. Run it with `uv run poe test-live` (serial, fixed order, reads an optional `.env`).
- Typer renders help and errors with Rich ANSI styling; compare `Text.from_ansi(result.output).plain` (from `rich.text`) instead of raw output when asserting option names or rendered messages.
