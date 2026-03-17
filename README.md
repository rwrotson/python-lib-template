# python-lib-template

A template for building Python libraries with structured logging, environment-based configuration, and a modern toolchain.

## Stack

- **[structlog](https://www.structlog.org/)** — structured logging with context binding; dev console output or JSON for aggregators
- **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** — environment-based configuration
- **[uv](https://docs.astral.sh/uv/)** — package management
- **[Ruff](https://docs.astral.sh/ruff/)** — linting and formatting
- **[MyPy](https://mypy.readthedocs.io/)** — strict type checking
- **[pytest](https://docs.pytest.org/)** + **[pytest-xdist](https://github.com/pytest-dev/pytest-xdist)** — parallel testing with coverage enforcement
- **[commitizen](https://commitizen-tools.github.io/commitizen/)** — Conventional Commits + automated versioning and CHANGELOG
- **[MkDocs Material](https://squidfunk.github.io/mkdocs-material/)** — documentation site

## Requirements

- Python 3.13+
- uv

## Getting Started

```bash
# Clone the repo and install dependencies
uv sync --all-extras

# Install pre-commit hooks (enforces Conventional Commits)
uv run pre-commit install
```

## Development

Tasks are available via [taskipy](https://github.com/taskipy/taskipy) — run with `uv run task <name>`:

```bash
uv run task lint        # ruff check
uv run task fmt         # ruff format
uv run task typecheck   # mypy src/
uv run task test        # pytest (parallel, 80% coverage enforced)
uv run task test-fast   # pytest --no-cov -n auto
uv run task audit       # pip-audit dependency audit
```

Or run the tools directly:

```bash
uv run pytest --no-cov -n auto          # fast parallel run
uv run pytest tests/path/to/test.py     # single file
```

## Docs

```bash
uv run --group docs mkdocs serve      # live preview at http://127.0.0.1:8000
uv run --group docs mkdocs build      # build static site to site/
uv run --group docs mkdocs gh-deploy  # deploy to GitHub Pages (gh-pages branch)
```

Source is in `docs/`. Powered by [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) with `mkdocstrings` for API reference generation.

## Versioning & Changelog

This template uses [Conventional Commits](https://www.conventionalcommits.org/) enforced by a `commit-msg` pre-commit hook.

```bash
# Bump version, update CHANGELOG, tag
uv run cz bump

# Preview changelog without bumping
uv run cz changelog --dry-run
```

Bump type is inferred automatically: `fix:` → patch, `feat:` → minor, `feat!:` / `BREAKING CHANGE` → major.

## Configuration

Logging behaviour can be configured via environment variables or a `.env` file:

| Prefix | Controls |
|--------|----------|
| `LIB_LOG_*` | Log level, file rotation, JSON output |

```env
LIB_LOG_LEVEL=DEBUG
LIB_LOG_USE_JSON_FORMATTER=true   # emit JSON logs (for Datadog, Loki, etc.)
```

## Project Structure

```
src/
└── lib/                     # rename to your package name
    ├── utils/
    │   ├── log.py           # structlog setup (ConsoleRenderer dev / JSON prod)
    │   └── misc.py          # find_project_root()
    └── pkg/                 # placeholder for your domain modules
tests/
    └── utils/
        ├── test_log.py
        └── test_misc.py
```

## CI/CD

`.github/workflows/ci.yml` runs on every push/PR to `main` and `dev`:

| Step | What it does |
|------|-------------|
| ruff format | formatting check |
| ruff lint | linting |
| mypy | strict type checking |
| pytest | parallel tests, 80% coverage enforced |
| pip-audit | known CVE check for dependencies |
| trivy | filesystem vulnerability scan (CRITICAL/HIGH, fails build) |

Dependabot opens weekly PRs for both pip packages and GitHub Actions.

`.github/workflows/release.yml` runs on version tags (`v*`):

| Job | What it does |
|-----|-------------|
| `publish` | builds the package and publishes to PyPI via OIDC trusted publisher (no secrets) |
| `docs` | deploys MkDocs to GitHub Pages |

PyPI publishing uses keyless OIDC — configure a trusted publisher on PyPI pointing to this repo with workflow file `release.yml`.

## Author

Igor Lashkov — rwrotson@yandex.ru
