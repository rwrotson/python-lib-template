# Tests

- `tests/` mirrors the package (`core/`, `logs/`, `cli/`, `test_main.py`); `tests/test_package.py` covers the public API, import-time behaviour, and the missing-extra message.
- Tests run in parallel (pytest-xdist) and in random order (pytest-randomly); warnings are errors and each test has a 30-second timeout. `poe test` enforces 95% branch coverage. Reproduce an order-dependent failure with `uv run pytest -p randomly --randomly-seed=<seed>`.
- Autouse fixtures in `tests/conftest.py` remove `MY_LIB_*` variables, run each test in a temporary working directory (so a local `.env` is not read), and restore logging and structlog configuration.
- pytest adds its own capture handlers to the root logger, so assert on the library's handlers only.
- Test functions and fixtures need type annotations (mypy strict covers `tests/`) but no docstrings.
- Run a focused file or `-k` selection before the full suite.
