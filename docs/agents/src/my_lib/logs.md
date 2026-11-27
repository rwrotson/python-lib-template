# Logging

- Library code logs through stdlib `logging.getLogger(__name__)` so records follow the application's configuration; the package logger has a `NullHandler`. Do not call `structlog.configure()` or `logging.basicConfig()` from library code.
- `logs` adds structlog to the core's dependencies and imports library names only from `my_lib`. `my_lib.logs` raises a `ModuleNotFoundError` naming the `logs` extra when structlog is missing.
- `setup_logging()` is an opt-in helper for applications. It configures structlog bridged through stdlib via `ProcessorFormatter`: a stderr handler (`ConsoleRenderer`, or JSON with `format="json"`) and, when `dir` is set, a rotating JSON file handler. Without arguments it uses `LogSettings` defaults and never reads the environment.
- Calling `setup_logging()` again replaces only its own handlers; if creating a handler fails, the previous configuration stays. See [the logging section](../../../architecture.md#logging) and the [structlog notes](../../../notes.md#structlog-integration).
- `LogSettings` fields need a `Field(description=...)`; they are exposed as `MY_LIB_LOG__*` through the [CLI settings](cli.md).
