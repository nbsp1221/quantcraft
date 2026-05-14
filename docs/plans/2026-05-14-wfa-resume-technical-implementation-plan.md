# Walk-Forward Analysis Resume Technical Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to
> implement this plan task-by-task.

**Goal:** Implement the Stage 4 first-slice walk-forward validation workflow
defined by the WFA resume product and test specs.

**Architecture:** Add WFA as a research-layer study that composes the existing
`ParameterStudy` train-search path and the existing
`BacktestEngine.run(strategy=StrategyClass, config=...)` selected-test path.
Do not add another strategy construction model, execution engine, optimizer, or
continuous OOS account model.

**Tech Stack:** Python 3.13, stdlib dataclasses/statistics/math, strict mypy,
Ruff, pytest, `uv`, Poe, existing `quantleet.data`, `quantleet.strategy`,
`quantleet.backtest`, and `quantleet.research` contracts.

---

- Date: 2026-05-14
- Task: Stage 4 WFA implementation
- Status: `implemented`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Define exactly how to implement the Stage 4 WFA product and test
  specs in the current codebase without bypassing canonical research,
  strategy, data, or backtest paths.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/walk-forward-analysis-resume.md`
  - `docs/product-specs/walk-forward-analysis-resume-test-scenarios.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
  - `docs/product-specs/direct-backtest-class-config-api.md`
  - `docs/product-specs/direct-backtest-class-config-api-test-scenarios.md`
  - `docs/product-specs/strategy-configuration-contract.md`
  - `docs/product-specs/reporting-config-source-of-truth.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: WFA product/test specs define the feature contract;
  parameter exploration, direct-backtest, strategy config, and reporting specs
  define the canonical paths WFA must compose; architecture and reliability
  docs define package ownership, safety tier, and verification.
- In-repo scope:
  - add WFA implementation under `src/quantleet/research/`
  - export WFA public types from `quantleet.research`
  - add focused unit, integration, structure, smoke, and docs tests
  - add only Stage 4 public documentation/examples required by the specs
  - update this plan during implementation with work log, review findings, and
    verification evidence
- Out-of-repo scope: none.
- Tier A progression requested: `no`.
- Approval record, if required: not required; WFA is Tier B research/backtest
  work and must not change `trading` or `execution`.
- Verification commands:
  - focused tests listed in each implementation task
  - `uv run pytest tests/unit/research/test_walk_forward_windows.py tests/unit/research/test_walk_forward_preflight.py tests/unit/research/test_walk_forward_result_summary.py tests/unit/research/test_walk_forward_records.py tests/unit/research/test_walk_forward_diagnostics.py -q`
  - `uv run pytest tests/integration/research/test_walk_forward_study.py tests/integration/research/test_walk_forward_failures.py tests/integration/research/test_walk_forward_records.py -q`
  - `uv run pytest tests/smoke/local/test_public_imports.py tests/structure/architecture/test_walk_forward_boundaries.py tests/structure/docs/test_walk_forward_docs.py -q`
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run poe verify-runtime`
- Success criteria:
  - `WalkForwardStudy` runs the canonical rolling train/test WFA workflow on a
    materialized single-symbol `BarSeries`
  - train selection uses `ParameterStudy` only
  - selected OOS tests use `BacktestEngine.run(strategy=StrategyClass,
    config=...)` only
  - invalid inputs fail before any backtest starts
  - fold-level failures are recorded and later folds continue by default
  - no eligible training row produces no fabricated test result
  - successful folds retain train `GridSearchResult` and selected test
    `BacktestResult`
  - result records are portable, JSON-friendly, and pandas-independent
  - `oos_summary` summarizes independent test folds without stitched account
    semantics
  - diagnostics are factual and non-failing
  - public docs/examples stay within Stage 4 scope
  - full runtime verification passes
- Out of scope:
  - multi-symbol, multi-timeframe, portfolio, paper, live, short, leverage, or
    margin support
  - custom folds, calendar windows, timestamp windows, gaps, embargoes,
    anchored/expanding modes, or source-backed WFA input
  - callable objectives, string aliases, adaptive optimizers, random search,
    parallel execution, persistence, caching, resume queues, or memory-light
    mode
  - stitched OOS equity, `oos_report`, aggregate account return, or financial
    recommendation diagnostics
  - changes to backtest matching, order execution, trading kernel semantics, or
    `ParameterStudy` public behavior beyond narrow shared-helper extraction

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: confirm that the implementation
  follows this plan, product/test specs remain authoritative, no canonical path
  is bypassed, and fresh verification evidence is recorded before completion.
- Acceptance artifact location:
  `docs/plans/2026-05-14-wfa-resume-technical-implementation-plan.md`
- How the generator and evaluator agreed on done before execution: this plan
  names the governing docs, exact code paths, public field decisions, tests,
  verification commands, auto-fail conditions, and success criteria before code
  edits.
- Checks the evaluator will use:
  - inspect diff against product spec, test spec, and this plan
  - run the focused WFA tests
  - run structure and smoke tests covering public imports and boundaries
  - run `uv run poe verify-runtime`
  - obtain third-party subagent review before final completion
- Auto-fail conditions:
  - WFA does not live under `quantleet.research`
  - WFA creates a second strategy construction model or accepts strategy
    instances/callable factories
  - WFA bypasses `ParameterStudy` for train search or bypasses
    `BacktestEngine.run(strategy=..., config=...)` for selected OOS tests
  - invalid preflight input starts any train or test backtest
  - failed or unselected folds fabricate selected test results or numeric OOS
    aggregates
  - result records emit non-standard JSON floats, raw exception objects,
    tracebacks, or top-level user config key collisions
  - public docs imply stitched OOS account semantics, trading advice, source
    input, aliases/callables, or unsupported Stage 4 modes
  - runtime verification is skipped

## Implementation Goal

Implement a first-slice WFA workflow that answers:

> Did parameters selected on each training window survive the next unseen test
> window?

The implementation should make this validation evidence inspectable without
claiming optimization, tradability, or future performance.

## Implementation Scope And Non-Scope

In scope:

- public `quantleet.research.WalkForwardStudy`
- public result dataclasses:
  - `WalkForwardResult`
  - `WalkForwardFold`
  - `WalkForwardDiagnostic`
  - `WalkForwardOosSummary`
  - `WalkForwardExecutionScale`
- rolling bar-count folds only
- materialized `BarSeries` only
- finite parameter grids compatible with `ParameterStudy`
- objective tuple syntax only
- mapping-based constraints that receive materialized `strategy_config`
- per-fold train `GridSearchResult` retention
- per-fold selected test `BacktestResult` retention when successful
- independent-fold OOS summary and factual diagnostics
- fold-level and train-candidate record export
- default unlimited WFA total-run cap plus optional explicit total-run cap
- inherited per-fold `ParameterStudy.max_candidates` guardrail

Non-scope matches the product spec non-goals and must not be implemented as
hidden extras.

## Codebase Survey

### Current Project Structure

- `src/quantleet/data/`
  - owns `TimeBar`, `BarSeries`, and historical source adapters
  - WFA should accept `BarSeries` and slice it by `rows`
- `src/quantleet/strategy/`
  - owns `Strategy`, `StrategyConfig`, config validation, config snapshots, and
    strategy runtime authoring contracts
  - WFA should validate strategy class shape through the same expectations as
    `ParameterStudy` and `BacktestEngine`
- `src/quantleet/backtest/`
  - owns `BacktestEngine`, result/report objects, and historical execution
  - WFA should compose this public surface for selected OOS tests
- `src/quantleet/research/`
  - owns research ergonomics, indicators, QC helpers, and `ParameterStudy`
  - WFA belongs here as another research study
- `tests/unit`, `tests/integration`, `tests/structure`, `tests/smoke/local`
  - already separate behavior level, integration contract, architecture/docs,
    and import smoke checks

### Related Modules And Files

- `src/quantleet/research/parameter_exploration.py`
  - `ParameterStudy` is the canonical finite-grid train search path
  - `GridSearchResult.best()` and `.top()` are the canonical objective-based
    selection helpers
  - `GridSearchRow.strategy_config` is the materialized config snapshot WFA
    should pass into selected tests
  - `GridSearchResult.to_records()` defines the existing portable
    pandas-independent row export style
  - `_METRIC_EXTRACTORS`, `_METRIC_KEYS`, `_validate_objective`,
    `_validate_parameter_grid`, `_candidate_count`, `_validate_max_candidates`,
    `_normalize_metrics`, and `_normalize_metric` are reusable mechanics
- `src/quantleet/backtest/engine.py`
  - `BacktestEngine.run(...)` is the canonical selected-test execution path
  - `_materialize_strategy(...)` enforces strategy class plus config
  - `_BacktestStrategyConstructionError` wraps direct construction failures
- `src/quantleet/backtest/results.py`
  - `BacktestResult` retains report, trade log, equity curve, and plot support
  - WFA should retain selected test results but must not stitch them into a
    continuous account
- `src/quantleet/backtest/reporting.py`
  - `BacktestReport` exposes the metrics used by `ParameterStudy`
  - `RunManifest.strategy_config` is the reporting source of truth for config
    snapshots
- `src/quantleet/data/bars.py`
  - `TimeBar.timestamp` is an `int`
  - `BarSeries.rows` is a tuple of `TimeBar`
  - `BarSeries` currently validates metadata and row type, not chronological
    uniqueness
- `src/quantleet/research/__init__.py`
  - lazy public export surface for research types
  - WFA public types should be added here

### Existing Architecture And Design Patterns

- Capability-first package ownership: WFA belongs in `research`, not
  `backtest`, `strategy`, `trading`, or `execution`.
- Public workflow objects are small dataclasses or classes with explicit
  validated constructor arguments.
- Research workflows compose backtest/strategy/data contracts instead of
  redefining execution semantics.
- Result objects are immutable dataclasses where possible and expose
  query/export helpers such as `to_records()`.
- Validation errors use built-in `TypeError` and `ValueError` for public call
  shape and input value issues; no new public exception hierarchy is required.
- Tests prefer public behavior, deterministic tiny fixtures, and focused
  integration coverage over private-helper assertions.

### Existing Canonical Paths

Use these paths; do not replace them:

- Train search:
  `ParameterStudy(engine=engine, bars=train_bars, strategy=StrategyClass).grid_search(...)`
- Train selection:
  `GridSearchResult.best(objective)` or `top(1, objective=objective)`
- Selected test execution:
  `engine.run(bars=test_bars, strategy=StrategyClass, config=SelectedConfig)`
- Config materialization:
  `StrategyClass.config_type(**candidate)` through `ParameterStudy`
- Report config snapshot:
  `BacktestResult.report.run.strategy_config`
- Metric extraction and metric-state vocabulary:
  existing `ParameterStudy` metric extractors and state strings
- Portable train-candidate records:
  `GridSearchResult.to_records()`

### Reusable Functions, Types, And Test Utilities

Implementation can reuse:

- `BarSeries` and `TimeBar`
- `Strategy`, `StrategyConfig`, `StrategyConfigValidationError`
- `BacktestEngine`, `BacktestResult`, `_BacktestStrategyConstructionError`
- `ParameterStudy`, `GridSearchResult`, `GridSearchRow`
- `JSONScalar`, `Objective`, `MetricState`, `MetricValue`, `Constraint`
- metric extraction and normalization logic currently inside
  `parameter_exploration.py`
- test fixtures from `tests/unit/research/support_parameter_study.py`:
  `make_bars`, `make_engine`, `CountingEngine`, `NoTradeStrategy`,
  `RoundTripStrategy`
- integration fixture patterns from
  `tests/integration/research/test_parameter_study_grid_search.py`
- public import assertions in `tests/smoke/local/test_public_imports.py`
- architecture AST-import pattern from
  `tests/structure/architecture/test_parameter_exploration_boundaries.py`

Recommended small refactor before WFA implementation:

- move shared research-study mechanics from `parameter_exploration.py` to a
  private module `src/quantleet/research/_study_metrics.py`
- expose only internal names there:
  - `JSONScalar`
  - `Objective`
  - `MetricState`
  - `MetricValue`
  - `Constraint`
  - `METRIC_EXTRACTORS`
  - `METRIC_KEYS`
  - `UNDEFINED_METRIC_STATES`
  - `validate_objective`
  - `extract_metrics`
  - `normalize_metrics`
  - `normalize_metric`
- keep public exports unchanged
- update `parameter_exploration.py` to import these internals

This avoids duplicating metric/objective rules in WFA while keeping the public
API small.

### Existing Test Ways And Verification Commands

- Unit tests: `tests/unit/...`, run with `uv run poe test-unit` or targeted
  `uv run pytest ... -q`
- Integration tests: `tests/integration/...`
- Structure tests: `tests/structure/...`
- Smoke tests: `tests/smoke/local/...`
- Full default verification: `uv run poe verify`
- Runtime-sensitive verification: `uv run poe verify-runtime`

Because WFA touches `src/quantleet/research` and composes the runtime-sensitive
backtest path, final implementation verification must include
`uv run poe verify-runtime`.

### Impacted Areas

- Public research imports may change by adding new names; root package should
  remain unchanged.
- Research tests will grow substantially.
- Structure docs/import tests should gain WFA-specific boundary checks.
- Public docs/examples may need a small WFA example after implementation.
- `parameter_exploration.py` may change only for shared-helper extraction; its
  public behavior must remain unchanged.

### Existing Paths Not To Bypass Or Duplicate

- Do not manually rank train candidates by reaching around `GridSearchResult`
  when `best()`/`top()` already provide objective selection.
- Do not call private backtest runtime functions from WFA.
- Do not instantiate strategies directly in WFA for selected tests.
- Do not copy metric extractors into WFA.
- Do not introduce a `BacktestEngine.optimize(...)` or WFA method on
  `BacktestEngine`.
- Do not add WFA imports from `backtest`, `trading`, or `execution`.
- Do not add pandas as a canonical result dependency.

## Public API And Field Decisions

These are implementation-detail decisions, not product-scope changes.

- Public module exposure:
  - `from quantleet.research import WalkForwardStudy`
  - `WalkForwardResult`, `WalkForwardFold`, `WalkForwardDiagnostic`,
    `WalkForwardOosSummary`, and `WalkForwardExecutionScale` are also exported
    from `quantleet.research`
- Implementation file:
  - create `src/quantleet/research/walk_forward.py`
- `WalkForwardStudy.__init__`:
  ```python
  WalkForwardStudy(
      *,
      engine: object,
      bars: BarSeries,
      strategy: type[Strategy[StrategyConfig]],
  )
  ```
- `WalkForwardStudy.run`:
  ```python
  def run(
      self,
      *,
      parameters: Mapping[str, Sequence[JSONScalar]],
      objective: Objective,
      constraint: Constraint | None = None,
      train_size: int,
      test_size: int,
      step_size: int | None = None,
      mode: Literal["rolling"] = "rolling",
      max_candidates: int | None = 1000,
      max_total_runs: int | None = None,
  ) -> WalkForwardResult:
      ...
  ```
- Timestamps in public records remain `int`, matching `TimeBar.timestamp` and
  `BacktestReport`.
- No-trade diagnostic severity is `info` because a technically valid WFA fold
  can legitimately have no closed trades; it should be visible but not framed
  like an execution failure.
- Stable diagnostic codes:
  - `fold_execution_failed`
  - `no_selected_config`
  - `undefined_oos_objective`
  - `no_closed_trades`
  - `zero_successful_oos_folds`

## Data Flow And Control Flow

1. `WalkForwardStudy.__init__` validates:
   - `engine` has callable `run`
   - `bars` is a non-empty `BarSeries`
   - `strategy` is a `Strategy` subclass
2. `run(...)` preflights all cheap contracts before any backtest:
   - objective tuple via shared `validate_objective`
   - parameter grid shape via existing/shared parameter-grid validation
   - WFA-specific rule that empty parameter mapping is invalid
   - parameter names via `strategy.config_type.validate_override_names`
   - `train_size`, `test_size`, `step_size`, and `mode`
   - chronological bars: strictly increasing unique timestamps
   - at least one complete rolling fold
   - raw candidates per fold against `max_candidates`
   - planned total runs against optional `max_total_runs`
3. Fold generation creates immutable fold windows:
   - `train_start`, `train_end`, `test_start`, `test_end`
   - indexes are start-inclusive/end-exclusive
   - timestamp fields use first/last observed bar timestamps from each slice
4. For each fold:
   - construct train/test `BarSeries` slices preserving metadata
   - run `ParameterStudy(...).grid_search(..., fail_fast=False)`
   - select `best` eligible row using the objective
   - materialize selected config with `strategy.config_type(**dict(row.candidate_parameters))`
   - run selected test through `engine.run(bars=test_bars, strategy=strategy,
     config=selected_config, label=f"walk-forward-fold-{fold_index}-test")`
   - extract selected test metrics through shared metric extraction
   - record `status="success"` or structured failure
5. After all folds:
   - compute counts and `oos_summary` from successful selected test folds only
   - generate factual diagnostics
   - return `WalkForwardResult`

## Result Model

Create frozen, slotted dataclasses unless mutation is needed.

`WalkForwardExecutionScale`:

- `fold_count: int`
- `raw_candidate_count_per_fold: int`
- `planned_train_candidate_runs: int`
- `planned_selected_test_runs: int`
- `planned_total_runs: int`
- `max_candidates: int | None`
- `max_total_runs: int | None`

`WalkForwardFold`:

- `fold_index: int`
- `status: Literal["success", "failed"]`
- train/test positional and timestamp boundaries
- `train_result: GridSearchResult | None`
- `selected_train_row: GridSearchRow | None`
- `selected_config: Mapping[str, JSONScalar] | None`
- `selected_test_result: BacktestResult | None`
- `train_metrics: Mapping[str, MetricValue]`
- `train_metric_states: Mapping[str, MetricState]`
- `test_metrics: Mapping[str, MetricValue]`
- `test_metric_states: Mapping[str, MetricState]`
- `failure_stage: Literal["train_search", "selection", "test_strategy_construction",
  "test_backtest", "test_metric_extraction"] | None`
- `error_type: str | None`
- `error_message: str | None`

`WalkForwardOosSummary`:

- counts: `fold_count`, `successful_fold_count`, `failed_fold_count`,
  `failure_rate`
- objective: `objective_metric_path`, `objective_direction`
- objective metric states: counts by metric state
- numeric objective aggregates over successful selected test folds with
  defined finite values: `mean`, `median`, `min`, `max`
- `positive_fold_ratio` for `returns.total_return` when finite successful
  return values exist
- no aggregate equity, final account, stitched return, or continuous account
  fields

`WalkForwardDiagnostic`:

- `severity: Literal["info", "warning"]`
- `code: Literal[...]`
- `message: str`
- `fold_indexes: tuple[int, ...]`

`WalkForwardResult`:

- `folds: tuple[WalkForwardFold, ...]`
- `objective: Objective`
- `execution_scale: WalkForwardExecutionScale`
- `oos_summary: WalkForwardOosSummary`
- `diagnostics: tuple[WalkForwardDiagnostic, ...]`
- count properties: `fold_count`, `successful_fold_count`,
  `failed_fold_count`
- `to_records() -> list[dict[str, object]]`
- `to_candidate_records() -> list[dict[str, object]]`

## Record Export Design

Fold records must keep top-level metadata and metrics flat, but keep config
snapshots nested:

- top-level:
  - `fold_index`
  - train/test positional boundaries
  - train/test first/last timestamps
  - `objective_metric_path`
  - `objective_direction`
  - `train_status`
  - `test_status`
  - `status`
  - `failure_stage`
  - `error_type`
  - `error_message`
- nested:
  - `selected_config`
- metrics:
  - selected train metric keys prefixed with `train.`
  - selected test metric keys prefixed with `test.`
  - metric-state keys suffixed with `_state`

Candidate records should be built from each fold's
`train_result.to_records()` and add `fold_index` plus fold boundary fields.
This reuses the existing `GridSearchResult` portable record contract instead
of inventing a second candidate export shape.

When metric state is not `defined`, public records should emit the metric value
as `None` and expose the state separately. This matches the current
`ParameterStudy.to_records()` behavior and avoids non-standard JSON float
tokens.

## Architecture And Pattern Rationale

- WFA as `research/walk_forward.py` follows capability-first ownership:
  research owns validation studies, backtest owns execution, strategy owns
  construction/config, and data owns bar contracts.
- Composition over inheritance keeps WFA from becoming a backtest engine or a
  second optimizer.
- Frozen dataclasses make result objects easy to inspect and stable for tests.
- A small private shared metric module avoids duplicating objective and metric
  state logic while keeping public API unchanged.
- Built-in `TypeError`/`ValueError` follows `ParameterStudy` and direct
  backtest conventions.
- Sequential execution is deliberate; parallelism would add scheduling,
  ordering, and failure semantics outside Stage 4.

## Test Implementation Plan

### Unit Tests

Create:

- `tests/unit/research/test_walk_forward_windows.py`
  - one fold, multiple folds, explicit step, exact boundary, insufficient bars
  - start-inclusive/end-exclusive indexes and timestamp boundaries
  - rolling-only mode rejection
- `tests/unit/research/test_walk_forward_preflight.py`
  - invalid bars, empty bars, duplicate/out-of-order timestamps
  - invalid size types and values
  - invalid strategy, strategy instance, callable factory, invalid engine
  - malformed parameter grids, empty mapping, empty value list, unknown fields
  - invalid objective aliases/callables/directions/paths
  - no-run assertions via `CountingEngine`
  - explicit total cap and inherited per-fold `max_candidates`
- `tests/unit/research/test_walk_forward_result_summary.py`
  - success/failure counts
  - objective aggregate fields from successful selected test folds only
  - failed folds excluded from numeric aggregates
  - zero-success summary exposes counts/failure rate only
  - no stitched account fields
- `tests/unit/research/test_walk_forward_records.py`
  - fold record shape for success and failure
  - nested `selected_config`
  - metric-state fields and JSON-safe output
  - candidate records include `fold_index` and reuse train records
- `tests/unit/research/test_walk_forward_diagnostics.py`
  - required diagnostic codes and severities
  - no closed trades emits `info`
  - diagnostics do not fail valid runs

### Integration Tests

Create:

- `tests/integration/research/test_walk_forward_study.py`
  - canonical real WFA workflow with real `BarSeries`,
    `BacktestEngine`, `StrategyConfig`, `ParameterStudy`, and strategy class
  - train/test separation and selected config flow
  - retained `GridSearchResult` and selected `BacktestResult`
  - fresh strategy state across candidates/folds
- `tests/integration/research/test_walk_forward_failures.py`
  - candidate failure while fold succeeds with another eligible row
  - no eligible training row
  - selected test failure with continuation
  - undefined objective metric handling
  - zero successful OOS folds
- `tests/integration/research/test_walk_forward_records.py`
  - real fold and candidate records are portable and joinable
  - records serialize with `json.dumps(..., allow_nan=False)`

### Smoke And Structure Tests

Modify:

- `tests/smoke/local/test_public_imports.py`
  - assert `WalkForwardStudy` and result/diagnostic types are available from
    `quantleet.research`

Create:

- `tests/structure/architecture/test_walk_forward_boundaries.py`
  - WFA implementation lives under `src/quantleet/research`
  - `backtest`, `trading`, and `execution` do not import WFA
  - `BacktestEngine` does not gain WFA/optimizer methods
  - WFA signature omits deferred controls such as `source`, parallel workers,
    custom fold objects, and callable objectives
- `tests/structure/docs/test_walk_forward_docs.py`
  - docs/examples do not show unsupported Stage 4 behavior
  - docs avoid `oos_report`, stitched OOS equity, trading recommendation
    claims, source input, aliases, and callable objectives

## Migration And Compatibility Considerations

- This is pre-beta Stage 4 planning; no legacy WFA API exists.
- Adding public names to `quantleet.research` is additive.
- Existing `ParameterStudy` public behavior must remain compatible. If shared
  helper extraction changes it, existing parameter exploration tests must catch
  regressions.
- No changes should be made to root `quantleet` exports.
- No new runtime dependencies are required.
- No persistence or data migration is needed.

## Risks And Responses

- Risk: WFA accidentally duplicates `ParameterStudy` candidate handling.
  - Response: extract/share metric/objective helpers only; call
    `ParameterStudy.grid_search(...)` for train search.
- Risk: WFA preflight misses an invalid input and starts partial backtests.
  - Response: use `CountingEngine` no-run tests for every strict preflight
    class.
- Risk: OOS summary looks like a continuous account.
  - Response: summary type has only independent-fold counts and metric
    distributions; structure/docs tests forbid stitched account terms.
- Risk: selected config cannot be reconstructed safely from a `GridSearchRow`.
  - Response: use `strategy.config_type(**dict(selected_row.candidate_parameters))`
    and assert selected test report config equals `selected_row.strategy_config`.
- Risk: private helper extraction causes parameter exploration regression.
  - Response: run existing parameter exploration unit/integration tests after
    extraction and before WFA logic.
- Risk: full result retention can use significant memory on large studies.
  - Response: preserve the product decision; expose planned execution scale
    and optional `max_total_runs` preflight cap.
- Risk: timestamp representation becomes ambiguous.
  - Response: keep integer timestamps exactly as `TimeBar` and
    `BacktestReport` already expose them.

## Implementation Order

### Task 1: Extract Shared Research Metric Helpers

**Files:**

- Create: `src/quantleet/research/_study_metrics.py`
- Modify: `src/quantleet/research/parameter_exploration.py`
- Test: existing parameter exploration tests

Steps:

1. Move metric/objective type aliases, extractor mapping, objective
   validation, metric extraction, and metric normalization into
   `_study_metrics.py`.
2. Import those helpers from `parameter_exploration.py`.
3. Keep `parameter_exploration.__all__` unchanged.
4. Run:
   `uv run pytest tests/unit/research/test_parameter_grid_validation.py tests/unit/research/test_grid_search_result_selection.py tests/unit/research/test_grid_search_records.py tests/integration/research/test_parameter_study_grid_search.py tests/integration/research/test_parameter_study_failures.py -q`

### Task 2: Add WFA Window And Preflight Skeleton

**Files:**

- Create: `src/quantleet/research/walk_forward.py`
- Create: `tests/unit/research/test_walk_forward_windows.py`
- Create: `tests/unit/research/test_walk_forward_preflight.py`

Steps:

1. Write failing window/preflight tests.
2. Implement `WalkForwardStudy.__init__`, `run(...)` input validation,
   fold generation, and `WalkForwardExecutionScale`.
3. Ensure strict preflight failures happen before engine calls.
4. Run:
   `uv run pytest tests/unit/research/test_walk_forward_windows.py tests/unit/research/test_walk_forward_preflight.py -q`

### Task 3: Add Fold Execution And Result Objects

**Files:**

- Modify: `src/quantleet/research/walk_forward.py`
- Create: `tests/integration/research/test_walk_forward_study.py`
- Create: `tests/integration/research/test_walk_forward_failures.py`

Steps:

1. Write failing integration tests for canonical workflow and fold failure
   continuation.
2. Implement `WalkForwardFold` and `WalkForwardResult`.
3. Execute each fold through `ParameterStudy` and selected tests through
   `BacktestEngine.run(...)`.
4. Record fold failures without aborting later folds.
5. Run:
   `uv run pytest tests/integration/research/test_walk_forward_study.py tests/integration/research/test_walk_forward_failures.py -q`

### Task 4: Add OOS Summary And Diagnostics

**Files:**

- Modify: `src/quantleet/research/walk_forward.py`
- Create: `tests/unit/research/test_walk_forward_result_summary.py`
- Create: `tests/unit/research/test_walk_forward_diagnostics.py`

Steps:

1. Write failing summary and diagnostic tests.
2. Implement `WalkForwardOosSummary`.
3. Implement `WalkForwardDiagnostic` and required diagnostic codes.
4. Ensure no-threshold diagnostics only.
5. Run:
   `uv run pytest tests/unit/research/test_walk_forward_result_summary.py tests/unit/research/test_walk_forward_diagnostics.py -q`

### Task 5: Add Record Exports

**Files:**

- Modify: `src/quantleet/research/walk_forward.py`
- Create: `tests/unit/research/test_walk_forward_records.py`
- Create: `tests/integration/research/test_walk_forward_records.py`

Steps:

1. Write failing record-shape tests.
2. Implement `WalkForwardResult.to_records()`.
3. Implement `WalkForwardResult.to_candidate_records()` by extending retained
   `GridSearchResult.to_records()` rows with fold metadata.
4. Verify JSON-safe record output.
5. Run:
   `uv run pytest tests/unit/research/test_walk_forward_records.py tests/integration/research/test_walk_forward_records.py -q`

### Task 6: Export Public Surface

**Files:**

- Modify: `src/quantleet/research/__init__.py`
- Modify: `tests/smoke/local/test_public_imports.py`
- Create: `tests/structure/architecture/test_walk_forward_boundaries.py`

Steps:

1. Add lazy exports for WFA public types.
2. Add smoke import assertions.
3. Add boundary assertions.
4. Run:
   `uv run pytest tests/smoke/local/test_public_imports.py tests/structure/architecture/test_walk_forward_boundaries.py -q`

### Task 7: Add Minimal Public Docs Contract Checks

**Files:**

- Modify: relevant public docs or examples only if the implementation is ready
  to expose WFA in docs
- Create: `tests/structure/docs/test_walk_forward_docs.py`

Steps:

1. Add or update public docs with a small Stage 4 WFA example only if the
   implementation surface is stable.
2. Add docs structure tests forbidding unsupported WFA patterns.
3. Run:
   `uv run pytest tests/structure/docs/test_walk_forward_docs.py -q`

### Task 8: Final Verification And Review

**Files:**

- Modify: this plan with evaluator work log, review findings, and verification
  evidence

Steps:

1. Run all focused WFA tests.
2. Run `uv run ruff check .`.
3. Run `uv run mypy src`.
4. Run `uv run poe verify-runtime`.
5. Request third-party subagent review against product spec, test spec, and
   this plan.
6. Fix blocker/important review findings.
7. Rerun relevant focused tests and `uv run poe verify-runtime`.
8. Record final evaluator disposition in this plan.

## Success Conditions

Implementation is complete only when:

- all product-spec core requirements are implemented
- all P0 and P1 test-spec scenarios have direct or equivalent coverage
- any scenario not implemented exactly has an equivalent verification and a
  documented reason
- no unsupported Stage 4 behavior appears in public docs or API examples
- focused tests pass
- `uv run poe verify-runtime` passes
- third-party review finds no remaining blocker or important issues

## Human Confirmation Needed

No product-scope human questions remain before implementation.

The implementation plan closes the remaining technical details as follows:

- public export surface: `quantleet.research`
- timestamp record representation: integer timestamps
- diagnostic codes: snake-case stable strings listed above
- no-closed-trades severity: `info`
- result retention and total-run cap: full retention, no default total cap,
  optional explicit `max_total_runs`

If later implementation discovers a conflict that would change product scope,
pause and bring that specific question back to the user.

## Generator Work Log

- Planned slice order:
  1. Read WFA product/test specs and related governing docs. Completed.
  2. Survey codebase structure, canonical paths, reusable helpers, tests, and
     verification commands. Completed.
  3. Write technical implementation plan. Completed.
  4. Extract shared research metric helpers. Completed.
  5. Implement WFA public workflow, result models, records, diagnostics, and
     public exports. Completed.
  6. Add unit, integration, smoke, structure, and docs contract tests.
     Completed.
  7. Request third-party subagent review and address blocker/important
     findings. Completed.
  8. Run final runtime verification and record evaluator disposition.
     Completed.
- Notes:
  - Implementation is proceeding from the approved product, test, and
    technical implementation specs.
  - The plan deliberately keeps WFA in `research` and keeps `backtest`,
    `trading`, and `execution` free of WFA ownership.
  - Anthropic long-running harness principles applied: this plan is the
    durable sprint contract, Codex is the generator, read-only subagents are
    used for bounded scouting/review, and review findings are routed back into
    implementation before final disposition.
  - Focused verification so far:
    - `uv run pytest tests/unit/research/test_parameter_grid_validation.py tests/unit/research/test_grid_search_result_selection.py tests/unit/research/test_grid_search_records.py tests/integration/research/test_parameter_study_grid_search.py tests/integration/research/test_parameter_study_failures.py -q`
      passed: 51 tests.
    - `uv run pytest tests/unit/research/test_walk_forward_windows.py tests/unit/research/test_walk_forward_preflight.py tests/unit/research/test_walk_forward_result_summary.py tests/unit/research/test_walk_forward_records.py tests/unit/research/test_walk_forward_diagnostics.py tests/integration/research/test_walk_forward_study.py tests/integration/research/test_walk_forward_failures.py tests/integration/research/test_walk_forward_records.py tests/smoke/local/test_public_imports.py tests/structure/architecture/test_walk_forward_boundaries.py tests/structure/docs/test_walk_forward_docs.py -q`
      passed: 43 tests after review fixes.
    - `uv run pytest tests/integration/research/test_walk_forward_failures.py -q`
      passed: 3 tests after adding rejected-candidate fold continuation
      coverage.
    - `uv run ruff check .` passed.
    - `uv run mypy src` passed.
    - `uv run pytest tests/structure/architecture/test_backtest_mvp_slice1.py tests/smoke/local/test_public_imports.py tests/structure/architecture/test_walk_forward_boundaries.py -q`
      passed: 15 tests after updating the historical Slice 1 public-surface
      check for additive Stage 4 research exports.
    - `uv run poe verify-runtime` passed: ruff, mypy, pytest
      (`737 passed, 4 skipped`), coverage policy, build, repo-check,
      notebook validation, and perf tests all completed successfully.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - Initial third-party review found blocker/important gaps in test coverage
    and important product/architecture mismatches: incomplete no-run preflight
    coverage, missing failed-record export coverage, under-asserted OOS
    summary semantics, private backtest exception dependency, stale
    `test_construction` failure-stage naming, missing result-level window
    metadata, and missing per-metric summary `count`.
  - All blocker and important findings were addressed. Follow-up review found
    no remaining blocker/important architecture findings and no remaining
    blocker/important test-quality findings. A final product-contract follow-up
    identified result-level `mode`, `train_size`, `test_size`, and resolved
    `step_size` metadata plus a stale plan stage name; both were fixed before
    final verification.
  - WFA remains under `quantleet.research`, composes `ParameterStudy` and
    `BacktestEngine.run(strategy=..., config=...)`, and does not introduce a
    second strategy construction or execution path.
- Verification evidence:
  - `uv run pytest tests/unit/research/test_walk_forward_windows.py tests/unit/research/test_walk_forward_preflight.py tests/unit/research/test_walk_forward_result_summary.py tests/unit/research/test_walk_forward_records.py tests/unit/research/test_walk_forward_diagnostics.py tests/integration/research/test_walk_forward_study.py tests/integration/research/test_walk_forward_failures.py tests/integration/research/test_walk_forward_records.py tests/smoke/local/test_public_imports.py tests/structure/architecture/test_walk_forward_boundaries.py tests/structure/docs/test_walk_forward_docs.py -q`
    passed: 43 tests.
  - `uv run pytest tests/structure/architecture/test_backtest_mvp_slice1.py tests/smoke/local/test_public_imports.py tests/structure/architecture/test_walk_forward_boundaries.py -q`
    passed: 15 tests.
  - `uv run poe verify-runtime` passed: ruff, mypy, full pytest
    (`737 passed, 4 skipped`), coverage policy, build, repo-check, notebook
    validation, and perf tests.
- Final disposition:
  - Complete for Stage 4 WFA implementation. Product spec, test spec, and
    technical implementation plan success conditions are satisfied with fresh
    verification evidence and third-party review closure.
