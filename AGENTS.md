# AGENTS.md

A template for building typed Python libraries with a small public API that depends only on Pydantic, an optional structlog-based logging setup for applications (`logs` extra), and an optional Typer command configured through Pydantic Settings (`cli` extra).

Distribution name: `my-lib` | Python package: `my_lib` | Environment prefix: `MY_LIB_`

## Load instructions by path

For each area of the task, mirror its repo-relative path under [docs/agents](docs/agents/) and read the matching guide before editing: for `src/my_lib/logs/setup.py`, read the [logging guide](docs/agents/src/my_lib/logs.md). For any code change, also read [docs/architecture.md](docs/architecture.md). The [Read when](#read-when) table lists every guide.

## Commands

This project uses [uv](https://docs.astral.sh/uv/) for package management; the full task list is in README "Development".

```bash
uv sync --all-groups --locked
uv run poe check        # fmt-check, lint, lint-imports, typecheck, test (95% branch coverage)
uv run poe quick        # lint, lint-imports, typecheck (no formatting check or tests)
uv run poe test-fast    # pytest without coverage, parallel, random order
uv run poe test-live    # tests/integration against real services; needs --live, reads .env
uv run poe fmt          # ruff format . (rewrites files)
uv run poe audit        # pip-audit over locked dependencies
uv run --group docs properdocs build --strict
```

## Change Workflow

- Inspect `git status` before editing. Preserve existing uncommitted changes and limit edits to the requested task.
- Run `uv run poe check` after code changes. After documentation, `properdocs.yml`, or public docstring changes, also run `uv run --group docs properdocs build --strict`.
- Use non-rewriting checks (`poe fmt-check`, `poe lint`) for verification; run formatters or `--fix` only when intentionally editing files. Pre-commit's Ruff hooks rewrite files.
- Report which checks ran, which were skipped, and why. `poe test-fast` is not the full CI suite: it skips coverage, and CI also runs tests on macOS, the lowest-dependency job, package and docs builds, and security scans.
- When changing settings, the public API, or the command, update `.env.example`, README, and the docs.

## Commit Handoff

- Do not create or amend commits on the user's behalf.
- After completing and verifying a meaningful, self-contained part of the work, pause before starting the next part.
- At each pause, send the user a one-line English Conventional Commit message for the completed work. Resume when the user asks you to continue.

## Layers

```
main  src/my_lib/main.py  `my-lib` console script; reports a missing `cli` extra
cli   src/my_lib/cli/     Typer app, its MY_LIB_* Settings, composition root (`my-lib[cli]`)
logs  src/my_lib/logs/    LogSettings and opt-in setup_logging() for applications (`my-lib[logs]`)
core  src/my_lib/core/    library functionality and the MyLibError hierarchy (base install)
```

`src/my_lib/__init__.py` re-exports the public API with `__all__` and adds a `NullHandler` to the `my_lib` logger. A layer imports only layers below it; `main`, `cli`, and `logs` import library names only from `my_lib`, never from `my_lib.core` modules. The rules are in [docs/architecture.md](docs/architecture.md#rules); `uv run poe lint-imports` enforces them.

## Invariants

- Do not lower coverage thresholds, disable checks, relax import-linter contracts, or add lint and type suppressions solely to pass CI. Explain necessary suppressions at the affected line.
- Importing `my_lib` must not read the environment or `.env`, configure logging or structlog, add handlers outside the `my_lib` logger, import optional dependencies, or perform I/O. `tests/test_package.py` checks this in a fresh interpreter.
- Library code never reads the environment and takes settings objects as arguments; only `load_settings()` in the CLI reads the environment and `.env`.
- Expected failures raise a `MyLibError` subclass.
- Treat everything exported from `my_lib/__init__.py` as public API. Mark removals and incompatible changes with `!` or a `BREAKING CHANGE:` footer so Commitizen bumps the version correctly.
- Tests never use the network, except `tests/integration/` under `--live`.
- Keep the user's `.env` and secrets untracked.

## Code Style

- Internal imports use the `my_lib.` prefix. Ruff bans relative imports except in package `__init__.py`, which may re-export from sibling modules (`from .module import ...`, never `..`).
- Import a module or package whose name starts with `_` only from modules in the same package and its subpackages.
- MyPy runs with `strict = true` and the Pydantic plugin over `src/`, `tests/`, and `docs/`. All new code must have complete type annotations. Prefer `X | Y` over `Optional[X]`.

## Documentation and Comments

- Write documentation, docstrings, and comments in English. Keep them short and factual. Describe each entity's purpose without editorial commentary or tutorials.
- Do not add module docstrings. Package docstrings in `__init__.py` are optional. Put package behavior and important module details in Markdown documentation such as `README.md` or `docs/`.
- Give public classes, functions, and ordinary methods a docstring. Prefer one line describing their overall purpose; do not repeat names, signatures, or type annotations. Ruff checks these in library code. Test functions, fixtures, and standard `dunder` methods are exempt.
- Add docstrings to protected or private objects only when they explain behavior that is not clear from code.
- Keep inline comments only for non-obvious behavior or decisions. Put a short comment on the relevant line when it fits; otherwise place it immediately above. Retain necessary tool directives such as `# noqa` and `# type: ignore`.
- A comment placed above a line or group of lines applies only to it. Separate that line or group from the code before and after it with a blank line, unless it starts or ends a block, so the comment's scope is clear. At module and class level, give each commented constant or attribute its own block, and keep uncommented related definitions together in one block.
- In long functions, methods, and tests, separate logical steps (input validation, setup, execution, result handling; arrange, act, assert) with a single blank line. Do not add comments to label the steps. Keep short functions compact.
- Prefer clearer names and more precise types over comments that restate code.

## Read when

| Task | Read |
| --- | --- |
| Any code change | [docs/architecture.md](docs/architecture.md) (layers, rules, public API, logging, errors) |
| Working in `src/my_lib/core/` or adding functionality | [Core guide](docs/agents/src/my_lib/core.md) |
| Working in `src/my_lib/logs/` | [Logging guide](docs/agents/src/my_lib/logs.md) |
| Working in `src/my_lib/cli/` or `src/my_lib/main.py`, settings, `.env.example` | [CLI guide](docs/agents/src/my_lib/cli.md) |
| Working in `tests/` | [Test guide](docs/agents/tests.md) |
| Working in `docs/`, `properdocs.yml`, or public docstrings | [Docs guide](docs/agents/docs.md) |
| Dependencies, extras, `pyproject.toml`, `uv.lock` | [Dependency guide](docs/agents/pyproject.md) |
| CI, releases, publishing, Dependabot | [GitHub guide](docs/agents/github.md) |
| Renaming the template | [Renaming checklist](docs/notes.md#renaming-the-template) |
