# Logging

- Library code logs through stdlib `logging.getLogger(__name__)` so records follow the application's configuration; the package logger has a `NullHandler`. Do not call `structlog.configure()` or `logging.basicConfig()` from library code.
- Library records pass structured fields as `extra={LOG_FIELDS: {...}}`, not as separate `extra` keys; `setup_logging()` renders only those. Use a constant message and put values in the fields.
- `logs` adds structlog to the core's dependencies and imports library names only from `my_lib`. `my_lib.logs` raises a `ModuleNotFoundError` naming the `logs` extra when structlog is missing.
- `setup_logging()` is an opt-in helper for applications. It configures structlog bridged through stdlib via `ProcessorFormatter`: a stderr handler (`ConsoleRenderer`, or JSON with `format="json"`) and, when `dir` is set, a rotating JSON file handler. Without arguments it uses `LogSettings` defaults and never reads the environment.
- `setup_logging(console=False)` installs a marked `NullHandler` instead of the stderr handler so `logging.lastResort` stays silent. Records logged with `extra=FILE_ONLY` skip the console handler (a filter on it) and still reach the file handler.
- Library modules do not log the errors they raise; the caller decides how to report them.
- Calling `setup_logging()` again replaces only its own handlers; if creating a handler fails, the previous configuration stays. See [the logging section](../../../architecture.md#logging) and the [structlog notes](../../../notes.md#structlog-integration).
- `LogSettings` fields need a `Field(description=...)`; they are exposed as `MY_LIB_LOG__*` through the [CLI settings](cli.md).
