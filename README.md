# python-lib-template

A Python library template with a typed public API that depends only on Pydantic, plus optional extras for structlog logging setup and a Typer command configured from the environment.

## What Is Included

- A `core/` layer with an example function and a `MyLibError` hierarchy, re-exported from `my_lib` with `__all__`; `py.typed` for type checkers
- Library-safe logging: stdlib loggers with a `NullHandler`, and no environment reads or logging configuration at import time
- Optional extras, so library consumers do not install application dependencies: `logs` (structlog) and `cli` (Typer, Pydantic Settings)
- An opt-in `setup_logging()` for applications (`my-lib[logs]`): structlog to stderr (console or JSON) and an optional rotating JSON log file with UTC timestamps
- A minimal `my-lib` command (`my-lib[cli]`) as the composition root: the only place that reads `MY_LIB_*` variables and `.env`, through one Pydantic `Settings` with a nested `MY_LIB_LOG__*` section, a test that keeps `.env.example` in sync, and a generated configuration page
- import-linter layer contracts (`main` → `cli` → `logs` → `core`) that also limit the third-party packages of each layer
- Strict MyPy with the Pydantic plugin, Ruff, pytest in parallel and random order with a 95% branch coverage gate, poethepoet tasks, pre-commit hooks, Commitizen
- CI on Ubuntu and macOS with a lowest-dependency test job, package and strict docs builds, pip-audit, and trivy; actions pinned to commit SHAs; PyPI Trusted Publishing and ProperDocs on GitHub Pages after CI passes on a release tag

## Stack

- **[structlog](https://www.structlog.org/)** — structured logging with context binding; dev console output or JSON for aggregators
- **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** — environment-based configuration of the command
- **[Typer](https://typer.tiangolo.com/)** — optional command-line interface
- **[uv](https://docs.astral.sh/uv/)** — package management and build backend
- **[Ruff](https://docs.astral.sh/ruff/)** — linting and formatting
- **[MyPy](https://mypy.readthedocs.io/)** — strict type checking
- **[pytest](https://docs.pytest.org/)** + **[pytest-xdist](https://github.com/pytest-dev/pytest-xdist)** + **[pytest-randomly](https://github.com/pytest-dev/pytest-randomly)** — parallel tests in random order with coverage enforcement
- **[import-linter](https://import-linter.readthedocs.io/)** — layer boundary contracts
- **[poethepoet](https://poethepoet.natn.io/)** — task runner
- **[commitizen](https://commitizen-tools.github.io/commitizen/)** — Conventional Commits + automated versioning and CHANGELOG
- **[ProperDocs](https://properdocs.org/)** + **[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)** — documentation site

## Requirements

- Python 3.14+
- uv

## Getting Started

```bash
uv sync --all-groups --locked

uv run pre-commit install
```

## Usage

```python
from my_lib import InvalidInputError, greet

greet("Ada")  # "Hello, Ada!"

try:
    greet("")
except InvalidInputError as error:
    ...
```

The library logs through stdlib loggers under `my_lib` and stays silent until the application configures logging. An application that installs `my-lib[logs]` can use the bundled helper:

```python
from my_lib.logs import LogSettings, setup_logging

setup_logging(LogSettings(level="DEBUG", format="json"))
```

With `my-lib[cli]`, the same API is available as a command:

```bash
my-lib greet Ada
my-lib --verbose greet Ada
```

## Development

Run development tasks with [poethepoet](https://poethepoet.natn.io/):

```bash
uv run poe check       # format check, lint, import contracts, type check, tests with coverage
uv run poe fmt
uv run poe test-fast
uv run poe docs
uv run poe audit
```

Or run the tools directly:

```bash
uv run pytest
uv run pytest tests/path/to/test.py
uv build
```

## Docs

```bash
uv run --group docs properdocs serve
uv run --group docs properdocs build --strict
```

Source is in `docs/`. ProperDocs generates the API reference from public docstrings. The release workflow deploys the site to GitHub Pages.

## Versioning & Changelog

This template uses [Conventional Commits](https://www.conventionalcommits.org/) enforced by a `commit-msg` pre-commit hook.

```bash
uv run cz bump
git push origin main --tags

uv run cz changelog --dry-run
```

Bump type is inferred automatically: `fix:` → patch, `feat:` → minor, `feat!:` / `BREAKING CHANGE` → major (minor while the version is `0.x`). `cz bump` creates the tag locally; pushing it starts the release workflow.

## Configuration

The library takes settings as arguments and never reads the environment. The `my-lib` command loads `my_lib.cli.settings.Settings` from `MY_LIB_*` environment variables and `.env`; defaults are in code and the process environment wins. Sections are nested with `__`:

| Prefix | Controls |
|--------|----------|
| `MY_LIB_LOG__*` | Log levels, console renderer, optional log directory, file rotation |

```env
MY_LIB_LOG__LEVEL=DEBUG
MY_LIB_LOG__FORMAT=json
MY_LIB_LOG__DIR=./logs
```

See `.env.example` and the generated configuration page in the documentation site.

## Project Structure

```
src/
└── my_lib/
    ├── __init__.py          # public API (__all__), NullHandler
    ├── py.typed             # PEP 561 marker
    ├── main.py              # my-lib console script; reports a missing cli extra
    ├── cli/                 # my-lib[cli]
    │   ├── app.py           # Typer app: loads settings, sets up logging, calls the library
    │   └── settings.py      # Settings (MY_LIB_*) with the log section
    ├── logs/                # my-lib[logs]
    │   ├── settings.py      # LogSettings
    │   └── setup.py         # opt-in setup_logging() for applications
    └── core/
        ├── errors.py        # MyLibError, InvalidInputError
        └── example.py       # greet() example
tests/                       # mirrors the package; test_package.py checks import-time behaviour
```

## CI/CD

`.github/workflows/ci.yml` runs on every push/PR to `main` and `dev`. Actions are pinned to commit SHAs.

| Job | What it does |
|-----|-------------|
| `quality` | ruff format check, ruff lint, import-linter contracts, strict mypy |
| `test` | parallel tests in random order on Ubuntu and macOS, 95% branch coverage enforced |
| `lowest` | tests against the lowest allowed direct dependencies, with all extras |
| `build` | package build and wheel smoke test (with and without extras), `properdocs build --strict`, pip-audit, trivy filesystem scan (CRITICAL/HIGH) |

Dependabot opens weekly grouped PRs for uv dependencies, GitHub Actions, and pre-commit hooks.

`.github/workflows/release.yml` runs on version tags (`v*`) or via `workflow_dispatch`. It runs CI first, then:

| Job | What it does |
|-----|-------------|
| `build` | checks that the tag matches the project version, builds the sdist and wheel |
| `publish` | publishes to PyPI with Trusted Publishing (tags only, when the `PUBLISH_TO_PYPI` variable is `true`) |
| `docs` | builds the docs with ProperDocs and deploys it to GitHub Pages via GitHub Actions |

To publish a project created from this template, set the repository variable `PUBLISH_TO_PYPI=true` and configure a trusted publisher on PyPI with workflow `release.yml` and environment `pypi`. Set Pages Source to **GitHub Actions** and allow `v*` tags in the `github-pages` environment.

## Using This Template

The distribution, import package, and environment prefix have separate names. Follow the [renaming checklist](https://rwrotson.github.io/python-lib-template/notes/#renaming-the-template) when copying this template into a new project.

### Remove the Example

The example function is meant to be copied, then deleted. When your first real API exists, remove:

- `src/my_lib/core/example.py` and `tests/core/test_example.py`
- `greet` from `src/my_lib/core/__init__.py` and `src/my_lib/__init__.py`
- the `greet` command in `src/my_lib/cli/app.py` and its tests in `tests/cli/test_app.py`
- the `my_lib.core.example` row in `docs/reference/index.md` and the example in this README

Then run `uv run poe check` and `uv run --group docs properdocs build --strict`.

### Remove the CLI

A library without a command keeps `core` and `logs`. Remove:

- `src/my_lib/cli/`, `src/my_lib/main.py`, `tests/cli/`, and `tests/test_main.py`
- the `cli` extra, `[project.scripts]`, and `pydantic-settings` and `typer` from the `dev` group in `pyproject.toml`; the `my_lib.cli` and `my_lib.main` layers and `typer` and `pydantic_settings` from the import-linter contracts
- `.env.example`, `docs/gen_config_page.py`, its `gen-files` script and the Configuration page in `properdocs.yml`, and the `cli` rows in `docs/reference/index.md`; `-e ".[cli]"` becomes `-e ".[logs]"` in the CI `lowest` job

Then run `uv lock` and the checks above.

## Author

Igor Lashkov — rwrotson@yandex.ru
