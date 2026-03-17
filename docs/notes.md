# Notes

## Build Backend

The project uses `uv_build` with the standard `src/` layout: source lives in `src/lib/`. This is the conventional approach and is configured with:

```toml
[tool.uv.build-backend]
module-name = "lib"
module-root = "src"
```

`module-root = "src"` tells uv_build to look for `./src/lib/__init__.py` as the package root.

## structlog Integration

Logging is built on [structlog](https://www.structlog.org/) bridged through stdlib's `logging` module via `ProcessorFormatter`. This means:

- **First-party loggers** use `structlog.get_logger()` with keyword-argument context binding (`log.info("event", key=value)`).
- **Third-party stdlib loggers** (e.g. `httpx`, `sqlalchemy`) are automatically picked up by the same handler chain.
- **Console output** uses `ConsoleRenderer` (colourised, human-readable) by default, switching to `JSONRenderer` when `LIB_LOG_USE_JSON_FORMATTER=true`.
- **File output** always writes JSON for structured log analysis.
- `structlog.contextvars.bind_contextvars()` lets you attach fields that appear on every subsequent log line within a request or operation.

`setup_logging()` in `utils/log.py` must be called once at startup before any logger is used. Before it is called (e.g. during tests), structlog is configured to output to stderr via `PrintLoggerFactory` so it never pollutes stdout.

## Commitizen & Versioning

[Commitizen](https://commitizen-tools.github.io/commitizen/) reads Conventional Commit messages to determine the next version and generate CHANGELOG entries. Configuration lives in `[tool.commitizen]` in `pyproject.toml`:

```toml
version_provider = "uv"          # reads/writes the version in pyproject.toml
update_changelog_on_bump = true
major_version_zero = true        # 0.x.y — breaking changes don't force 1.0
```

The `commit-msg` pre-commit hook rejects commits that don't follow the format (`feat:`, `fix:`, `chore:`, etc.).

## `find_project_root()` Caching

`find_project_root()` is decorated with `@functools.cache`, so the filesystem walk happens only once per process — subsequent calls return the cached result immediately. This matters because `LogConfig` now uses a `Field(default_factory=...)` that calls `find_project_root()` at instantiation time; without caching, every `LogConfig()` call would trigger a directory walk.

If you need to reset the cache (e.g. in tests that change the working directory), call `find_project_root.cache_clear()`.

## Renaming the Template

To use this as a real project:

1. Rename `src/lib/` to your package name (e.g. `src/mylib/`)
2. Update `name` in `pyproject.toml`
3. Update `module-name` in `[tool.uv.build-backend]` to match the new directory name
4. Update `[tool.coverage.run]` source and `[tool.ruff.lint.isort]` known-local-folder
5. Update env-var prefix (`LIB_LOG_*`) in `LogConfig`
6. Do a global find-and-replace of `lib.` imports to your new package name
