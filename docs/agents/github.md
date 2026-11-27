# GitHub

- `.github/workflows/ci.yml` triggers on push/PR to `main` and `dev` and is reusable via `workflow_call`. Workflow permissions are `contents: read`; actions are pinned to commit SHAs. Parallel jobs:
    - **`quality`** — `poe fmt-check`, `poe lint`, `poe lint-imports`, `poe typecheck`.
    - **`test`** — `poe test` (95% branch coverage) on Ubuntu and macOS.
    - **`lowest`** — installs the lowest allowed direct dependencies with the `cli` extra (`--resolution lowest-direct`) and runs pytest; it checks the declared lower bounds, which the lock does not.
    - **`build`** — `uv build` with a wheel smoke test (base install without extras, then the `cli` extra), `properdocs build --strict`, `poe audit`, trivy filesystem scan (CRITICAL/HIGH).
- `.github/workflows/release.yml` triggers on version tags (`v*`) and manual `workflow_dispatch`. It runs CI first, then:
    - **`build`** — on tags, checks that the tag matches `uv version --short`; then `uv build` and uploads `dist/` as an artifact.
    - **`publish`** — tags only, and only when the repository variable `PUBLISH_TO_PYPI` is `true`; publishes `dist/` to **PyPI** with Trusted Publishing (OIDC, the `pypi` environment, `id-token: write`). No API token is stored. Without the variable, a release builds the package and deploys docs; the template repository does not set it.
    - **`docs`** — builds the site with `properdocs build --strict` and deploys it to **GitHub Pages** via `actions/upload-pages-artifact` + `actions/deploy-pages` (the `github-pages` environment).
- To publish a project created from the template, set `PUBLISH_TO_PYPI=true` (Settings → Secrets and variables → Actions → Variables) and add a PyPI trusted publisher for the repository with workflow `release.yml` and environment `pypi`. Pages Source must be set to **"GitHub Actions"** (Settings → Pages), and the `github-pages` environment must allow the `v*` tag. Site: https://rwrotson.github.io/python-lib-template/
- Dependabot opens weekly grouped PRs for uv dependencies (`uv.lock`), GitHub Actions, and pre-commit hooks (`.github/dependabot.yml`).
- `uv run pre-commit install` installs the pre-commit, commit-msg, and pre-push hooks; `uv run pre-commit run --all-files` runs them on all files.
