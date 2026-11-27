# Docs

- The site is built with ProperDocs from `docs/` and `properdocs.yml`; `docs/agents/` is excluded from it. Check changes with `uv run --group docs properdocs build --strict`. See the [toolchain notes](../notes.md#documentation-toolchain).
- `docs/gen_ref_pages.py` generates API pages from source modules and skips private packages. `docs/gen_config_page.py` builds the configuration page from `Settings` field types, defaults, and descriptions.
- Do not edit generated pages (configuration, API reference); edit `Settings` field descriptions and source docstrings instead.
- List new public names in `docs/reference/index.md`.
- The generator scripts are type-checked with the rest of the project (mypy strict covers `docs/`).
