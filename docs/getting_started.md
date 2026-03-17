# Getting Started

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Installation

```bash
git clone <repo-url>
cd python-lib-template
uv sync --all-extras
uv run pre-commit install
```

## Development Commands

Tasks are available via taskipy — run with `uv run task <name>`:

```bash
uv run task lint        # ruff check .
uv run task fmt         # ruff format .
uv run task typecheck   # mypy src/
uv run task test        # pytest (parallel, 80% coverage enforced)
uv run task test-fast   # pytest --no-cov -n auto
uv run task audit       # pip-audit dependency audit
```

Or run the tools directly:

```bash
uv run pytest                        # full suite
uv run pytest --no-cov               # skip coverage (faster)
uv run pytest tests/path/to/test.py  # single file
```

## Versioning & Changelog

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) — enforced by the `commit-msg` pre-commit hook.

```bash
uv run cz bump            # bump version, update CHANGELOG, create tag
uv run cz changelog       # update CHANGELOG without bumping
uv run cz changelog --dry-run
```

Bump type is inferred from commits: `fix:` → patch · `feat:` → minor · `feat!:` / `BREAKING CHANGE:` → major.

## Configuration

Behaviour can be overridden via environment variables or a `.env` file:

| Prefix | Controls |
|--------|----------|
| `LIB_LOG_*` | Log level, file path, rotation, JSON format |

```env
LIB_LOG_LEVEL=DEBUG
LIB_LOG_USE_JSON_FORMATTER=true   # JSON logs for Datadog/Loki/etc.
```
