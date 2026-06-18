# Reporting Config Source Of Truth Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace report-facing strategy self-reported parameters with
`StrategyConfig` snapshots, so `report.run.strategy_config` is the single
execution-config truth for direct backtests and retained `ParameterStudy`
backtests.

**Architecture:** Keep `StrategyConfig` ownership in `quantcraft.strategy`,
historical report construction in `quantcraft.backtest`, and study composition in
`quantcraft.research`. The implementation reuses `StrategyConfig.to_mapping()`
as the only snapshot source and removes the old `Strategy.parameters()` report
path instead of adding an adapter, alias, or compatibility layer.

**Tech Stack:** Python 3.13, dataclasses, pytest, mypy strict mode, Ruff,
Poe/uv repository verification, existing Quantcraft `Strategy`, `StrategyConfig`,
`BacktestEngine`, `BacktestReport`, and `ParameterStudy` surfaces.

---

- Date: 2026-05-10
- Task: Reporting Config Source Of Truth implementation plan
- Status: `completed`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Simplification Pass

- Date: 2026-05-10
- Requestor: retn0
- Scope:
  - Behavior-preserving cleanup in files already changed by this slice.
  - No public contract, product behavior, or verification scope expansion.
- Success criteria:
  - `BacktestEngine.run(...)` keeps the same validation and snapshot behavior
    with a smaller local reasoning surface.
  - Reporting contract tests keep the same assertions while reducing repeated
    engine setup noise.
- Verification:
  - Run the smallest targeted tests that cover touched runtime and reporting
    contract behavior after edits.
- Result:
  - `BacktestEngine.run(...)` now selects and validates run bars once before
    delegating to `_run_backtest(...)`, preserving the run-start config
    snapshot and source/bars validation behavior.
  - Reporting contract tests now use a local `_engine()` helper for repeated
    default-engine setup, keeping assertions focused on report behavior.
  - Verification passed:
    `uv run pytest tests/integration/research/test_backtest_result_reporting_contract.py tests/unit/backtest/test_strategy_like_report_config_validation.py -q`
    (`10 passed`), `uv run ruff check src/quantcraft/backtest/engine.py tests/integration/research/test_backtest_result_reporting_contract.py`,
    `uv run mypy src`, `git diff --check`, and
    `uv run poe verify-runtime` (`693 passed, 4 skipped`, coverage policy
    passed, build/repo/notebook/perf checks passed).

## Planner Contract

- Goal: Define how to implement Stage 3 reporting provenance cleanup in the
  current codebase.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/reporting-config-source-of-truth.md`
  - `docs/product-specs/reporting-config-source-of-truth-test-scenarios.md`
  - `docs/product-specs/strategy-configuration-contract.md`
  - `docs/product-specs/strategy-configuration-contract-test-scenarios.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - The Stage 3 product and test specs define the required external contract.
  - Strategy configuration specs define `StrategyConfig.to_mapping()` and
    materialized immutable snapshots.
  - Parameter exploration specs define `candidate_parameters` versus
    `strategy_config` vocabulary.
  - Backtest and research specs define the current beta result/report and study
    surfaces.
  - Architecture docs define capability ownership and dependency rules.
  - Reliability docs require runtime-sensitive verification for backtest and
    research changes.
- In-repo scope:
  - Source changes under `src/quantcraft/strategy`, `src/quantcraft/backtest`,
    and current `src/quantcraft/research` call sites only as required by the
    Stage 3 contract.
  - Tests under existing `tests/unit`, `tests/integration`, `tests/structure`,
    and `tests/smoke/local` taxonomy.
  - Managed current docs under `README.md`, `docs/site`, and current governing
    product/test specs where they present current guidance.
  - Managed fixtures including canonical report snapshots.
  - Tracked notebooks only if inspection shows current runnable strategy
    examples need migration.
- Out-of-repo scope: none.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is Tier B strategy,
  backtest, and research cleanup; it must not change `trading` or `execution`
  behavior.
- Verification commands:
  - Targeted red/green commands listed in the implementation tasks.
  - `uv run poe test-unit`
  - `uv run poe test-integration`
  - `uv run poe test-structure`
  - `uv run poe test-smoke`
  - `uv run poe notebook-validate`
  - `uv run poe verify-runtime`
  - `uv run poe verify`
  - `git diff --check`
- Success criteria:
  - `BacktestReport.run` exposes `strategy_config` and no longer exposes
    `strategy_parameters`.
  - Report construction never calls `Strategy.parameters()`.
  - Base `Strategy` no longer defines `parameters()` as canonical API.
  - User-defined `parameters()` methods may still exist on user classes but are
    ignored by reporting.
  - Official config-less `Strategy` subclasses report `strategy_config == {}`.
  - Custom strategy-like objects without valid `StrategyConfig` metadata fail
    with an explicit validation error, not a raw missing-attribute error and
    not a silent `{}` fallback.
  - Successful `ParameterStudy` rows and their retained backtest reports expose
    identical full `strategy_config` snapshots.
  - Managed current docs, examples, tests, fixtures, and notebooks no longer
    teach the old report contract.
  - Historical/audit references are not rewritten merely to erase history.
- Out of scope:
  - WFA implementation or WFA result shape.
  - Paper/live trading behavior.
  - Direct `BacktestEngine.run(strategy=StrategyClass, config=...)` API
    implementation.
  - Removal or redesign of instance-based `BacktestEngine.run(...)`.
  - Arbitrary run metadata bags.
  - New optimization algorithms or metrics.
  - Changelog rewriting.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm the implementation follows this plan and the product/test specs.
  - Confirm no compatibility alias keeps `strategy_parameters` alive.
  - Confirm no report path calls `Strategy.parameters()`.
  - Confirm architecture boundaries remain intact.
  - Confirm fresh verification evidence includes runtime-sensitive checks.
- Acceptance artifact location:
  - This plan's `## Evaluator Review` section after implementation.
- How the generator and evaluator agree on done before execution:
  - Generator must follow TDD: write failing contract tests, run them, implement
    minimal production changes, rerun targeted tests, then broaden
    verification.
  - Evaluator rejects new parallel metadata/reporting paths and any
    implementation that infers constructor args or runtime attributes.
- Checks the evaluator will use:
  - `rg -n "strategy_parameters|def parameters|Strategy.parameters\\(\\)" src tests docs/site README.md notebooks`
  - Targeted tests for report shape, stale hook ignore behavior, config-less
    behavior, invalid strategy-like validation, and ParameterStudy/report
    alignment.
  - `uv run poe verify-runtime`
  - `uv run poe verify`
  - `git diff --check`
- Auto-fail conditions:
  - `RunManifest` keeps `strategy_parameters`.
  - Report construction calls `parameters()` directly or indirectly.
  - Base `Strategy` keeps `parameters()` as a canonical method.
  - A config-less invalid custom strategy-like object silently reports `{}`.
  - `ParameterStudy` row/report snapshots can disagree for successful rows.
  - Implementation adds WFA, metadata bags, or direct class-plus-config API
    behavior.
  - Verification fails without a recorded blocker.

## Codebase Survey Results

### Project Structure

- The package is a Python 3.13 library under `src/quantcraft`.
- Capability roots are `data`, `trading`, `research`, `strategy`, `backtest`,
  `execution`, and `integrations`.
- Relevant Tier B roots for this work:
  - `src/quantcraft/strategy`: shared strategy authoring and config contract.
  - `src/quantcraft/backtest`: historical runtime, result, report, and plotting.
  - `src/quantcraft/research`: `ParameterStudy` composition and study records.
- Tests use the existing taxonomy:
  - `tests/unit`
  - `tests/integration`
  - `tests/structure`
  - `tests/smoke`
  - `tests/perf`
- There is no current `tests/regression` directory or pytest marker. Do not add
  a new top-level test category for this slice. Put regression-style checks in
  existing unit, integration, and structure locations.

### Relevant Domain Files

- `src/quantcraft/strategy/config.py`
  - Defines `StrategyConfig`, `JSONConfigScalar`, config validation errors,
    immutable materialized snapshots, and `StrategyConfig.to_mapping()`.
  - This is the canonical snapshot source to reuse.
- `src/quantcraft/strategy/strategy.py`
  - Defines `Strategy[ConfigT]`, config declaration resolution, config
    materialization, runtime state reset, `display_name`, and the old
    `parameters()` method.
  - Stage 3 must remove the base `parameters()` method.
- `src/quantcraft/backtest/strategy_runtime.py`
  - Defines `StrategyLike` and `_StrategyDriver`.
  - `StrategyLike` currently requires `parameters()`. It must require
    `config: StrategyConfig` instead.
  - This is the right place for a small private strategy-like config validation
    helper because it owns runtime strategy protocol shape.
- `src/quantcraft/backtest/engine.py`
  - Public `BacktestEngine.run(...)` entry point.
  - Keep the signature unchanged. Add validation through the runtime helper
    before `_run_backtest(...)` starts.
- `src/quantcraft/backtest/runtime.py`
  - `_run_backtest(...)` creates `_ReportBuilder`, runs `_StrategyDriver`, then
    calls `report_builder.build(..., strategy=strategy, ...)`.
  - No new report path is needed. The existing handoff to `_ReportBuilder` is
    the canonical path.
- `src/quantcraft/backtest/reporting.py`
  - Defines `RunManifest` with current `strategy_parameters`.
  - `_ReportBuilder.build(...)` currently sets
    `strategy_parameters=_strategy_parameters(strategy)`.
  - `_strategy_parameters(...)` currently calls `strategy.parameters()`.
  - Replace this with `strategy_config=_strategy_config(strategy)` using
    `strategy.config.to_mapping()`.
- `src/quantcraft/research/parameter_exploration.py`
  - `ParameterStudy` already materializes candidates as `StrategyConfig`
    instances and records `strategy_config=MappingProxyType(config.to_mapping())`.
  - `_row_to_record(...)` already exports `strategy_config`.
  - Only assertions and any stale report references need updating; do not
    change study row data flow unless tests expose a real mismatch.

### Existing Canonical Paths To Reuse

- Use `StrategyConfig.to_mapping()` for all report snapshots.
- Use `Strategy.config_type()` and `Strategy(config)` materialization already
  implemented in `Strategy`.
- Use existing `BacktestEngine.run(...) -> _run_backtest(...) ->
  _ReportBuilder.build(...) -> BacktestResult(_report=report)` flow.
- Use existing `ParameterStudy` construction path:
  `config_type(**candidate) -> strategy = StrategyClass(config) ->
  engine.run(..., strategy=strategy) -> GridSearchRow.success(...)`.
- Use existing fixture helpers:
  - `tests.integration.research.support_backtest_runner.fixture_bar_series`
  - `tests.integration.research.support_backtest_runner.run_engine_backtest`
  - `tests.unit.research.support_parameter_study.make_bars`
  - `tests.unit.research.support_parameter_study.make_engine`
  - `tests.support_backtest.assert_canonical_report`

### Current Stale Surface Found

- Source:
  - `src/quantcraft/strategy/strategy.py` defines `Strategy.parameters()`.
  - `src/quantcraft/backtest/strategy_runtime.py` requires `parameters()` in
    `StrategyLike`.
  - `src/quantcraft/backtest/reporting.py` has `strategy_parameters` and calls
    `_strategy_parameters(strategy)`.
- Tests:
  - Backtest reporting tests assert `report.run.strategy_parameters`.
  - ParameterStudy tests assert retained reports use `strategy_parameters`.
  - Test strategy fixtures define `parameters()` just to mirror config.
  - Canonical report snapshots contain `strategy_parameters`.
- Docs/examples:
  - `docs/site/guides/parameter-exploration.md` teaches `def parameters(...)`.
  - Current product specs such as `parameter-exploration.md` and
    `research-ergonomics.md` contain current-looking `Strategy.parameters()`
    language and must be updated where they are current authority.
- Notebooks:
  - Initial text search did not show current strategy `parameters()` examples
    in notebooks, but implementation must run notebook validation after docs
    and examples are migrated.

## Implementation Scope And Non-Scope

In scope:

- Replace `RunManifest.strategy_parameters` with `RunManifest.strategy_config`.
- Validate strategy-like objects expose a real `StrategyConfig` instance.
- Remove report use of `Strategy.parameters()`.
- Remove base `Strategy.parameters()`.
- Update current tests, fixtures, docs, examples, and notebooks to use
  `StrategyConfig` and `strategy_config`.
- Keep historical/audit mentions only where they clearly describe prior state.

Non-scope:

- No direct class-plus-config `BacktestEngine.run(...)` API.
- No WFA implementation.
- No metadata bag.
- No new test taxonomy.
- No changes to `trading` or `execution`.

## Design Decisions

### Report Snapshot Source

Use:

```python
strategy.config.to_mapping()
```

Reason:

- It is already the canonical `StrategyConfig` plain dict snapshot API.
- It preserves default fields and falsey JSON scalar values.
- It returns a detached plain dict, satisfying the product spec.
- It avoids introspecting constructor args, public attributes, or user metadata.

Do not introduce a new serializer in `backtest`. Future domain-object config
serialization is explicitly out of Stage 3 scope.

### Strategy-Like Validation

Add a small private helper in `src/quantcraft/backtest/strategy_runtime.py`:

```python
def validate_strategy_like_config(strategy: object) -> StrategyConfig:
    config = getattr(strategy, "config", None)
    if not isinstance(config, StrategyConfig):
        raise ValueError("strategy must expose StrategyConfig config metadata")
    return config
```

Use this helper from `BacktestEngine.run(...)` before `_run_backtest(...)`.
This gives invalid custom strategy-like objects a clear validation failure
before report construction can produce misleading metadata.

Use `ValueError` for the runtime input contract. Keep
`StrategyConfigValidationError` for failures raised by actual `StrategyConfig`
materialization and validation.

### Report Field Replacement

Change:

```python
strategy_parameters: dict[str, object]
```

to:

```python
strategy_config: dict[str, JSONConfigScalar]
```

in `RunManifest`.

Remove `_strategy_parameters(...)` and `_normalize_public_value(...)` unless
another current code path still uses `_normalize_public_value(...)`.

Add:

```python
def _strategy_config(strategy: Any) -> dict[str, JSONConfigScalar]:
    config = validate_strategy_like_config(strategy)
    return config.to_mapping()
```

Keep `_strategy_display_name(...)` unchanged.

### Base Strategy Surface

Remove the `Strategy.parameters()` method from `Strategy`. User classes may
still define their own `parameters()` method as ordinary Python, but the
framework must not require or call it.

### Test Taxonomy

The test spec proposes regression tests as a level, but the current repo does
not have a `tests/regression` taxonomy or pytest marker. Implement regression
coverage inside:

- `tests/unit/backtest/...` for local stale-hook and invalid strategy-like
  checks
- `tests/integration/research/...` for real direct backtest and study/report
  alignment
- `tests/structure/docs/...` for managed current docs

This avoids adding repository workflow surface for a single slice.

## Data Flow And Control Flow

### Direct Backtest

1. User constructs a strategy instance, for example
   `SmaStrategy(SmaConfig(fast=10))`.
2. `Strategy.__init__` materializes `self.config` as a `StrategyConfig`
   instance.
3. `BacktestEngine.run(...)` validates bars/source and calls
   `validate_strategy_like_config(strategy)`.
4. `_run_backtest(...)` runs the existing runtime loop unchanged.
5. `_ReportBuilder.build(...)` calls `_strategy_config(strategy)`.
6. `_strategy_config(...)` returns `strategy.config.to_mapping()`.
7. `RunManifest.strategy_config` stores the detached plain dict.

### Config-Less Direct Backtest

1. User constructs a plain `Strategy` subclass with no explicit config type.
2. `Strategy.__init__` materializes `StrategyConfig()`.
3. `StrategyConfig.to_mapping()` returns `{}`.
4. The report stores `strategy_config == {}`.

### ParameterStudy

1. `ParameterStudy.grid_search(...)` validates grid keys against
   `strategy.config_type`.
2. `_prepare_candidate(...)` materializes `config = config_type(**candidate)`.
3. `_prepare_candidate(...)` records `strategy_config =
   MappingProxyType(config.to_mapping())`.
4. The study constructs `strategy = self.strategy(prepared.config)`.
5. `engine.run(..., strategy=strategy)` records
   `report.run.strategy_config = strategy.config.to_mapping()`.
6. `GridSearchRow.success(...)` keeps the existing row-level
   `strategy_config`.
7. Tests assert row and report snapshots match.

## Major Files And Responsibilities

### Production Code

- `src/quantcraft/strategy/strategy.py`
  - Remove base `parameters()`.
  - Keep `display_name`.
  - Do not change config materialization or runtime order APIs.
- `src/quantcraft/backtest/strategy_runtime.py`
  - Update `StrategyLike` to require `config: StrategyConfig`.
  - Remove `parameters()` from the protocol.
  - Add private config-validation helper.
- `src/quantcraft/backtest/engine.py`
  - Call the validation helper in `BacktestEngine.run(...)`.
  - Keep the public signature unchanged.
- `src/quantcraft/backtest/reporting.py`
  - Replace `RunManifest.strategy_parameters` with `strategy_config`.
  - Replace `_strategy_parameters(...)` with `_strategy_config(...)`.
  - Remove old NaN-normalization behavior for strategy metadata because
    `StrategyConfig` rejects non-finite float values upstream.
- `src/quantcraft/backtest/__init__.py`
  - No planned public export change unless type names need import ordering
    cleanup after `RunManifest` changes.
- `src/quantcraft/research/parameter_exploration.py`
  - No planned data-flow change.
  - Update only if mypy or tests expose a stale report-field reference.

### Tests And Fixtures

- `tests/integration/research/test_backtest_result_reporting_contract.py`
  - Replace old explicit-parameters tests with config snapshot and stale-hook
    ignored tests.
- `tests/integration/research/test_parameter_study_grid_search.py`
  - Update retained report assertions to `report.run.strategy_config`.
- `tests/integration/research/test_parameter_study_canonical_grid_contract.py`
  - Remove `parameters()` methods from managed test strategies.
  - Update selected report assertion to `strategy_config`.
- `tests/unit/research/support_parameter_study.py`
  - Remove `NoTradeStrategy.parameters()`.
  - Update call-count tests to inspect `strategy.config.to_mapping()`.
- `tests/unit/research/test_parameter_grid_validation.py`
  - Replace `call["strategy"].parameters()` assertions with
    `call["strategy"].config.to_mapping()`.
- `tests/unit/strategy/test_strategy_surface.py`
  - Keep config availability tests.
  - Add or adjust assertion that base `Strategy` has no canonical
    `parameters` attribute.
- `tests/unit/research/test_strategy_surface.py`
  - This older research-surface test currently asserts `parameters()`.
    Update it to `display_name` only or move config assertions to
    `quantcraft.strategy`.
- `tests/fixtures/backtest/canonical_report_snapshots.json`
  - Rename `strategy_parameters` keys to `strategy_config`.
  - Expected values are `{}` for current config-less canonical strategies unless
    those strategies are also migrated to explicit `StrategyConfig`.
- `tests/support_backtest.py`
  - `assert_canonical_report(...)` should continue to work because it compares
    dataclass fields against fixture keys. Update fixture data first; change
    constants only if field-set assertions require it.
- `tests/structure/docs/test_reporting_config_source_of_truth_docs.py`
  - Add a new docs structure test for Stage 3 routing and current-doc cleanup.
- Existing structure docs tests:
  - Update stale expectations in
    `tests/structure/docs/test_backtest_result_reporting_docs.py`.
  - Update strategy configuration docs tests if Stage 3 resolution changes
    current-contract wording.

### Managed Docs And Examples

- `docs/site/guides/parameter-exploration.md`
  - Remove `def parameters(...)` from the strategy example.
  - Teach `self.config` as the tunable settings path.
- `docs/site/reference/public-api.md`
  - Ensure `StrategyConfig` and `BacktestResult.report` remain listed.
  - Do not list `Strategy.parameters()`.
- `docs/site/examples.md`, `docs/site/quickstart.md`, and README
  - Update only if they contain stale report/config examples.
- `docs/product-specs/parameter-exploration.md`
  - Update current examples and current-contract text that still present
    `Strategy.parameters()` as active metadata.
- `docs/product-specs/research-ergonomics.md`
  - Update current-contract language that says `Strategy.parameters()` is the
    explicit metadata path.
- `docs/product-specs/strategy-configuration-contract.md`
  - Preserve problem-background references, but update unresolved/open current
    Stage 3 wording so it does not read as still undecided.
- `docs/product-specs/wfa-prerequisite-roadmap.md`
  - Preserve roadmap background, but update Stage 3 readiness state only if the
    implementation slice closes that blocker.
- `notebooks/*.ipynb`
  - Inspect for runnable `def parameters(...)` examples during implementation.
  - Update notebooks only when they teach or execute tunable strategy settings.

## Test Implementation Plan

### Task 1: Direct Report Contract Tests

**Files:**

- Modify: `tests/integration/research/test_backtest_result_reporting_contract.py`

**Step 1: Write failing tests**

Add tests for:

- configured strategy report exposes full `strategy_config`
- config-less strategy report exposes `{}`
- stale user-defined `parameters()` returning conflicting data is ignored
- stale user-defined `parameters()` raising is not called
- `strategy_parameters` is absent

Representative assertion shape:

```python
assert result.report.run.strategy_config == {"fast": 10, "slow": 20}
assert not hasattr(result.report.run, "strategy_parameters")
```

**Step 2: Run failing tests**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_result_reporting_contract.py -q
```

Expected: failures show missing `strategy_config`, present old
`strategy_parameters`, or stale `parameters()` behavior.

### Task 2: ParameterStudy Alignment Tests

**Files:**

- Modify: `tests/integration/research/test_parameter_study_grid_search.py`
- Modify: `tests/integration/research/test_parameter_study_canonical_grid_contract.py`

**Step 1: Write failing assertions**

Assert:

```python
assert best.backtest is not None
assert best.backtest.report.run.strategy_config == dict(best.strategy_config)
assert not hasattr(best.backtest.report.run, "strategy_parameters")
```

Remove managed test strategy `parameters()` methods that only mirror
`self.config.to_mapping()`.

**Step 2: Run failing tests**

Run:

```bash
uv run pytest tests/integration/research/test_parameter_study_grid_search.py tests/integration/research/test_parameter_study_canonical_grid_contract.py -q
```

Expected: failures show report field mismatch until production code changes.

### Task 3: Strategy-Like Validation Tests

**Files:**

- Create: `tests/unit/backtest/test_strategy_like_report_config_validation.py`
- Modify: `tests/unit/strategy/test_strategy_surface.py`

**Step 1: Write failing tests**

Cover:

- custom strategy-like object without `config` raises a clear `ValueError`
- custom strategy-like object with non-`StrategyConfig` `config` raises a clear
  `ValueError`
- base `Strategy` does not define canonical `parameters`

Keep the fake strategy-like object minimal but runtime-shaped enough to reach
engine validation if the helper is missing.

**Step 2: Run failing tests**

Run:

```bash
uv run pytest tests/unit/backtest/test_strategy_like_report_config_validation.py tests/unit/strategy/test_strategy_surface.py -q
```

Expected: failures show missing validation and old base method.

### Task 4: Production Code Minimal Change

**Files:**

- Modify: `src/quantcraft/strategy/strategy.py`
- Modify: `src/quantcraft/backtest/strategy_runtime.py`
- Modify: `src/quantcraft/backtest/engine.py`
- Modify: `src/quantcraft/backtest/reporting.py`

**Implementation notes:**

- Remove `Strategy.parameters()`.
- Update `StrategyLike`:

```python
class StrategyLike(Protocol):
    config: StrategyConfig
    ...
```

- Add `validate_strategy_like_config(...)` in `strategy_runtime.py`.
- Call `validate_strategy_like_config(strategy)` from `BacktestEngine.run(...)`.
- In `reporting.py`, import `StrategyConfig`/`JSONConfigScalar` through the
  strategy package path or strategy config module as needed.
- Change `RunManifest.strategy_parameters` to `strategy_config`.
- Replace:

```python
strategy_parameters=_strategy_parameters(strategy)
```

with:

```python
strategy_config=_strategy_config(strategy)
```

- Delete `_strategy_parameters(...)` and `_normalize_public_value(...)` unless
  another source reference remains.

**Step 2: Run targeted tests**

Run the tests from Tasks 1-3 again.

Expected: targeted report and validation tests pass.

### Task 5: Update Existing Test Expectations And Fixtures

**Files:**

- Modify: `tests/unit/research/support_parameter_study.py`
- Modify: `tests/unit/research/test_parameter_grid_validation.py`
- Modify: `tests/unit/research/test_strategy_surface.py`
- Modify: `tests/fixtures/backtest/canonical_report_snapshots.json`
- Modify any failing report fixture tests surfaced by targeted runs.

**Implementation notes:**

- Replace managed test helper `parameters()` methods with config access.
- Replace assertions against `strategy.parameters()` with
  `strategy.config.to_mapping()`.
- Rename canonical snapshot run keys from `strategy_parameters` to
  `strategy_config`.

**Step 2: Run unit and integration lanes**

Run:

```bash
uv run poe test-unit
uv run poe test-integration
```

Expected: no stale test expectations remain.

### Task 6: Current Docs, Examples, And Structure Checks

**Files:**

- Modify: `docs/site/guides/parameter-exploration.md`
- Modify: `docs/product-specs/parameter-exploration.md`
- Modify: `docs/product-specs/research-ergonomics.md`
- Modify: `docs/product-specs/strategy-configuration-contract.md`
- Modify: `tests/structure/docs/test_backtest_result_reporting_docs.py`
- Create: `tests/structure/docs/test_reporting_config_source_of_truth_docs.py`
- Modify other current docs/tests only when `rg` identifies current guidance,
  not historical audit references.

**Implementation notes:**

- Do not add public migration notes for pre-release `Strategy.parameters()`.
- Do not rewrite `CHANGELOG.md`.
- Do not erase historical plans merely because they mention old terms.
- Structure tests should inspect current authority and public docs, not do a
  blind repository-wide ban that catches historical/audit material.

**Step 2: Run docs/structure checks**

Run:

```bash
uv run poe test-structure
uv run poe repo-check
```

Expected: docs routing and current-doc tests pass.

### Task 7: Notebook And Smoke Validation

**Files:**

- Modify tracked notebooks only if they contain runnable current
  `parameters()` strategy examples or stale report-field assertions.
- Modify smoke examples if they teach `parameters()`.

**Step 1: Search current managed surfaces**

Run:

```bash
rg -n "def parameters|strategy_parameters|Strategy.parameters\\(\\)" README.md docs/site notebooks tests/smoke src tests/unit tests/integration tests/structure
```

Expected: only negative stale-hook tests and historical/current-spec background
references remain. Current public docs and managed examples should not teach
old behavior.

**Step 2: Run smoke and notebook validation**

Run:

```bash
uv run poe test-smoke
uv run poe notebook-validate
```

Expected: managed examples and notebooks run against the new contract.

### Task 8: Full Verification And Evaluator Pass

**Files:**

- Modify: this plan's `## Evaluator Review` section.

**Step 1: Runtime-sensitive verification**

Run:

```bash
uv run poe verify-runtime
```

Expected: default verification plus performance gate passes.

**Step 2: Default verification**

Run:

```bash
uv run poe verify
```

Expected: default repo verification passes.

**Step 3: Whitespace check**

Run:

```bash
git diff --check
```

Expected: no whitespace errors.

**Step 4: Record evaluator review**

Update this plan with:

- findings first
- exact verification commands and output summaries
- final disposition

## Migration And Compatibility Considerations

- This is a breaking pre-beta cleanup. Do not keep
  `report.run.strategy_parameters` as an alias.
- Do not keep `Strategy.parameters()` on the base class.
- User-defined `parameters()` methods may remain in user code, but framework
  reporting ignores them.
- Managed current docs and tests must migrate. Historical/audit records may
  keep older language when clearly historical.
- Canonical report snapshots must be updated because the report schema changes.
- No public direct-run API migration occurs in this phase; that is the next WFA
  prerequisite phase.

## Risks And Mitigations

- Risk: A blind docs search flags historical/audit references.
  - Mitigation: Structure tests should target current authority and public docs,
    not all of `docs/plans` or historical background sections.
- Risk: Removing `Strategy.parameters()` breaks tests that use it as a
  convenient config accessor.
  - Mitigation: Replace those test assertions with `strategy.config.to_mapping()`.
- Risk: Invalid custom strategy-like objects fail late after runtime work.
  - Mitigation: Validate `strategy.config` in `BacktestEngine.run(...)` before
    `_run_backtest(...)`.
- Risk: Report snapshots become live views if `StrategyConfig._values` is
  reused directly.
  - Mitigation: Always call `to_mapping()` and store the returned plain dict.
- Risk: Introducing a local serializer duplicates `StrategyConfig` semantics.
  - Mitigation: Reuse `StrategyConfig.to_mapping()` only.
- Risk: New `tests/regression` taxonomy creates repo workflow churn.
  - Mitigation: Keep regression-style assertions inside existing test
    directories.
- Risk: Performance lane changes because runtime validation runs on every
  backtest.
  - Mitigation: Validation is one `getattr` and `isinstance`; verify with
    `uv run poe verify-runtime`.

## Open Questions

- None requiring human confirmation for Stage 3 implementation planning.

## Evaluator Review

- Findings:
  - No blocking findings for the implementation slice.
  - `RunManifest` now exposes `strategy_config` and no longer exposes
    `strategy_parameters`.
  - `BacktestEngine.run(...)` copies the `StrategyConfig.to_mapping()` snapshot
    before runtime execution and passes that snapshot through to reporting.
  - Report construction stores the run-start `strategy_config` snapshot; it
    does not call `Strategy.parameters()`.
  - Base `Strategy` no longer defines `parameters()` as a canonical method.
  - User-defined `parameters()` methods may still exist on user strategy
    classes, but reporting ignores them.
  - Config-less official `Strategy` subclasses report `strategy_config == {}`.
  - Custom strategy-like objects without real `StrategyConfig` metadata fail
    with an explicit `ValueError` before report generation.
  - Successful `ParameterStudy` rows and retained backtest reports now agree on
    the same full `strategy_config` snapshot, including defaults that are not
    present in partial `candidate_parameters`.
  - Managed current docs, public examples, smoke examples, structure checks, and
    canonical report snapshots teach the new contract.
  - The implementation does not add WFA behavior, arbitrary metadata bags,
    direct class-plus-config backtest API behavior, or Tier A changes.
  - Subagent review found four important coverage/semantics gaps; all were
    fixed and a follow-up subagent review found no blocker or important issues.
- Verification evidence:
  - Red verification before implementation:
    - `uv run pytest tests/integration/research/test_backtest_result_reporting_contract.py tests/integration/research/test_parameter_study_grid_search.py tests/integration/research/test_parameter_study_canonical_grid_contract.py tests/unit/backtest/test_strategy_like_report_config_validation.py tests/unit/strategy/test_strategy_surface.py -q`
    - Output summary: 11 failed, 11 passed. Failures showed missing
      `strategy_config`, reporting calling `parameters()`, missing
      strategy-like config validation, and base `Strategy.parameters()`.
  - Targeted green verification:
    - `uv run pytest tests/integration/research/test_backtest_result_reporting_contract.py tests/integration/research/test_parameter_study_grid_search.py tests/integration/research/test_parameter_study_canonical_grid_contract.py tests/unit/backtest/test_strategy_like_report_config_validation.py tests/unit/strategy/test_strategy_surface.py -q`
    - Output: `22 passed in 5.01s`
  - `uv run poe test-unit`
    - Output after review fixes: `425 passed in 1.19s`
  - `uv run poe test-integration`
    - Output: `115 passed in 10.67s`
  - `uv run poe test-structure`
    - Output after Stage 3 structure guard was added: `143 passed in 0.40s`
  - `uv run poe test-smoke`
    - Output after review fixes: `10 passed in 0.72s`
  - `uv run poe notebook-validate`
    - Output: validated `backtest-plotting-real-data-example.ipynb`,
      `binance-spot-usdm-validation.ipynb`,
      `binance-usdm-rsi-2024-ad-hoc.ipynb`,
      `research-ergonomics-quickstart.ipynb`, and
      `spot-cross-exchange-price-comparison.ipynb`.
  - `uv run ruff check .`
    - Output: `All checks passed!`
  - `uv run mypy src`
    - Output: `Success: no issues found in 59 source files`
  - `uv run poe repo-check`
    - Output: `repository checks passed`
  - `uv run poe verify-runtime`
    - Output summary: Ruff passed; mypy passed; `pytest -q` reported
      `693 passed, 4 skipped`; coverage policy check passed at 93%; package
      build succeeded; repository checks passed; notebook validation passed;
      performance gate reported `3 passed`.
  - `uv run poe verify`
    - Output summary: Ruff passed; mypy passed; `pytest -q` reported
      `693 passed, 4 skipped`; coverage policy check passed at 93%; package
      build succeeded; repository checks passed; notebook validation passed.
  - Initial subagent review:
    - Product/spec reviewer: one important issue, run-start snapshot timing for
      mutable custom `StrategyLike`.
    - Test reviewer: three important issues, partial-vs-full `ParameterStudy`
      report alignment coverage, falsey/default scalar report-boundary
      coverage, and smoke/example report assertion coverage.
    - Code/architecture reviewer: no blocker findings.
  - Post-fix subagent review:
    - Output summary: no blocker or important findings. Reviewer confirmed
      run-start snapshot copy, partial/full alignment coverage, falsey/default
      scalar report coverage, and smoke/example report assertion coverage.
  - Final commit-readiness review fan-out:
    - Verification/test reviewer: no blocker or important findings; confirmed
      coverage for direct report config snapshots, stale `parameters()` hooks,
      custom strategy-like config validation, ParameterStudy report alignment,
      smoke examples, and structure guards.
    - Architecture/contract reviewer: one important documentation issue in
      `docs/product-specs/wfa-prerequisite-roadmap.md`; the roadmap still
      presented the removed `strategy_parameters`/`Strategy.parameters()` report
      path as current state.
    - `/tmp` source comparison reviewer: no blocker or important findings.
      Relevant QuantCraft crosscheck artifacts under `/tmp` did not depend on
      the removed report metadata path; `/tmp/quantcraft-external-comparison`
      remains stale as an advisory-only external harness.
  - Final review fix:
    - Updated `docs/product-specs/wfa-prerequisite-roadmap.md` so Stage 3
      reporting config source-of-truth is described as resolved current state,
      not as a pending/current `strategy_parameters` dependency.
  - Final post-review verification:
    - `uv run poe test-structure`
      - Output: `143 passed in 0.41s`
    - `uv run poe repo-check`
      - Output: `repository checks passed`
    - `uv run poe verify`
      - Output summary after the final roadmap fix: Ruff passed; mypy passed;
        `pytest -q` reported `693 passed, 4 skipped`; coverage policy check
        passed at 93%; package build succeeded; repository checks passed;
        notebook validation passed.
  - `git diff --check`
    - Output: no whitespace errors
- Final disposition:
  - Accepted. Stage 3 reporting config source-of-truth cleanup is implemented
    and verified.
