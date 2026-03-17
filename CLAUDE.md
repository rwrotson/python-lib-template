# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All tasks run via [taskipy](https://github.com/taskipy/taskipy):

```bash
uv run task lint        # ruff check .
uv run task fmt         # ruff format .
uv run task typecheck   # mypy src/
uv run task test        # pytest (parallel, 80% coverage enforced)
uv run task test-fast   # pytest --no-cov -n auto
uv run task audit       # pip-audit dependency audit
```

Run a single test file:

```bash
uv run pytest tests/path/to/test.py
```

Serve the docs locally:

```bash
uv run --group docs mkdocs serve
```

## Architecture

```
src/lib/               # library package — rename to your package name
    utils/
        log.py         # structlog setup bridged through stdlib; LIB_LOG_* env vars
        misc.py        # find_project_root() utility
    pkg/               # placeholder for your domain modules
tests/
    utils/
        test_log.py
        test_misc.py
```

- **Logging** (`utils/log.py`): `LogConfig` reads settings from `LIB_LOG_*` environment variables (Pydantic Settings). Call `setup_logging()` once at startup. Structlog is wired through stdlib so third-party loggers share the same handler chain.
- **`find_project_root()`** (`utils/misc.py`): walks up from the module's directory until it finds a directory containing `pyproject.toml` (or a custom marker).
- **Tests**: pytest with 80% coverage enforcement, parallelised via pytest-xdist (`-n auto`).
- **Env config**: prefix `LIB_LOG_*`; reads `.env` file automatically.

## Renaming the Template

To rename `lib` to your package name:

1. Rename `src/lib/` to `src/yourpackage/`
2. Update `name` and `[tool.uv.build-backend] module-name` in `pyproject.toml`
3. Update `[tool.coverage.run] source` and `[tool.ruff.lint.isort] known-local-folder`
4. Update `env_prefix` in `LogConfig` (e.g. `YOURPACKAGE_LOG_`)
5. Global find-and-replace `lib.` imports → `yourpackage.`
