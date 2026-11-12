# Architecture

The core does the library's work and knows nothing about settings, logging setup, or the command line. Each outer layer adds one application concern on top of the layers below it, and its third-party packages come from an optional extra, so a library consumer installs only Pydantic.

## Layers

Layers are listed from top to bottom. A layer may import any layer below it and never one above it.

| Layer | Location | Responsibility | Third-party packages | Install |
| --- | --- | --- | --- | --- |
| Entry point | `my_lib/main.py` | `my-lib` console script; reports a missing `cli` extra | — | base |
| CLI | `my_lib/cli/` | Composition root: loads `MY_LIB_*` settings, sets up logging, calls the library, maps errors to exit codes | Pydantic Settings, Typer | `my-lib[cli]` |
| Logging setup | `my_lib/logs/` | `LogSettings` and the opt-in `setup_logging()` for applications | structlog | `my-lib[logs]` |
| Core | `my_lib/core/` | Library functionality and the `MyLibError` hierarchy | Pydantic | base |

`my_lib/__init__.py` re-exports the core's supported names with `__all__` and attaches a `NullHandler` to the `my_lib` logger. `my_lib.logs` raises a `ModuleNotFoundError` that names the `logs` extra when structlog is missing.

### Rules

- `main`, `cli`, and `logs` import library names only from `my_lib`, never from `my_lib.core` modules.
- A module or package whose name starts with `_` is imported only by modules in the same package and its subpackages.
- The library never reads the environment or `.env`. Only the CLI does, in `my_lib.cli.settings`; another application composes its own settings from `LogSettings` and passes values to the library.
- Library code receives settings as arguments, such as `setup_logging(LogSettings(...))`.
- A new third-party dependency belongs to the lowest layer that needs it, and to that layer's extra.

import-linter checks the layers, access to the core through `my_lib`, and the third-party packages of each layer with `uv run poe lint-imports`; the contracts are in `pyproject.toml`. Rules that the contracts do not cover are checked in review.

## Public API

Everything listed in `my_lib.__all__` is public and follows semantic versioning. Other modules can be imported but are not covered by compatibility guarantees, except `my_lib.logs`, which applications use for setup. The `my-lib` command and its `MY_LIB_*` variables are a separate interface for end users. A removal or incompatible change to the public API is a breaking change (`feat!:` or a `BREAKING CHANGE:` footer).

## Import-time behaviour

`import my_lib` does not read the environment or `.env`, configure logging or structlog, add handlers outside the `my_lib` logger, import optional dependencies, or perform I/O. `tests/test_package.py` checks this in a fresh interpreter.

## Logging

Library modules log through `logging.getLogger(__name__)`. The `NullHandler` on `my_lib` keeps records silent until the application configures logging, and records then follow the application's levels and handlers.

`my_lib.logs.setup_logging()` is a helper for applications that do not have their own setup:

1. Without arguments it uses the `LogSettings` defaults; it never reads the environment.
2. It creates all handlers first; if one fails, the previous configuration stays in place.
3. It replaces the handlers it created before and keeps all others.
4. It adds a stderr handler (console or JSON) and, when a log directory is set, a rotating JSON file handler.
5. It configures structlog to render through the same stdlib handlers, so structlog and stdlib records share one format.

The `my-lib` command calls it with `LogSettings` loaded from `MY_LIB_LOG__*`.

## Errors

| Error | Base classes | Raised when |
| --- | --- | --- |
| `MyLibError` | `Exception` | Base for every expected library failure |
| `InvalidInputError` | `MyLibError`, `ValueError` | The input cannot be processed |

Callers can catch `MyLibError` for all library failures or the built-in base for a specific one. Add a subclass for each new kind of expected failure. Unexpected exceptions are not wrapped.

## Adding functionality

- Put the code in `core/` and raise a `MyLibError` subclass for expected failures.
- Accept settings or values as arguments; do not read the environment from the core.
- Export public names from `core/__init__.py` and `my_lib/__init__.py`, and add them to `__all__`.
- Test the behaviour in `tests/core/`.
- To expose it on the command line, add a command in `cli/app.py` that imports it from `my_lib`.

`core/example.py` shows this pattern.
