# Ruff Baseline Remediation

- Date: 2026-05-26
- Task: Fix Ruff baseline findings that can be resolved without human product judgment.
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Resolve every Ruff baseline finding that is mechanically or locally
  inferable, leave only findings that genuinely need human policy judgment, and
  run the repository check surface.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: This is quality-gate remediation on the repository
  check surface. The reliability docs govern check evidence, and the repo
  contract governs plan and safety boundaries.
- In-repo scope:
  - Ruff baseline violations exposed by `E/F/I/UP/B/SIM`
  - Source, test, and notebook edits needed to satisfy those rules
- Out-of-repo scope: none
- Tier A progression requested: `no`
- Approval record, if required: not required. Any Tier A edits are limited to
  behavior-preserving lint simplification and must be verified by tests.
- Verification commands:
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run pytest -q`
  - `uv run poe check`
- Success criteria:
  - Ruff baseline passes or any remaining findings are clearly documented as
    requiring human policy judgment.
  - All locally safe findings are fixed.
  - Fresh check evidence is recorded.
- Out of scope:
  - Adding non-baseline Ruff rules
  - Behavior-changing refactors unrelated to lint findings
  - Using task-driven network access

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Confirm every remaining Ruff
  finding has either been fixed or classified as human-policy-needed, and that
  the requested check surface has fresh evidence.
- Acceptance artifact location: this plan and the final user report
- How the generator and evaluator agreed on done before execution: The user
  requested autonomous remediation for LLM-safe findings and a report for human
  decisions.
- Checks the evaluator will use:
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run pytest -q`
  - `uv run poe check`
  - `git diff --stat`
- Auto-fail conditions:
  - A remaining Ruff baseline finding is not classified.
  - Check failures are ignored.
  - Edits exceed the Ruff baseline remediation scope.

## Generator Work Log

- Planned slice order:
  - Inspect remaining findings.
  - Apply behavior-preserving local fixes.
  - Run Ruff, mypy, pytest, and repo check.
  - Record evidence and human-needed decisions.
- Notes:
  - Safe Ruff autofix was already applied in the previous slice.
  - Manual remediation fixed the remaining baseline findings with local,
    behavior-preserving changes.
  - `zip(sequence, sequence[1:])` sliding-window cases require
    `strict=False`; equal-cardinality internal pairs use `strict=True`.
  - `uv run poe check` initially failed in `diff-cover` because a pre-existing
    untracked non-ASCII Markdown filename was parsed through quoted Git path
    output. No user file content was changed; local Git config
    `core.quotePath=false` made the check command handle the path correctly.
- Blockers or scope changes: none

## Evaluator Review

- Findings:
  - No Ruff baseline findings remain.
  - No human policy decisions remain for the Ruff baseline slice.
  - The pre-existing untracked `코드 품질 기계 검토.md` file remains untouched.
- Verification evidence:
  - `uv run ruff check .`: passed.
  - `uv run mypy src`: passed with no issues in 61 source files.
  - `uv run pytest -q`: passed with 802 passed, 4 skipped, 1 warning.
  - `uv run poe coverage-diff`: passed after `core.quotePath=false`, with
    diff coverage 100% over 47 changed source lines.
  - `uv run poe check`: passed. It completed format check, Ruff, mypy,
    coverage gates, build, Twine check, repo check, and notebook validation.
- Final disposition: complete.
