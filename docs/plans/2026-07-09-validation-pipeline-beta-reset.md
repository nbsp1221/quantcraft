# Validation Pipeline Beta Reset

- Date: 2026-07-09
- Task: Reset `quantcraft.research` around a validation pipeline substrate and WFA public flow
- Status: `active`
- Risk class: `Tier B`
- Requestor: user
- Owner: GJC

## Planner Contract

- Goal: Replace the old beta research study surface with a first-slice validation architecture that exposes `ValidationPipeline`, result/diagnostic/provenance types, `RollingSplitPolicy`, and `WalkForwardValidation`.
- Governing docs:
  - `AGENTS.md`
  - `.gjc/_session-019f4050-9ab9-7000-983c-e8e2a7374e87/plans/ralplan/019f4050-9ab9-7000-983c-e8e2a7374e87/pending-approval.md`
  - `docs/research/2026-07-09-validation-pipeline-architecture-research.md`
  - `docs/research/2026-07-08-backtesting-library-limitations.md`
  - `docs/product-specs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/quantcraft-architecture.md`
- Why these are governing: the repo contract requires an active in-repo plan; the ralplan artifact is the approved execution contract; the research report explains the market/architecture evidence; product/design docs define source-of-record and package boundaries.
- In-repo scope:
  - product-spec reset/supersession for validation pipeline and old parameter/WFA specs;
  - `src/quantcraft/research/validation/` first-slice implementation;
  - `src/quantcraft/research/__init__.py` export reset;
  - tests under `tests/unit/research` and `tests/integration/research` that pin old research APIs;
  - README and site/reference/guide docs that mention old research APIs.
- Out-of-repo scope: external services, live/paper trading, market data fetches, PyPI/npm, non-repo files.
- Tier A progression requested: `no`
- Approval record, if required: not required; this is not `trading` or `execution` Tier A work. Ralplan consensus approval exists in `.gjc/.../pending-approval.md` and execution was requested by the user.
- Verification commands:
  - `uv run pytest -q tests/unit/research tests/integration/research`
  - `uv run python scripts/repo_check.py`
  - `uv run poe check`
- Success criteria:
  - public research exports match the pending approval plan;
  - `MetricSelectionPolicy`, `ParameterStudy`, `GridSearch*`, `WalkForwardStudy`, and old WFA dataclasses are not public exports;
  - pipeline result, diagnostic, artifact, provenance, and stop/skip behavior are tested;
  - WFA runs through `WalkForwardValidation(..., objective=(...))` and produces fold/candidate records with required provenance;
  - public docs/specs no longer describe old beta research APIs as current.
- Out of scope:
  - compatibility wrappers/deprecated aliases;
  - public `MetricSelectionPolicy`;
  - Monte Carlo, purged CV, cost sensitivity, multiple-testing, trust reports, paper/live, shorting, leverage, margin;
  - deferred placeholder modules for future features.

## Evaluator Acceptance Contract

- Evaluator owner: GJC after implementation, with architect and executor QA/red-team review lanes required by Ultragoal before checkpoint.
- Evaluator-owned done contract for this slice: source, tests, product specs, and public docs all reflect the new validation-first public API, and verification commands pass or blockers are recorded.
- Acceptance artifact location: this plan plus Ultragoal ledger/checkpoint evidence.
- How the generator and evaluator agreed on done before execution: ralplan stage-04 final/pending approval with Architect `CLEAR/APPROVE`, Critic `OKAY`, and user corrections around internal-only metric selection.
- Checks the evaluator will use:
  - focused research tests;
  - repo docs check;
  - full repo check;
  - final ai-slop cleanup, architect review, and executor QA/red-team gate.
- Auto-fail conditions:
  - preserving old research APIs as compatibility wrappers;
  - exposing `MetricSelectionPolicy` publicly;
  - adding source placeholders for deferred features;
  - updating code without product spec/docs reset;
  - claiming completion without current verification evidence.

## Generator Work Log

- Planned slice order:
  1. Add/reset product spec authority and docs indexes.
  2. Implement validation core types and pipeline.
  3. Implement rolling split and WFA public flow using direct objective tuples.
  4. Reset public exports.
  5. Port/delete research tests to new contracts.
  6. Update public docs and sweep old symbols.
  7. Run focused and repo verification.
- Notes:
  - Compatibility is intentionally not a constraint.
  - Private selection internals may be named freely as long as public API stays clean.
- Blockers or scope changes: none.

## Evaluator Review

- Findings: no blocking findings. Final architect review returned `CLEAR/CLEAR/CLEAR`
  and `APPROVE`; executor QA/red-team passed; cleanup sweep reported no blocking
  findings and the remaining low docs-label advisory was resolved.
- Verification evidence:
  - `uv run poe check` passed after final fixes: ruff format/check, vulture,
    duplicate-code, dependency, mypy, coverage pytest suite (`771 passed,
    4 skipped, 1 warning`), diff coverage, coverage baseline, mutation score,
    build, twine, repo check, and notebook validation.
  - `agent://23-FinalValidationArchitect` approved architecture, product, and
    code lanes with no blockers.
  - `agent://22-FinalExecutorQaRedTeam` passed public API, retired API,
    WFA, split policy, pipeline behavior, and docs/spec red-team checks.
- Final disposition: accepted for Ultragoal completion checkpoint.
