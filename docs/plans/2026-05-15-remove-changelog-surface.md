# Remove Changelog Surface

- Date: 2026-05-15
- Task: Remove `CHANGELOG.md` from the current release-facing repository surface
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Delete `CHANGELOG.md` and remove current public/release-facing references so the project behaves as if a standalone changelog is not part of the beta repository contract.
- Governing docs:
  - `AGENTS.md`
  - `docs/PLANS.md`
  - `README.md`
  - `docs/product-specs/public-beta-documentation.md`
  - `src/quantleet/_repo_tools.py`
  - `tests/structure/repo/test_repository_entrypoint_docs.py`
  - `tests/structure/repo/test_public_package_metadata.py`
  - `tests/structure/repo/test_poe_task_contracts.py`
- Why these are governing: They define current workflow, public beta docs, repo-check required docs, and tests that enforce the release-facing documentation surface.
- In-repo scope:
  - Remove `CHANGELOG.md`.
  - Remove changelog references from current user-facing docs, PR template, package metadata, repo-check contract, and structure tests.
  - Update the current public beta product spec where it still requires a changelog as a present-day release-facing artifact.
- Out-of-repo scope: none.
- Tier A progression requested: `no`
- Approval record, if required: not required; this is documentation/repo-contract maintenance and does not touch `trading` or `execution`.
- Verification commands:
  - `uv run pytest tests/structure/repo -q`
  - `uv run poe repo-check`
- Success criteria:
  - `CHANGELOG.md` no longer exists.
  - Current public/release-facing docs and metadata no longer link to or require `CHANGELOG.md`.
  - Historical/audit records are left intact.
  - Structure checks and repo-check pass.
- Out of scope:
  - Rewriting historical plans or old research notes.
  - Changing runtime behavior.
  - Adding a replacement release-notes system.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Diff removes only the current changelog surface and keeps historical records untouched unless they are current product-contract requirements.
- Acceptance artifact location: this plan.
- How the generator and evaluator agreed on done before execution: This plan records the scope and verification commands before edits.
- Checks the evaluator will use:
  - Search for remaining current changelog references.
  - Run targeted structure tests.
  - Run repo-check.
- Auto-fail conditions:
  - `CHANGELOG.md` still exists.
  - Current README, package metadata, PR template, repo tools, or current public beta spec still require the changelog.
  - Verification commands fail.

## Generator Work Log

- Planned slice order:
  1. Remove current changelog references and delete `CHANGELOG.md`. `complete`
  2. Update repo-check and structure tests. `complete`
  3. Run targeted verification and record results. `complete`
- Notes:
  - Historical plans and research notes that mention changelog policy were left
    unchanged as audit history.
- Blockers or scope changes:

## Evaluator Review

- Findings:
  - No blocker findings.
  - Current changelog references remain only as negative assertions in structure
    tests.
  - Historical plans/research notes were intentionally left unchanged.
- Verification evidence:
  - `uv run pytest tests/structure/repo -q`: 50 passed.
  - `uv run poe repo-check`: repository checks passed.
  - `git diff --check`: passed with no output.
- Final disposition: accepted; the current repository surface no longer treats
  `CHANGELOG.md` as a required beta artifact.
