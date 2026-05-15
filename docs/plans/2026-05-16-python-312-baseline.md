# Python 3.12 Package Baseline

- Date: 2026-05-16
- Task: Establish Python 3.12 as the current public/package baseline
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Make the current Quantleet package, user docs, repo checks, and local
  developer default consistently use Python 3.12 as the beta baseline, while
  leaving historical plan and execution records intact.
- Governing docs:
  - `AGENTS.md`
  - `docs/PLANS.md`
  - `README.md`
  - `docs/site/installation.md`
  - `docs/site/getting-started/index.md`
  - `pyproject.toml`
  - `.python-version`
  - `uv.lock`
  - `tests/structure/repo/test_public_package_metadata.py`
  - `tests/structure/repo/test_repository_entrypoint_docs.py`
- Why these are governing: They define the repo workflow, public package
  metadata, user-facing install guidance, default local Python version, and
  structure tests that enforce the public beta repository surface.
- In-repo scope:
  - Set `requires-python`, classifiers, mypy target, Ruff target, and local
    `.python-version` to Python 3.12.
  - Regenerate `uv.lock` for the new lower bound.
  - Update current public/user-facing docs, current research report text, and
    structure tests.
  - Update notebook kernel metadata only where it is current example surface.
- Out-of-repo scope: none.
- Tier A progression requested: `no`
- Approval record, if required: not required; this is package/docs/test harness
  metadata and compatibility maintenance, not `trading` or `execution` logic.
- Verification commands:
  - `uv run -p 3.12 poe verify`
  - `uv run -p 3.12 poe verify-runtime` if runtime-sensitive checks are
    feasible after the baseline change
  - targeted searches for stale current-surface Python baseline references
- Success criteria:
  - Current package metadata advertises Python `>=3.12`.
  - Current public docs say Python 3.12.
  - Structure tests expect Python 3.12.
  - The package verifies under Python 3.12.
  - Historical plans and execution records are not rewritten.
  - No commit is created.
- Out of scope:
  - Rewriting historical `docs/plans` or `docs/exec-plans`.
  - Adding GitHub Actions workflows.
  - Changing runtime behavior except where Python 3.12 compatibility requires it.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The current public/package
  baseline is Python 3.12 and local verification under Python 3.12 succeeds.
- Acceptance artifact location: this plan.
- How the generator and evaluator agreed on done before execution: This plan
  records scope, exclusions, and verification before edits.
- Checks the evaluator will use:
  - Inspect package metadata and current docs.
  - Search for stale current-surface Python baseline references.
  - Run verification under Python 3.12.
- Auto-fail conditions:
  - `pyproject.toml`, `.python-version`, README, docs/site, or current
    structure tests do not use Python 3.12.
  - `uv.lock` does not declare project `requires-python = ">=3.12"`.
  - Python 3.12 verification fails without a documented blocker.
  - Historical-only references are rewritten unnecessarily.

## Generator Work Log

- Planned slice order:
  1. Update package metadata, local Python default, public docs, tests, and
     current research report text. `complete`
  2. Regenerate the lockfile for Python 3.12. `complete`
  3. Run Python 3.12 verification and current-surface search. `complete`
- Notes:
  - User asked not to commit.
  - Current uncommitted CI/CD research docs are preserved and updated as part
    of the current research surface.
  - Historical `docs/plans` and `docs/exec-plans` records were intentionally
    left intact as audit history.
- Blockers or scope changes:

## Evaluator Review

- Findings:
  - No blocker findings.
  - Current package, public docs, current product spec, notebook metadata, and
    structure tests use the Python 3.12 baseline.
  - `uv.lock` declares project `requires-python = ">=3.12"`.
  - Any numeric version strings left inside the lockfile are dependency
    package versions or wheel tags, not current package baseline declarations.
- Verification evidence:
  - `uv lock -p 3.12`: resolved 86 packages using CPython 3.12.11.
  - `uv run -p 3.12 poe verify`: passed; Ruff, mypy, 739 tests with 4 skipped,
    coverage policy, build, repo-check, and notebook validation all completed.
  - `uv run -p 3.12 poe verify-runtime`: passed; includes the same verification
    lane plus `pytest tests/perf -q -x --run-perf`, 3 passed.
  - `uvx twine check dist/*`: wheel and sdist passed.
  - Isolated wheel smoke under Python 3.12.11: imported and ran
    `BacktestEngine`, `ParameterStudy`, and `WalkForwardStudy`; output
    `wheel smoke ok None 4 4`.
  - Current-surface search for stale Python baseline references across package metadata,
    public docs, current product/design docs, structure tests, README, and
    notebooks returned no matches.
  - `uv run -p 3.12 poe repo-check`: repository checks passed after the final
    product-spec wording update.
- Final disposition: accepted; current public/package baseline is Python 3.12
  and verifies under Python 3.12.
