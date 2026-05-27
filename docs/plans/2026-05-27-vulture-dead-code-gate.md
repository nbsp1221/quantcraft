- Date: 2026-05-27
- Task: Add an experimental Vulture dead-code gate
- Status: `active`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Add Vulture as a repository-local dead-code check, wire it into the
  existing Poe check surface, and verify that the gate currently fails before
  any dead-code fixes or suppressions are applied.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `docs/PLANS.md`
- Why these are governing:
  - `AGENTS.md` defines the planner/generator/evaluator workflow and canonical
    check commands.
  - `README.md` documents contributor setup around `uv run poe check`.
  - `docs/PLANS.md` defines where active plan artifacts live.
- In-repo scope:
  - `pyproject.toml`
  - `uv.lock`
  - `AGENTS.md`
  - Poe contract tests and repo-check contract helpers
  - the targeted unit test that exposes the current Vulture finding
  - this plan artifact
- Out-of-repo scope: none
- Tier A progression requested: `no`
- Approval record, if required: not required; this changes repository quality
  tooling only and does not alter trading or execution behavior.
- Verification commands:
  - `uv run poe dead-code`
  - `uv run poe check`
- Success criteria:
  - Vulture is a dev dependency managed by `uv`.
  - Vulture settings live in `pyproject.toml`.
  - A Poe task exposes the dead-code check using existing task naming style.
  - The default `check` sequence includes the new dead-code gate.
  - The new gate demonstrably fails on the current known finding.
- Out of scope:
  - Suppressing Vulture findings with a whitelist or ignore rule.
  - Adding a whitelist.
  - Changing runtime behavior.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: inspect the diff for scope
  control, then run the new targeted task and default check far enough to prove
  the new gate is active and failing for the expected Vulture finding.
- Acceptance artifact location: this plan.
- How the generator and evaluator agreed on done before execution: this plan
  defines the only intended edits and expected failing verification.
- Checks the evaluator will use:
  - `uv run poe dead-code`
  - `uv run poe check`
- Auto-fail conditions:
  - The gate is not reachable via Poe.
  - `uv run poe check` does not include the Vulture task.
  - Any source/test behavior is modified in this slice.

## Generator Work Log

- Planned slice order:
  - Add Vulture to the development dependency group.
  - Add `[tool.vulture]` configuration.
  - Add `dead-code` Poe task and include it in `check`.
  - Fix the actionable test fake signature finding by asserting the subprocess
    options it receives.
  - Update Poe contract tests and repo-check helpers for the new required task.
  - Run targeted and aggregate checks to confirm the gate passes after the
    finding is resolved.
- Notes:
  - Initial threshold is `min_confidence = 80` so 60% public API and test-helper
    inventory remains out of the default gate while 90/100 confidence findings
    are enforced.
- Blockers or scope changes: none

## Evaluator Review

- Findings:
  - No scope issues found. The slice adds the Vulture development dependency,
    Vulture configuration, a Poe task, default-check wiring, and the matching
    repository contract updates.
  - The initial gate failure was actionable test code, not a dead-code
    suppression case. The fake `subprocess.run` now asserts the keyword options
    it receives, preserving the production contract and satisfying Vulture.
- Verification evidence:
  - `uv run poe dead-code` passed.
  - `uv run pytest tests/unit/scripts/test_coverage_baseline.py
    tests/structure/repo/test_coverage_harness.py
    tests/structure/repo/test_poe_task_contracts.py -q` passed with 34 tests.
  - `uv run pytest tests/structure/repo/test_repo_check_contracts.py
    tests/structure/repo/test_poe_task_contracts.py
    tests/structure/repo/test_coverage_harness.py -q` passed with 29 tests.
  - `uv run ruff check AGENTS.md src/quantleet/_repo_tools.py
    tests/unit/scripts/test_coverage_baseline.py
    tests/structure/repo/test_coverage_harness.py
    tests/structure/repo/test_poe_task_contracts.py
    tests/structure/repo/test_repo_check_contracts.py` passed.
  - `uv run mypy src` passed.
  - `uv run poe check` passed: 813 tests passed, 4 skipped, 1 warning; Vulture,
    mypy, coverage, build, twine, repo-check, and notebook validation all
    completed successfully.
- Final disposition: complete.
