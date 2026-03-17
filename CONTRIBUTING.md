# Contributing

## Setup

```bash
git clone https://github.com/rwrotson/python-lib-template
cd python-lib-template
uv sync --all-extras
uv run pre-commit install
```

## Running checks

```bash
uv run task lint        # ruff check
uv run task fmt         # ruff format
uv run task typecheck   # mypy
uv run task test        # pytest (80% coverage enforced)
```

## Commit format

This project uses [Conventional Commits](https://www.conventionalcommits.org/), enforced by the `commit-msg` pre-commit hook via commitizen.

Examples: `feat: add X`, `fix: correct Y`, `chore: update deps`, `docs: explain Z`.

## Pull requests

1. Branch off `main`
2. Make your changes with passing tests and types
3. Open a PR with a clear description of what changed and why

## Renaming the template

See [docs/notes.md](docs/notes.md) for step-by-step instructions on adapting this template to your project.
