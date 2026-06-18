# Active Plan

- Date: 2026-06-18
- Task: Complete the public library rename to Quantcraft
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal:
  - Make this public open-source library consistently use the
    Quantcraft/`quantcraft` identity so the service name can be handled outside
    this repository.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/public-beta-documentation.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/quantcraft-architecture.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `.github/workflows/release.yaml`
- Why these are governing:
  - The change affects the installable package root, distribution metadata,
    public imports, release-facing docs, public beta docs, CI/release
    workflows, notebooks, tests, and package verification.
  - The package topology docs define the engine package boundary that is being
    renamed.
  - The public beta documentation spec controls release-facing public wording
    and import examples.
  - The release workflow governs the tag-to-PyPI publication path that must
    target the new project name.
- In-repo scope:
  - Move the source package root to `src/quantcraft`.
  - Update Python imports in `src/`, `tests/`, and `scripts/`.
  - Update notebooks and notebook-derived docs that teach imports.
  - Update package metadata, project URLs, mypy, coverage, deptry, mutmut, and
    build/release settings in `pyproject.toml`.
  - Update current release-facing docs, public docs, governing docs, tests, and
    repo-local tooling to use Quantcraft/`quantcraft`.
  - Update historical internal docs only when they function as current checks,
    routing authority, or active public/package identity evidence.
  - Preserve behavior while changing import/package identity.
- Out-of-repo scope:
  - Do not rename the GitHub repository during this in-repo implementation
    slice.
  - Do not publish to PyPI, yank PyPI releases, delete PyPI projects, create
    tags, push commits, or change GitHub/PyPI settings from this run.
  - Do not create the future private app repository.
  - Do not rename or create `rice-hunters/quantlabs`.
- Tier A progression requested: `no`
- Approval record, if required:
  - In-repo rename approval:
    - Requestor: user
    - Human approver: user
    - Check marker: chat request on 2026-06-18 asking Codex to proceed with the
      plan and stop before human-required actions
    - Granted scope: in-repo package/docs/test/workflow rename to Quantcraft
    - Expiration: end of this rename task
    - Audit reference: this active plan
  - External GitHub/PyPI actions:
    - Not approved for execution in this implementation slice. Codex must stop
      and ask before any remote rename, tag push, PyPI publish, PyPI yank, or
      PyPI deletion.
- Verification commands:
  - `git status -sb`
  - stale-name sweep scoped to current active source/docs/tests after migration
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run pytest tests/structure -q`
  - `uv run pytest tests/smoke/local -q`
  - `uv run pytest tests/integration/commands -q`
  - `uv run poe repo-check`
  - `uv run poe build`
  - `uvx twine check --strict dist/*.whl dist/*.tar.gz`
  - Isolated wheel install/import smoke for `quantcraft`
- Success criteria:
  - `import quantcraft` works from the source checkout and built wheel.
  - Public examples and public docs use `quantcraft.*` imports and
    `quantcraft==0.1.0b1` install guidance.
  - The built wheel is named `quantcraft-0.1.0b1-...whl`.
  - Repo-local structure checks understand `src/quantcraft` as the engine
    package root.
  - Existing runtime behavior remains unchanged except import paths and
    identity metadata.
  - External release actions are documented but not executed.
- Out of scope:
  - Any live trading, paper trading, shorting, leverage, multi-symbol, or
    multi-timeframe runtime expansion.
  - Adding a long-term compatibility package in this repository.
  - Creating or modifying the future private service repository.
  - Publishing, yanking, deleting, or renaming PyPI projects from this run.

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex evaluator pass after implementation.
- Evaluator-owned done contract for this slice:
  - The diff is primarily a rename and metadata/docs alignment.
  - No trading or execution semantics change.
  - Public package identity is consistently Quantcraft/`quantcraft`.
  - External GitHub/PyPI steps are listed for the human but not executed.
- Acceptance artifact location:
  - This plan's `## Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - The planner contract, verification commands, success criteria, and
    auto-fail conditions were written before edits.
- Checks the evaluator will use:
  - Inspect `git diff --stat` and `git diff --name-status`.
  - Run the verification commands listed above as feasible.
  - Inspect package metadata and built artifact names.
  - Search active public/source/test surfaces for stale previous-name identity.
- Auto-fail conditions:
  - A remote repository rename, PyPI publish, PyPI yank, PyPI deletion, tag
    creation, push, or commit is performed without a fresh explicit human
    approval.
  - `pyproject.toml` does not name the distribution `quantcraft`.
  - Source package root is not `src/quantcraft`.
  - Public docs do not instruct users to install or import `quantcraft` as the
    current library.
  - Runtime semantics under `trading` or `execution` are changed beyond import
    paths.
  - Built wheel fails to import `quantcraft`.

## Generator Work Log

- Planned slice order:
  1. Move source package root and update Python imports.
  2. Update package metadata and repo-local tool assumptions.
  3. Update tests, public docs, governing docs, notebooks, and workflows.
  4. Run focused checks and fix rename misses.
  5. Build artifacts and run isolated import smoke.
  6. Document human-required GitHub/PyPI follow-up steps.
  7. Record evaluator review with fresh evidence.
- Notes:
  - Remote repository rename is a human-required external action and will not
    be executed by Codex in this slice.
  - PyPI publication/yanking/deletion are human-required external actions and
    will not be executed by Codex in this slice.
  - Source package root was moved to `src/quantcraft`.
  - Tracked text, tests, docs, notebooks, package metadata, and workflow
    metadata were mechanically updated to Quantcraft/`quantcraft`.
  - Ruff formatting was applied to `src/quantcraft/strategy/config.py` after
    the rename changed formatting width.
  - Build artifacts were regenerated as `quantcraft-0.1.0b1`.
  - No remote repository rename, tag push, PyPI publication, PyPI yank, PyPI
    deletion, or commit was performed.
  - Human-required external follow-up:
    1. Rename the GitHub repository to the Quantcraft repository name.
    2. Update the local `origin` URL after the remote rename.
    3. Configure PyPI Trusted Publishing for the Quantcraft package.
    4. Tag and publish `v0.1.0b1` for Quantcraft after human review.
    5. Apply the chosen deprecation/yank handling for the previous PyPI
       package name.
- Blockers or scope changes:
  - None yet.

## Evaluator Review

- Findings:
  - No blocker findings.
  - The diff is intentionally large because it is a repository-wide identity
    rename across source, tests, docs, notebooks, package metadata, and
    workflow metadata.
  - Runtime files under trading/backtest/research/strategy were changed for
    import-path identity only; no trading or execution semantics were
    deliberately changed.
  - External GitHub and PyPI actions remain unexecuted as required.
- Verification evidence:
  - `rg -n` stale previous-name sweep over the repository, excluding generated
    artifacts, returned no matches.
  - `uv run ruff check .` -> passed.
  - `uv run mypy src` -> `Success: no issues found in 60 source files`.
  - `uv run pytest tests/structure -q` -> `161 passed`.
  - `uv run pytest tests/smoke/local -q` -> `10 passed`, with the existing
    `requests` dependency warning.
  - `uv run pytest tests/integration/commands -q` -> `5 passed`.
  - `uv run poe repo-check` -> `repository checks passed`.
  - `uv run poe format-check` -> `205 files already formatted`.
  - `uv run poe dependency-check` -> `Success! No dependency issues found`.
  - `uv run pytest -q` -> `849 passed, 4 skipped`, with the existing
    `requests` dependency warning.
  - `uv run poe notebook-validate` -> all five tracked notebooks validated.
  - `git diff --check` -> passed.
  - `uv run poe build` -> built `dist/quantcraft-0.1.0b1.tar.gz` and
    `dist/quantcraft-0.1.0b1-py3-none-any.whl`.
  - `uvx twine check --strict dist/*.whl dist/*.tar.gz` -> both artifacts
    passed.
  - Isolated wheel install/import smoke -> installed the built wheel and
    imported `quantcraft`, `BacktestEngine`, `CostConfig`, and
    `DataFrameDataSource`.
  - `uv run poe coverage` -> `849 passed, 4 skipped`; total coverage `93%`.
- Final disposition:
  - Accepted for this in-repo rename slice. Human review is required before
    any remote repository rename, tag push, PyPI publication, PyPI yank, or
    PyPI deletion.
