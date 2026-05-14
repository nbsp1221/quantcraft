# WFA Real-Data Regression Test

- Date: 2026-05-15
- Task: Add a cheap real-data WFA integration regression test from the sweet
  spot experiment.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Add one default-lane WFA integration test that uses the checked-in BTC
  USD-M 1h 2025 fixture with the focused 12-candidate, 3-fold SMA + RSI setup
  found in the local sweet spot experiment.
- Governing docs:
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - `docs/PLANS.md`
  - `docs/product-specs/walk-forward-analysis-resume.md`
  - `docs/product-specs/walk-forward-analysis-resume-test-scenarios.md`
- Why these are governing: They define the repo workflow, verification lanes,
  WFA product contract, and WFA test contract.
- In-repo scope:
  - Add an integration test under `tests/integration/research/`.
  - Reuse the checked-in canonical BTC fixture through `tests/support_backtest.py`.
  - Keep the test cheap enough for the normal pytest lane.
- Out-of-repo scope: None.
- Tier A progression requested: `no`
- Approval record, if required: Not required; this is Tier B research/backtest
  test coverage only.
- Verification commands:
  - `uv run pytest tests/integration/research/test_walk_forward_real_data_contract.py -q`
  - `uv run pytest tests/integration/research/test_walk_forward_study.py tests/integration/research/test_walk_forward_records.py tests/integration/research/test_walk_forward_failures.py tests/integration/research/test_walk_forward_real_data_contract.py -q`
- Success criteria:
  - The new test uses the real 2025 BTC fixture.
  - The new test runs `WalkForwardStudy` through real `BacktestEngine`,
    `StrategyConfig`, indicators, `ParameterStudy`, and reporting paths.
  - The new test covers 3 folds, 12 valid candidates per fold, real OOS trades,
    mixed positive/negative OOS returns, and at least one open ending fold.
  - Targeted WFA integration tests pass.
- Out of scope:
  - Full 312-candidate WFA golden test.
  - New local affected-test tooling.
  - Production code changes.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Confirm the new test is cheap,
  fixture-backed, contract-focused, and passing with neighboring WFA integration
  tests.
- Acceptance artifact location: This plan's Evaluator Review section.
- How the generator and evaluator agreed on done before execution: The test is
  limited to the previously measured focused 12-candidate, 3-fold setup and
  must stay in the existing integration test surface.
- Checks the evaluator will use:
  - Inspect the test file for fixture use and WFA contract assertions.
  - Run the targeted new test.
  - Run neighboring WFA integration tests.
- Auto-fail conditions:
  - The test does not use the checked-in real fixture.
  - The test requires external network or `/tmp` artifacts.
  - The test adds production code or new dependencies.
  - The targeted test commands fail.

## Generator Work Log

- Planned slice order:
  1. Add the focused real-data WFA integration test.
  2. Run targeted verification.
  3. Record evaluator review evidence.
- Notes:
  - The focused setup comes from `/tmp/quantleet-wfa-sweetspot`:
    12 valid candidates, 3 folds, about 2 seconds in the experiment.
  - Added `tests/integration/research/test_walk_forward_real_data_contract.py`.
  - The test slices the checked-in 2025 BTC fixture from `2025-05-01` through
    `2025-10-27`, matching the focused sweet spot run.
  - The test asserts 3 successful folds, 18 raw candidates, 6 rejected
    candidates per fold, 12 valid candidates per fold, selected configs, OOS
    returns, OOS closed-trade counts, mixed positive/negative OOS returns, and
    one open ending fold.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings: No blocker findings. The new test is fixture-backed, deterministic,
  does not depend on `/tmp`, does not add dependencies, and stays in the
  existing integration pytest lane.
- Verification evidence:
  - `uv run pytest tests/integration/research/test_walk_forward_real_data_contract.py -q`
    - Result: `1 passed in 3.06s`
  - `uv run pytest tests/integration/research/test_walk_forward_study.py tests/integration/research/test_walk_forward_records.py tests/integration/research/test_walk_forward_failures.py tests/integration/research/test_walk_forward_real_data_contract.py -q`
    - Result: `9 passed in 3.34s`
- Final disposition: Complete for this slice.
