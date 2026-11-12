# Getting Started

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Installation

```bash
git clone <repo-url>
cd python-lib-template
uv sync --all-groups --locked
uv run pre-commit install
```

`pre-commit install` sets up three Git hooks:

- `pre-commit` — file hygiene checks, `uv lock` check, actionlint, a check that `.gitignore` hides no source files, ruff (with `--fix`), import-linter, mypy
- `commit-msg` — Conventional Commit format (Commitizen)
- `pre-push` — pytest without coverage

Ruff and mypy run from the locked project environment (`uv run --no-sync`), so hook and CI versions match.

## Using the Library

```python
from my_lib import InvalidInputError, greet

greet("Ada")  # "Hello, Ada!"
```

A base install (`pip install my-lib`) depends only on Pydantic. Optional extras add application features:

| Extra | Adds |
|-------|------|
| `my-lib[logs]` | `my_lib.logs`: `LogSettings` and `setup_logging()` (structlog) |
| `my-lib[cli]` | The `my-lib` command (Typer, Pydantic Settings) and the `logs` extra |

Configure logging in the application, or use the bundled helper:

```python
from my_lib.logs import LogSettings, setup_logging

setup_logging(LogSettings(level="DEBUG"))
```

The command runs the same API:

```bash
uv run my-lib greet Ada
uv run my-lib --verbose greet Ada  # debug logs on stderr
```

## Development Commands

Tasks are available via [poethepoet](https://poethepoet.natn.io/) — run with `uv run poe <name>`:

```bash
uv run poe check        # fmt-check, lint, lint-imports, typecheck, test
uv run poe fmt          # ruff format .
uv run poe fmt-check    # ruff format --check .
uv run poe lint         # ruff check .
uv run poe lint-imports # import-linter layer contracts
uv run poe typecheck    # mypy (strict: src, tests, docs)
uv run poe test         # pytest (parallel, 95% branch coverage enforced)
uv run poe test-fast    # pytest without coverage, parallel, random order
uv run poe docs         # properdocs serve
uv run poe audit        # pip-audit over locked dependencies
```

Tests run in parallel and in random order. pytest-randomly prints the seed at the top of the run; reproduce an order-dependent failure with `uv run pytest -p randomly --randomly-seed=<seed>`. `poe test-fast` skips coverage; `poe check` runs the same quality and test steps as the CI `quality` and `test` jobs.

Or run the tools directly:

```bash
uv run pytest                        # full suite without coverage
uv run pytest --cov                  # with the coverage gate
uv run pytest tests/path/to/test.py  # single file
uv build                             # sdist and wheel in dist/
```

## Versioning & Changelog

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) — enforced by the `commit-msg` pre-commit hook.

```bash
uv run cz bump            # bump version, update CHANGELOG, create tag
git push origin main --tags
uv run cz changelog       # update CHANGELOG without bumping
uv run cz changelog --dry-run
```

Bump type is inferred from commits: `fix:` → patch · `feat:` → minor · `feat!:` / `BREAKING CHANGE:` → major (minor while the version is `0.x`). `cz bump` creates the tag locally; pushing it runs the release workflow, which deploys the docs and, when `PUBLISH_TO_PYPI` is enabled, publishes to PyPI.

## Adding Functionality

See the [architecture guide](architecture.md) for the layers and error handling.

1. Create the code in `src/my_lib/core/slug.py`:

```python
from my_lib.core.errors import InvalidInputError


def slugify(text: str) -> str:
    """Convert text to a lowercase, hyphen-separated slug."""
    words = text.lower().split()
    if not words:
        raise InvalidInputError("text must not be empty")
    return "-".join(words)
```

2. Export it from `src/my_lib/core/__init__.py`:

```python
from .errors import InvalidInputError, MyLibError
from .example import greet
from .slug import slugify

__all__ = ["InvalidInputError", "MyLibError", "greet", "slugify"]
```

   and from `src/my_lib/__init__.py`:

```python
from .core import InvalidInputError, MyLibError, greet, slugify

__all__ = ["InvalidInputError", "MyLibError", "greet", "slugify"]
```

3. Test it in `tests/core/test_slug.py` and add a row to `docs/reference/index.md`.

## Configuration

The `my-lib` command reads `MY_LIB_*` environment variables and a `.env` file in the working directory through `my_lib.cli.settings.load_settings()`; the library itself never reads them. Sections are nested with `__`:

| Prefix | Controls |
|--------|----------|
| `MY_LIB_LOG__*` | Log levels, console renderer, optional log directory, file rotation |

```env
MY_LIB_LOG__LEVEL=DEBUG
MY_LIB_LOG__FORMAT=json
```

All variables are listed on the [configuration page](configuration.md).
