# CLI

- `cli` adds Pydantic Settings and Typer and imports library names only from `my_lib`. It is the composition root: loads settings, sets up logging, calls the library, maps errors to exit codes.
- To expose library functionality, add a command in `src/my_lib/cli/app.py` that imports it from `my_lib`, and test it in `tests/cli/`. Commands do not catch `MyLibError`.
- `_CommandGroup` (the `cls` of the Typer app) maps errors from commands in one place: a `MyLibError` that is also a `ValueError` exits with `EXIT_USAGE` (2), any other `MyLibError` with `EXIT_FAILURE` (1). It logs the error with `extra=FILE_ONLY` and prints `Error: ...` to stderr once. Other exceptions propagate. Invalid configuration also exits with 2.
- `src/my_lib/cli/settings.py` defines the command's `Settings` (Pydantic `BaseSettings`, prefix `MY_LIB_`, nested delimiter `__`) from library models: `log` is `LogSettings` (`MY_LIB_LOG__*`). Only `load_settings()` reads the environment and `.env`; empty values use defaults.
- Every setting needs a `Field(description=...)` and a line in `.env.example`; tests in `tests/cli/test_settings.py` enforce both. The docs configuration page is generated from `Settings`; see the [docs guide](../../docs.md).
- When changing settings or the command, update `.env.example`, README, and the docs.
- `src/my_lib/main.py` is the `my-lib` console script; it reports a missing `cli` extra. `tests/test_main.py` and `tests/test_package.py` cover the message.
