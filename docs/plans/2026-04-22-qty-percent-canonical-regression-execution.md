# Active Plan

- Date: `2026-04-22`
- Task: `Add canonical BTC regression contracts for qty_percent market and limit sizing`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  Add deterministic BTC-fixture-backed regression tests that lock shipped
  `qty_percent` market and limit behavior to checked-in result contracts.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the repo workflow, current backtest/research public contract,
    shipped `qty_percent` semantics, canonical verification expectations, and
    architecture boundaries for runtime-sensitive backtest behavior.
- In-repo scope:
  - Extend `tests/integration/research/test_order_sizing_contract.py` with
    BTC-fixture-backed `%` regressions for:
    - market-entry percent sizing
    - limit-entry percent sizing
    - limit-exit percent sizing
  - Keep the work test-only unless a new test exposes a real engine bug.
- Out-of-repo scope:
  - no production engine changes unless a test exposes a real bug
  - no external network or live-data verification
- Tier A progression requested: `no`
- Approval record, if required:
  - not required; this slice is test/support code only and stays outside Tier A
- Verification commands:
  - `uv run pytest tests/integration/research/test_order_sizing_contract.py -q`
  - `uv run pytest tests/integration/research -q`
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Success criteria:
  - The repo has checked-in BTC-fixture regression coverage for shipped
    `qty_percent` market and limit semantics.
  - New tests assert full summary contracts plus fill samples and trade-log
    digests, matching the existing canonical regression style.
  - Existing canonical RSI/EMA/MACD/limit tests remain intact.
  - Fresh runtime-sensitive verification passes.
- Out of scope:
  - replacing existing canonical RSI/EMA pair documentation
  - adding external-library cross-validation as a repo gate
  - new sizing semantics beyond shipped `qty_percent`

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close only when the new tests prove stable BTC-fixture-backed `%`
    regression coverage for market and limit paths without weakening the
    existing canonical suite.
- Acceptance artifact location:
  - `tests/integration/research/test_order_sizing_contract.py`
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - The slice is done when `%` market and limit behavior has deterministic
    canonical regression contracts using the checked-in BTC CSV and all fresh
    verification passes.
- Checks the evaluator will use:
  - compare added tests against the existing canonical regression pattern
  - confirm the chosen `%` strategies align with `order-sizing.md`
  - run the targeted test commands
  - run `uv run poe verify-runtime`
  - run `uv run poe repo-check`
- Auto-fail conditions:
  - new tests rely on ad hoc tiny fixtures instead of the checked-in BTC CSV
  - tests blur market and limit semantics so failures are hard to interpret
  - existing canonical regression coverage is silently rewritten instead of
    extended

## Generator Work Log

- Planned slice order:
  1. Add BTC-fixture `%` regression tests in the existing order-sizing contract
     file.
  2. Re-run the focused file and confirm the new regression contracts are
     stable.
  3. Widen to integration/runtime verification.
  4. Synthesize placement review and close.
- Notes:
  - Keep write ownership local.
  - Treat external-library cross-validation results as design evidence, not as
    repo authority.
- Blockers or scope changes:
  - Read-only placement review found that a new `test_canonical_percent_*`
    namespace would fight the repo's deliberately small canonical lane.
  - The slice was narrowed to extending
    `tests/integration/research/test_order_sizing_contract.py` with BTC-fixture
    `%` regressions instead of creating new canonical-percent files.

## Evaluator Review

- Findings:
  - No unresolved material findings.
  - One material placement issue was found during review and fixed before
    close:
    the first draft created a new `test_canonical_percent_*` family, but the
    repo's documented reliability model keeps the canonical lane small and
    routes additional deterministic sizing regressions into the normal
    integration suite.
  - Final test placement keeps:
    - existing canonical RSI/EMA/MACD/limit files untouched
    - `%` BTC-fixture regressions in the existing
      `tests/integration/research/test_order_sizing_contract.py`
  - Added BTC-fixture-backed `%` regressions:
    - market `%` sizing via RSI 30/70
    - limit-entry `%` sizing via EMA-based limit entry
    - limit-exit `%` sizing via RSI-based limit exit
- Verification evidence:
  - `uv run pytest tests/integration/research/test_order_sizing_contract.py -q`
    -> `8 passed in 0.87s`
  - `uv run pytest tests/integration/research -q`
    -> `41 passed in 2.13s`
  - `uv run poe repo-check`
    -> `repository checks passed`
  - `uv run poe verify-runtime`
    -> `ruff check .` passed
    -> `mypy src` passed
    -> `pytest -q` => `360 passed, 3 skipped`
    -> coverage policy check passed at `92%`
    -> `uv build` passed
    -> notebook validation passed for 4 notebooks
    -> perf check passed:
       `test_rsi_backtest_steady_state_median_is_within_threshold` median about
       `119.8ms`
- Final disposition:
  - `complete`
