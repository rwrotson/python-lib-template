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

`my_lib.logs.setup_logging()` (the `logs` extra) connects [structlog](https://www.structlog.org/) to stdlib logging through `ProcessorFormatter`:

- Library modules use stdlib loggers; their records and structlog events share the same handlers.
- Console logs use colourised `ConsoleRenderer` output or JSON with `LogSettings(format="json")` (`MY_LIB_LOG__FORMAT=json` for the command).
- File logs use JSON and are written only when `LogSettings.dir` (`MY_LIB_LOG__DIR`) is set.
- Timestamps are ISO 8601 in UTC.
- `structlog.contextvars.bind_contextvars()` adds fields to subsequent logs in the current context.

The library never calls `setup_logging()` itself. An application that already configures logging or structlog should skip it.

## Documentation Toolchain

The site is built with [ProperDocs](https://properdocs.org/), a maintained continuation of MkDocs 1.x that reads the same configuration (`properdocs.yml`) and runs MkDocs themes and plugins unchanged. MkDocs 2.0 drops the plugin and theme system, and Material for MkDocs requires `mkdocs<2`, so the `mkdocs` package stays on 1.x as a library dependency of the plugins. Running `properdocs` instead of `mkdocs` also avoids the MkDocs 2.0 warnings printed by Material and the plugins.

[Zensical](https://zensical.org/), the successor to Material for MkDocs, does not support `mkdocs-gen-files` yet; the API reference and configuration pages depend on it.

## Commitizen & Versioning

[Commitizen](https://commitizen-tools.github.io/commitizen/) reads Conventional Commit messages to select the next version and update `CHANGELOG.md`. Its settings are in `pyproject.toml`:

```toml
version_provider = "uv"
update_changelog_on_bump = true
major_version_zero = true
```

The `commit-msg` hook checks Conventional Commit format.

## Publishing

The release workflow publishes version tags to PyPI with [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) only when the repository variable `PUBLISH_TO_PYPI` is `true` (Settings → Secrets and variables → Actions → Variables). Without it, a release builds the package and deploys documentation; install a tagged version from GitHub instead. To publish, on PyPI add a trusted publisher with the repository owner and name, workflow `release.yml`, and environment `pypi`; for a project that does not exist on PyPI yet, add it as a pending publisher. Create the `pypi` environment in the GitHub repository settings, optionally with required reviewers.

The template repository does not set the variable, so its release tags deploy documentation only.

## Renaming the Template

Choose three names before editing: a distribution name (for example, `my-package`), an import
package (`my_package`), and an environment prefix (`MY_PACKAGE_`). Check that the distribution
name is free on PyPI.

1. Rename `src/my_lib/` to `src/my_package/`. Replace every `my_lib` throughout `src/`,
   `tests/`, and `docs/`: imports, logger names in tests, and paths and text in
   `docs/gen_ref_pages.py` and `docs/gen_config_page.py`. Update `module-name` under
   `[tool.uv.build-backend]`, `[tool.coverage.run].source`,
   `[tool.ruff.lint.isort].known-first-party`, and `[tool.importlinter]` in `pyproject.toml`.
2. Set `[project].name`, the description, authors, keywords, and `[project.urls]` in
   `pyproject.toml`. Replace every `my-lib` in `pyproject.toml`, `src/`, `tests/`, and
   `docs/gen_config_page.py`: the self-reference `my-lib[logs]` in the `cli` extra, the command
   name in `[project.scripts]`, `version("my-lib")` and the help text in the CLI, and the extra
   names in the error messages of `logs/__init__.py` and `main.py`. Rename `MyLibError` if the name should match the package.
3. Change `env_prefix` and the `env_fields()` default prefix in
   `src/my_package/cli/settings.py`, and `PREFIX` in `docs/gen_config_page.py`. Adjust the
   default log file name in `LogSettings`. Update `.env.example`, README examples, and tests
   using `MY_LIB_` variables.
4. Update `properdocs.yml` (`site_name`, `site_url`, repository links, `edit_uri` if the default
   branch is not `main`, and the source watch path). Update names and links in README, docs,
   `AGENTS.md`, the copyright holder in `LICENSE`, and the PyPI URL in
   `.github/workflows/release.yml`.
5. Configure GitHub Pages and, to publish to PyPI, the trusted publisher and the `PUBLISH_TO_PYPI`
   variable as described above.
6. Regenerate the lockfile with `uv lock`, then run `uv sync --all-groups --locked`,
   `uv run poe check`, `uv build`, and `uv run --group docs properdocs build --strict`.
