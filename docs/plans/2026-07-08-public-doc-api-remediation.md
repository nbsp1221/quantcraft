# Public Doc API Remediation

- Date: 2026-07-08
- Task: Re-verify critical/high public documentation API issues and fix confirmed defects.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: GJC

## Planner Contract

- Goal: Confirm whether the reported public beta documentation/API mismatches are real, then patch only confirmed documentation defects without changing product behavior.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/direct-backtest-class-config-api.md`
  - `docs/product-specs/reporting-config-source-of-truth.md`
  - `docs/product-specs/public-beta-documentation.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: The task concerns public beta docs, direct `BacktestEngine.run` strategy config usage, reporting config provenance, and user-facing research ergonomics in the current backtest beta surface.
- In-repo scope: README and public docs/examples under `docs/site` plus focused verification scripts/commands.
- Out-of-repo scope: Publishing packages, changing PyPI metadata, adding new product features, live/paper trading, external exchange calls.
- Tier A progression requested: `no`
- Approval record, if required: Not required; this is Tier B documentation remediation only.
- Verification commands:
  - Search public docs for stale `config={...}`, `.selected()`, and wrong report field names.
  - Run focused snippets/probes against the installed package or local source.
  - `uv run python scripts/repo_check.py`
  - `uv run pytest tests/smoke/local -q`
- Success criteria:
  - Every confirmed critical/high public documentation mismatch is corrected.
  - Public quickstart examples use the actual `StrategyConfig` instance contract.
  - No unsupported future-scope gap is misclassified as a bug or hidden by docs edits.
  - Focused checks pass from the current repository state.
- Out of scope:
  - Adding dict config support.
  - Adding multi-symbol, multi-timeframe, live/paper, leverage, or shorting support.
  - Reworking product positioning beyond confirmed API/doc mismatches.

## Evaluator Acceptance Contract

- Evaluator owner: GJC
- Evaluator-owned done contract for this slice: Review the diff against confirmed evidence, verify that each edit maps to a real mismatch, and ensure no beta-scope limitation is treated as a defect.
- Acceptance artifact location: This plan's Evaluator Review section.
- How the generator and evaluator agreed on done before execution: The planner contract limits edits to confirmed public documentation defects and requires focused repo checks.
- Checks the evaluator will use:
  - Public-doc search evidence for stale examples.
  - Focused smoke/documentation checks.
  - Manual diff review against governing docs.
- Auto-fail conditions:
  - Product code behavior changes without explicit need.
  - Documentation claims support for out-of-scope beta features.
  - Public examples still show APIs that fail against current implementation.

## Generator Work Log

- Planned slice order:
  1. Search public docs for suspected stale API expressions.
  2. Re-run failing/working snippets to classify true defects.
  3. Patch only confirmed public docs mismatches.
  4. Run focused checks and record evidence.
- Notes:
  - Public docs search found no current `config={...}`, `.selected()`, `grid.selected(...)`, `closed_count`, or `strategy_parameters` usage in `README.md` or `docs/site`.
  - Focused runtime probe confirmed direct dict config is rejected with `TypeError: config must be a StrategyConfig instance or None`, while a matching `StrategyConfig` instance records `report.run.strategy_config`.
  - The confirmed high issue was clarity: public docs named `config=...` without stating the direct-run config type contract or the rejected dict shape.
- Blockers or scope changes: None.

## Evaluator Review

- Findings:
  - No critical public example failure remained after re-verification; current quickstart and public beta smoke examples already pass.
  - Confirmed high documentation gap: `README.md`, `docs/site/guides/backtesting.md`, and `docs/site/reference/public-api.md` did not clearly state that direct `config=...` is a `StrategyConfig` instance, not a plain dict.
  - The patch is documentation-only and does not hide unsupported beta-scope gaps.
- Verification evidence:
  - Public-doc search for stale `config={...}`, `.selected()`, `closed_count`, and `strategy_parameters`: no current README/docs-site stale usage found.
  - Config contract probe: dict config rejected with `TypeError`; `Cfg(fast=3)` accepted and recorded `{'fast': 3}`.
  - `uv run python scripts/repo_check.py`: passed.
  - `uv run pytest tests/smoke/local -q`: 10 passed, 1 warning.
  - `uv run pytest tests/structure/docs/test_public_beta_docs.py tests/structure/docs/test_research_ergonomics_quickstart.py tests/structure/docs/test_reporting_config_source_of_truth_docs.py -q`: 15 passed.
- Final disposition: Accepted; confirmed high documentation clarity issue fixed, no confirmed critical defect remained.
