# Dependencies

- Put runtime imports needed by the core in `[project].dependencies` and those of outer layers in their extra (`logs`, `cli`); also list extra packages in the `dev` group so tests can import them. Put development tools in the `dev` group and documentation tools in the `docs` group.
- Keep runtime dependencies minimal and lower bounds wide enough for library consumers; they share one environment with the application.
- Change dependencies through uv (`uv add`, `uv remove`) so `pyproject.toml` and `uv.lock` change together. Verify the lock with `uv sync --locked --all-groups`.
- Raise a direct dependency's lower bound when code needs a newer API. The locked environment does not check lower bounds; the CI `lowest` job does.
- Do not import packages that are installed only as transitive dependencies.
- Add a new third-party dependency to the lowest layer that needs it and to that layer's extra (none for `core`), and update the import-linter contract that lists the layer's allowed packages.
- Security floors for transitive dependencies go in `[tool.uv] constraint-dependencies`.
- Use the project environment for tools. Do not install packages manually into `.venv`.
- The uv build backend loads `my_lib` from `src/` (`[tool.uv.build-backend]`, `module-name = "my_lib"`, `module-root = "src"`). `src/my_lib/py.typed` marks the package as typed (PEP 561); keep it in the wheel. See the [build backend notes](../notes.md#build-backend).
- Versioning: `uv run cz bump` bumps the version, updates `CHANGELOG.md`, and tags; `uv run cz changelog` updates the changelog only. Build with `uv build`.
