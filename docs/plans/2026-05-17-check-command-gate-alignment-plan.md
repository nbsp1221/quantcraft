# Check Command Gate Alignment Plan

- Date: 2026-05-17
- Task: Rename the default local gate from `verify` to `check` and align it
  with CI-required gates.
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Fix the current CI format failure, replace the `verify` command surface
  with `check` without leaving a `verify` alias, and make `check` the canonical
  local quality gate that includes the conventional CI-required gates.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `docs/RELIABILITY.md`
  - `docs/references/testing.md`
  - `docs/PLANS.md`
- Why these are governing:
  - `AGENTS.md` defines the repo entry contract and local verification command
    surface for agents.
  - `README.md` is the user-facing quickstart command surface.
  - `docs/RELIABILITY.md` defines local reliability gates.
  - `docs/references/testing.md` defines test and coverage command lanes.
  - `docs/PLANS.md` defines active plan location and workflow authority.
- In-repo scope:
  - Rename the default Poe task from `verify` to `check`.
  - Rename `verify-runtime` to `check-runtime`.
  - Do not keep `verify` or `verify-runtime` aliases.
  - Add `format-check` to the canonical `check` sequence.
  - Add `twine-check` to the canonical `check` sequence after package build.
  - Keep existing standalone commands such as `format`, `format-check`, `lint`,
    `typecheck`, `test`, `coverage`, `coverage-diff`, `coverage-gates`, `build`,
    `twine-check`, `repo-check`, and `notebook-validate`.
  - Update active docs, command-surface tests, repo-check contracts, and
    user-facing command references.
  - Fix the Ruff formatting failure in
    `tests/structure/repo/test_coverage_harness.py`.
  - Use subagent review before final reporting.
- Out-of-repo scope:
  - No commit.
  - No push.
  - No CI workflow behavior change unless a reference to the renamed task is
    present.
  - No rewrite of historical completed plans or historical verification
    evidence.
- Tier A progression requested: `no`
- Approval record, if required: not required.
- Verification commands:
  - `uv run poe format-check`
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py tests/structure/repo/test_runtime_check_lane.py tests/structure/docs/test_system_of_record_docs.py tests/structure/repo/test_repository_entrypoint_docs.py tests/integration/commands/test_poe_task_runner.py -q`
  - `uv run poe repo-check`
  - `uv run poe check`
  - `uv run poe check-runtime`
- Success criteria:
  - `uv run poe format-check` passes.
  - `pyproject.toml` has `check` and `check-runtime` tasks.
  - `pyproject.toml` has no `verify` or `verify-runtime` task.
  - `check` includes `format-check`, `lint`, `typecheck`, `coverage-gates`,
    `build`, `twine-check`, `repo-check`, and `notebook-validate`.
  - `check-runtime` runs `check` and `perf-check`.
  - Active docs and command-surface tests refer to `check` / `check-runtime`
    instead of `verify` / `verify-runtime`.
  - Historical plan evidence is not rewritten just to hide old command names.
  - Subagent review finds no blocker or important issue.
- Out of scope:
  - Changing public package behavior.
  - Changing release or publish workflows.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm no `verify` Poe task or alias remains.
  - Confirm the current format failure is fixed.
  - Confirm `check` is a conventional local quality gate with formatting,
    linting, typing, coverage-backed tests, build, repo checks, and notebook
    validation.
  - Confirm built package artifacts are validated with Twine after `uv build`.
  - Confirm docs/tests reflect the new command surface.
  - Confirm subagent review was completed and issues were handled.
- Acceptance artifact location:
  - this plan
- How the generator and evaluator agreed on done before execution:
  - Done means local and CI-required non-release gates no longer drift on
    formatting, and the repo exposes `check` as the only default local gate.
- Checks the evaluator will use:
  - focused structure and integration tests
  - `format-check`
  - `repo-check`
  - `check`
  - `check-runtime`
  - grep audit for remaining non-historical `verify` command references
- Auto-fail conditions:
  - A `verify` alias remains.
  - `format-check` is not part of `check`.
  - Active docs still direct agents or users to `uv run poe verify`.
  - The renamed runtime-sensitive lane still calls `verify`.

## Generator Work Log

- Planned slice order:
  - Audit current `verify` and `verify-runtime` references.
  - Update Poe tasks and repo-check required task names.
  - Update active docs and structure tests.
  - Run formatter and focused tests.
  - Run full `check` and runtime-sensitive `check-runtime`.
  - Run subagent review.
- Notes:
  - CI failure before this slice: `ruff format --check .` would reformat
    `tests/structure/repo/test_coverage_harness.py`.
- Blockers or scope changes:
  - None at planning time.

## Evaluator Review

- Findings:
  - Subagent review found an important gap: tests and repo-check did not
    enforce the "no `verify` / `verify-runtime` alias" contract. Fixed by
    adding forbidden Poe task checks in `src/quantleet/_repo_tools.py` and
    structure tests that fail if those aliases return.
  - Subagent review found active doc wording that still said "default
    verification" and an active exec-plan reference to the old runtime test
    filename. Fixed by changing those active references to `check` /
    `test_runtime_check_lane.py`.
  - Subagent review found that local `check` did not include CI's Twine
    distribution validation. Fixed by adding `twine-check` after `build` in
    `check`, and by narrowing CI/release Twine globs to wheel and sdist files.
  - A re-run of `uv run poe check` initially failed because `dist/*` included
    local `dist/.gitignore`; fixed by using
    `dist/*.whl dist/*.tar.gz` for Twine checks.
- Verification evidence:
  - `uv run poe format-check` passed: `197 files already formatted`.
  - Focused command-surface tests passed:
    `40 passed in 0.42s`.
  - `uv run poe repo-check` passed: `repository checks passed`.
  - `uv run poe check` passed: Ruff format/lint, mypy, pytest
    `740 passed, 4 skipped`, coverage `91%`, diff coverage `100%` for changed
    source lines, `uv build`, `twine-check`, repo-check, and notebook
    validation all passed.
  - `uv run poe check-runtime` passed: the full `check` lane plus
    `tests/perf` with `3 passed`.
  - Stale command audit found no non-historical `uv run poe verify`,
    `verify-runtime`, or Poe `verify` task references outside intentional
    forbidden-alias tests and historical report material.
  - Negative alias proof: `uv run poe verify` returns
    `Error: Unrecognized task 'verify'`.
- Final disposition:
  - Accepted. Blocker and important review findings were fixed and rechecked.
