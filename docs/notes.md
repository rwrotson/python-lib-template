# Notes

## Build Backend

`uv_build` loads the `my_lib` package from `src/`:

```toml
[tool.uv.build-backend]
module-name = "my_lib"
module-root = "src"
```

The wheel includes `py.typed`, so type checkers use the package's inline annotations.

## structlog Integration

`my_lib.utils.log.setup_logging()` connects [structlog](https://www.structlog.org/) to stdlib logging through `ProcessorFormatter`:

- Library modules use stdlib loggers; their records and structlog events share the same handlers.
- Console logs use colourised `ConsoleRenderer` output or JSON when `MY_LIB_LOG__FORMAT=json`.
- File logs use JSON and are written only when `MY_LIB_LOG__DIR` is set.
- Timestamps are ISO 8601 in UTC.
- `structlog.contextvars.bind_contextvars()` adds fields to subsequent logs in the current context.

The library never calls `setup_logging()` itself. An application that already configures logging or structlog should skip it.

## Commitizen & Versioning

[Commitizen](https://commitizen-tools.github.io/commitizen/) reads Conventional Commit messages to select the next version and update `CHANGELOG.md`. Its settings are in `pyproject.toml`:

```toml
version_provider = "uv"
update_changelog_on_bump = true
major_version_zero = true
```

The `commit-msg` hook checks Conventional Commit format.

## Publishing

The release workflow publishes version tags to PyPI with [Trusted Publishing](https://docs.pypi.org/trusted-publishers/). On PyPI, add a trusted publisher with the repository owner and name, workflow `release.yml`, and environment `pypi`; for a project that does not exist on PyPI yet, add it as a pending publisher. Create the `pypi` environment in the GitHub repository settings, optionally with required reviewers.

## Renaming the Template

Choose three names before editing: a distribution name (for example, `my-package`), an import
package (`my_package`), and an environment prefix (`MY_PACKAGE_`). Check that the distribution
name is free on PyPI.

1. Rename `src/my_lib/` to `src/my_package/`. Replace `my_lib` in imports throughout `src/`,
   `tests/`, and `docs/`, including logger names in tests. Update `module-name` under
   `[tool.uv.build-backend]`, `[tool.coverage.run].source`,
   `[tool.ruff.lint.isort].known-first-party`, and `[tool.importlinter]` in `pyproject.toml`.
2. Set `[project].name`, the description, authors, keywords, and `[project.urls]` in
   `pyproject.toml`. Rename `MyLibError` if the name should match the package.
3. Change `env_prefix` and the `env_fields()` default prefix in
   `src/my_package/config/settings.py`, and `PREFIX` in `docs/gen_config_page.py`. Adjust the
   default log file name in `LogSettings`. Update `.env.example`, README examples, and tests
   using `MY_LIB_` variables.
4. Update `mkdocs.yml` (`site_name`, repository links, and the source watch path) and
   `docs/gen_ref_pages.py`, which scans the import package for API pages. Update names and
   links in README, docs, `AGENTS.md`, and the PyPI URL in `.github/workflows/release.yml`.
5. Configure the PyPI trusted publisher and GitHub Pages as described above.
6. Regenerate the lockfile with `uv lock`, then run `uv sync --all-groups --locked`,
   `uv run poe check`, `uv build`, and `uv run --group docs mkdocs build --strict`.
