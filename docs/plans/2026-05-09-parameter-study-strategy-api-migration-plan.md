# ParameterStudy Strategy API Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to
> implement this plan task-by-task.

**Goal:** Migrate `ParameterStudy` from `strategy_factory` to the canonical
`strategy=StrategyClass` plus `StrategyConfig` contract, removing the old
factory API from active code, tests, examples, and public docs.

**Architecture:** Keep `quantcraft.strategy` as the source of strategy
configuration truth and `quantcraft.research.ParameterStudy` as the research
workflow that expands search spaces, materializes config snapshots, filters
candidates, runs fresh strategy instances, and records comparison rows.
`StrategyConfig.validate()` owns strategy-domain invariants; `ParameterStudy`
owns study-level pruning and result bookkeeping.

**Tech Stack:** Python 3.13, `quantcraft.strategy.StrategyConfig`,
`quantcraft.research.ParameterStudy`, pytest, Ruff, mypy, Poe/uv verification.

---

- Date: 2026-05-09
- Task: Stage 2 ParameterStudy Strategy API Migration
- Status: `implemented`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Planner Contract

- Goal: Replace the current `strategy_factory`-centered parameter exploration
  API with a strict config-backed `ParameterStudy(strategy=StrategyClass)` API
  and result model.
- Governing docs:
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
  - `docs/product-specs/strategy-configuration-contract.md`
  - `docs/product-specs/strategy-configuration-contract-test-scenarios.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/product-specs/walk-forward-analysis-readiness.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-05-06-strategy-configuration-contract-implementation-plan.md`
- Why these are governing:
  - `README.md` defines first-beta scope and names `ParameterStudy` as public
    beta surface.
  - `ARCHITECTURE.md` and package-topology docs define `strategy` and
    `research` ownership and confirm this is Tier B, not Tier A.
  - `parameter-exploration.md` defines current grid, objective, failure,
    records, and selected-run behavior that must be migrated.
  - `strategy-configuration-contract.md` defines `StrategyConfig`,
    `candidate_parameters`, `strategy_config`, empty search spaces, and WFA
    prerequisites. This Stage 2 plan deliberately resolves the document's
    downstream open questions with stricter breaking decisions because the
    library is not yet released.
  - `wfa-prerequisite-roadmap.md` orders this slice before reporting cleanup
    and WFA resume.
  - `RELIABILITY.md` requires fresh verification and `verify-runtime` for
    research/backtest-sensitive work.
  - `SECURITY.md` confirms no live credentials or Tier A progression are in
    scope.
- In-repo scope:
  - `src/quantcraft/strategy/config.py`
  - `src/quantcraft/research/parameter_exploration.py`
  - `src/quantcraft/research/__init__.py` only if public exports need adjustment
  - `tests/unit/strategy/*`
  - `tests/unit/research/*`
  - `tests/integration/research/*`
  - `tests/smoke/local/test_public_beta_examples.py`
  - `tests/structure/*` docs/API/architecture checks as needed
  - `docs/site/*`
  - active product specs or test specs only where they describe current Stage 2
    behavior rather than historical context
- Out-of-repo scope:
  - No external connectors.
  - No live trading, paper trading, exchange credentials, or task-driven network
    dependency.
  - No package publishing.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This slice touches Tier B
  `strategy`, `research`, and backtest-adjacent tests/docs, without `trading`
  or `execution` behavior changes.
- Verification commands:
  - Targeted while developing:
    - `uv run pytest tests/unit/strategy/test_strategy_config_materialization.py -q`
    - `uv run pytest tests/unit/research/test_parameter_grid_validation.py -q`
    - `uv run pytest tests/unit/research/test_grid_search_records.py -q`
    - `uv run pytest tests/unit/research/test_grid_search_result_selection.py -q`
    - `uv run pytest tests/unit/research/test_parameter_study_preflight.py -q`
    - `uv run pytest tests/integration/research/test_parameter_study_grid_search.py -q`
    - `uv run pytest tests/integration/research/test_parameter_study_failures.py -q`
    - `uv run pytest tests/integration/research/test_parameter_study_selected_run.py -q`
    - `uv run pytest tests/integration/research/test_parameter_study_metric_states.py -q`
    - `uv run pytest tests/integration/research/test_parameter_study_canonical_grid_contract.py -q`
    - `uv run pytest tests/smoke/local/test_public_beta_examples.py -q`
  - Full gates before completion:
    - `uv run poe repo-check`
    - `uv run poe verify`
    - `uv run poe verify-runtime`
- Success criteria:
  - `ParameterStudy` accepts `strategy=StrategyClass` and no longer accepts or
    exports `strategy_factory`.
  - Active source, public docs, examples, and tests no longer teach
    `strategy_factory`; historical docs may retain it as audit history.
  - `StrategyConfig.validate()` exists, runs after field/default/override
    validation, and can reject cross-field domain invariants.
  - `grid_search(parameters={})` runs exactly one default-config candidate.
  - Non-empty `parameters` keys must be declared public `StrategyConfig` fields;
    unknown/private fields fail before any backtest starts.
  - Candidate values are validated against `StrategyConfig` primitive type
    rules before any backtest starts.
  - Each row exposes `candidate_parameters` and full `strategy_config`; row
    field `parameters` is removed, not retained as an alias.
  - `to_records()` uses `candidate_parameters` and `strategy_config`, not
    `parameters`.
  - `StrategyConfig.validate()` failures become rejected rows with
    `rejection_stage="strategy_config"` and no backtest execution.
  - `constraint` remains as a study-level pruning hook, receives full
    `strategy_config` mapping, and `False` returns rejected rows with
    `rejection_stage="constraint"`.
  - `constraint` exceptions and non-bool returns remain failed rows with
    `failure_stage="constraint"` unless `fail_fast=True`.
  - Strategy construction failures become failed rows with
    `failure_stage="strategy_construction"`.
  - Backtest and metric extraction failure behavior remains inspectable and
    `fail_fast=True` preserves original exception types with row context notes.
  - Best-row UX centers `best.strategy_config`; `best.candidate_parameters`
    remains the partial override audit trail.
  - WFA remains paused; Stage 3 reporting migration remains separate unless a
    test must stop relying on report-level `strategy_parameters`.
- Out of scope:
  - WFA implementation or fold model.
  - New optimization algorithms.
  - Parallel/grid worker controls.
  - Parameter descriptor DSL, range metadata, automatic search-space generation,
    or static extraction of pruning conditions from validators.
  - `BacktestEngine.run(strategy=StrategyClass, config=...)`.
  - Full reporting migration from `strategy_parameters` to `strategy_config`.
  - Removing `Strategy.parameters()` globally; Stage 3 owns the report source of
    truth cleanup.
  - Live, paper, shorting, leverage, multi-symbol, and multi-timeframe behavior.

## Stage 2 Binding Decisions

These decisions supersede the open downstream questions in
`docs/product-specs/strategy-configuration-contract.md` for this implementation
slice.

- This is a breaking migration. `strategy_factory` is removed from active
  `ParameterStudy` code, active tests, public docs, and examples. No alias,
  deprecation path, or advanced escape hatch remains in the active public API.
- `ParameterStudy(engine=..., bars=..., strategy=StrategyClass)` is the only
  study construction path.
- `parameters` remains the `grid_search(...)` input name for the search space
  only. It never names row-level candidate snapshots.
- `candidate_parameters` means the partial candidate override from the search
  space.
- `strategy_config` means the full materialized config snapshot:
  `StrategyConfig defaults + candidate_parameters`.
- `GridSearchRow.parameters` is removed entirely.
- `to_records()["parameters"]` is removed entirely.
- `StrategyConfig.validate()` is added as the strategy-domain invariant hook.
- `StrategyConfig.validate()` failures are rejected rows, not failed rows.
- `constraint` remains, but only as a study-level pruning hook over a full
  `strategy_config` mapping.
- Candidate processing order is:

  ```text
  candidate_parameters
  -> StrategyConfig(**candidate_parameters)
  -> StrategyConfig.validate()
  -> rejected(rejection_stage="strategy_config") if invalid
  -> constraint(strategy_config_mapping)
  -> rejected(rejection_stage="constraint") if False
  -> Strategy(config)
  -> engine.run(...)
  -> metric extraction
  ```

- `grid_search(parameters={})` is valid and produces one default-config
  candidate.
- Rejected rows include a nullable `rejection_stage`.
- Failed rows include a nullable `failure_stage`.
- `strategy_factory` is removed from `FailureStage`; add
  `strategy_construction`.
- Unknown fields, malformed grids, invalid objective paths, and candidate-limit
  violations are study definition errors and fail before any backtest starts.

## Market Reference Notes

- `backtesting.py` accepts a constraint over a dict-like full parameter
  combination and uses it to decide whether a combination is admissible before
  testing.
- vectorbt PRO exposes parameter conditions that can reference other parameter
  values, such as fast-window versus slow-window relationships.
- Optuna distinguishes trial outcomes such as complete, pruned, and failed
  rather than collapsing every non-success into one bucket.
- Pydantic keeps validation errors structured and supports whole-model
  validation for cross-field invariants.

Implication for Quantcraft: use full materialized config mappings for
study-level pruning, keep strategy invariants on the config object, and expose
structured rejection/failure diagnostics.

## Evaluator Acceptance Contract

- Evaluator owner: Codex evaluator pass after generator implementation.
- Evaluator-owned done contract for this slice:
  - Review the diff against this active plan and all Stage 2 binding decisions.
  - Confirm no active source, active public docs, current tests, smoke examples,
    or public API references continue to teach `strategy_factory`.
  - Confirm historical docs and old plans are not rewritten merely to erase
    audit history.
  - Confirm `strategy_factory` appears only in allowed historical contexts or
    explicit historical references.
  - Confirm Stage 3 reporting work was not silently pulled into this slice.
  - Confirm WFA remains paused.
  - Confirm verification evidence is fresh from the final working tree.
- Acceptance artifact location:
  - This plan's `## Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - Generator must implement only the planned Stage 2 slice.
  - Evaluator must treat any compatibility alias for `strategy_factory`,
    `row.parameters`, or record `"parameters"` as an auto-fail.
  - Evaluator must treat any direct Tier A `trading` or `execution` behavioral
    change as an auto-fail unless a human approval record is added first.
- Checks the evaluator will use:
  - `git diff --stat`
  - `git diff -- src/quantcraft/strategy/config.py src/quantcraft/research/parameter_exploration.py`
  - `rg -n "strategy_factory" src tests docs/site README.md`
  - `rg -n "row\\.parameters|\\[\"parameters\"\\]|failure_stage=.*strategy_factory" src tests docs/site README.md`
  - targeted pytest commands listed in the planner contract
  - `uv run poe repo-check`
  - `uv run poe verify`
  - `uv run poe verify-runtime`
- Auto-fail conditions:
  - `ParameterStudy` accepts `strategy_factory`.
  - `GridSearchRow` still exposes `parameters`.
  - `to_records()` still emits `parameters`.
  - `constraint` receives partial candidate parameters instead of full
    `strategy_config`.
  - `StrategyConfig.validate()` is missing or not called during materialization.
  - Invalid config candidates can reach `engine.run(...)`.
  - Unknown config fields are recorded as row failures instead of preflight
    study definition errors.
  - Runtime-sensitive verification is skipped without a recorded blocker.

## Generator Work Log

- Planned slice order:
  1. Add `StrategyConfig.validate()` tests.
  2. Implement `StrategyConfig.validate()`.
  3. Rewrite `GridSearchRow` unit tests for `candidate_parameters`,
     `strategy_config`, `rejection_stage`, and new failure stages.
  4. Update `GridSearchRow` and record serialization.
  5. Rewrite `ParameterStudy` preflight and grid validation tests for
     `strategy=...`, empty `parameters={}`, unknown field preflight, and
     no-engine-run guarantees.
  6. Implement `ParameterStudy(strategy=...)` construction and remove
     `strategy_factory`.
  7. Add/rewrite config-aware constraint tests.
  8. Add/rewrite config validation rejection tests.
  9. Rewrite integration tests for fresh strategy instances, selected rows,
     failures, metric states, canonical grid contract, and selected-run
     inspection.
  10. Update public docs and smoke examples.
  11. Run targeted tests.
  12. Run full verification gates.
  13. Perform evaluator review and update this plan.
- Notes:
  - Use TDD for each slice: write or rewrite failing tests first, run the
    targeted failure, implement the minimal code, rerun targeted tests.
  - Keep row snapshots immutable using the existing `MappingProxyType` pattern.
  - Do not import private research validation helpers into `quantcraft.strategy`.
  - Preserve deterministic cartesian ordering and `max_candidates` semantics.
  - Preserve existing objective selection behavior except for row field names.
  - Keep `Strategy.parameters()` available for report metadata until Stage 3.
- Blockers or scope changes:
  - None at planning time.

## Implementation Tasks

### Task 1: Add Config Invariant Validation Tests

**Files:**
- Modify: `tests/unit/strategy/test_strategy_config_materialization.py`
- Modify: `src/quantcraft/strategy/config.py`

**Step 1: Write failing tests**

Add tests proving:

```python
class SmaConfig(StrategyConfig):
    fast: int = 10
    slow: int = 20

    def validate(self) -> None:
        if self.fast >= self.slow:
            raise StrategyConfigValidationError("fast must be less than slow")
```

Expected behaviors:

- `SmaConfig(fast=5, slow=20)` succeeds.
- `SmaConfig(fast=20, slow=10)` raises
  `StrategyConfigValidationError`.
- `validate()` sees defaulted values when only one override is provided.
- `validate()` runs after unknown field/type validation, so unknown fields still
  use the existing unknown-field validation path.

**Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/unit/strategy/test_strategy_config_materialization.py -q
```

Expected: failure because `StrategyConfig.validate()` does not exist or is not
called.

**Step 3: Implement minimal config hook**

Add to `StrategyConfig`:

```python
def validate(self) -> None:
    pass
```

Call `self.validate()` after `_values` is attached and before freezing is
complete enough for user code to read fields. If validation raises
`StrategyConfigValidationError`, let it propagate. If a user raises `ValueError`
or another exception from `validate()`, wrap or translate only if the existing
config error policy requires it; otherwise document the exact behavior in tests.
Preferred behavior for this slice: tests should raise
`StrategyConfigValidationError` explicitly in user validators.

**Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/unit/strategy/test_strategy_config_materialization.py -q
```

Expected: pass.

### Task 2: Rewrite GridSearchRow Contract Tests

**Files:**
- Modify: `tests/unit/research/test_grid_search_records.py`
- Modify: `tests/unit/research/test_grid_search_result_selection.py`
- Modify: `src/quantcraft/research/parameter_exploration.py`

**Step 1: Write failing tests**

Update row construction tests to use:

```python
GridSearchRow.success(
    run_index=0,
    candidate_parameters={"fast": 5},
    strategy_config={"fast": 5, "slow": 20},
    backtest=backtest,
    metrics=metrics,
)
```

Expected row fields:

```python
dict(row.candidate_parameters) == {"fast": 5}
dict(row.strategy_config) == {"fast": 5, "slow": 20}
row.rejection_stage is None
row.failure_stage is None
```

Update rejected rows:

```python
GridSearchRow.rejected(
    run_index=1,
    candidate_parameters={"fast": 30, "slow": 20},
    strategy_config={"fast": 30, "slow": 20},
    rejection_stage="strategy_config",
    error=StrategyConfigValidationError("fast must be less than slow"),
)
```

Expected:

```python
row.status == "rejected"
row.rejection_stage == "strategy_config"
row.error_type == "StrategyConfigValidationError"
row.error_message == "fast must be less than slow"
```

Update record tests to assert:

```python
record["candidate_parameters"] == {"fast": 5}
record["strategy_config"] == {"fast": 5, "slow": 20}
"parameters" not in record
```

Update selection tests to use `candidate_parameters` and `strategy_config`;
`best.strategy_config` is the canonical selected config.

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/unit/research/test_grid_search_records.py tests/unit/research/test_grid_search_result_selection.py -q
```

Expected: failures because current rows expose `parameters` only.

**Step 3: Implement row model changes**

In `parameter_exploration.py`:

- Rename row field `parameters` to `candidate_parameters`.
- Add row field `strategy_config`.
- Add `RejectionStage = Literal["strategy_config", "constraint"]`.
- Add `rejection_stage: RejectionStage | None`.
- Change `FailureStage` to:

```python
FailureStage: TypeAlias = Literal[
    "constraint",
    "strategy_construction",
    "backtest",
    "metric_extraction",
]
```

- Update row factory methods to require `candidate_parameters` and
  `strategy_config`.
- Ensure both mappings are copied into `MappingProxyType`.
- Update `_row_to_record`.
- Remove all row-level `parameters` aliases.

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/unit/research/test_grid_search_records.py tests/unit/research/test_grid_search_result_selection.py -q
```

Expected: pass.

### Task 3: Rewrite ParameterStudy Constructor And Preflight Tests

**Files:**
- Modify: `tests/unit/research/test_parameter_study_preflight.py`
- Modify: `tests/unit/research/test_parameter_grid_validation.py`
- Modify: `tests/unit/research/support_parameter_study.py`
- Modify: `src/quantcraft/research/parameter_exploration.py`

**Step 1: Write failing tests**

Update helper strategies to use `StrategyConfig`:

```python
class NoTradeConfig(StrategyConfig):
    x: int = 1


class NoTradeStrategy(Strategy[NoTradeConfig]):
    def on_bar(self, bar) -> None:
        pass
```

Assert constructor signature:

```python
ParameterStudy(engine=engine, bars=bars, strategy=NoTradeStrategy)
```

Assert `strategy_factory` is not accepted:

```python
with pytest.raises(TypeError):
    ParameterStudy(engine=engine, bars=bars, strategy_factory=lambda p: NoTradeStrategy())
```

Assert `strategy` must be a `Strategy` class, not an instance, arbitrary object,
or non-`Strategy` class.

Assert empty search space:

```python
result = study.grid_search(parameters={})
assert result.candidate_count == 1
assert result.rows[0].candidate_parameters == {}
assert result.rows[0].strategy_config == {"x": 1}
```

Assert unknown config field preflight:

```python
with pytest.raises(StrategyConfigValidationError, match="unknown"):
    study.grid_search(parameters={"missing": [1]})
```

Use a counting engine to assert no `engine.run(...)` call occurred.

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/unit/research/test_parameter_study_preflight.py tests/unit/research/test_parameter_grid_validation.py -q
```

Expected: failures because current constructor requires `strategy_factory`,
empty grids fail, and rows expose `parameters`.

**Step 3: Implement constructor and preflight**

In `ParameterStudy`:

- Change slots to `("engine", "bars", "strategy")`.
- Constructor accepts `strategy: type[Strategy]`.
- Validate engine and bars as before.
- Validate `strategy` is a class and `issubclass(strategy, Strategy)`.
- Store the strategy class.
- Remove `StrategyFactory`.
- Keep grid validation for mapping, ordered sequences, duplicate values,
  finite floats, unsupported scalar types, and `max_candidates`.
- Allow `parameters={}` and have `_iter_candidates` yield one
  `(0, {})` candidate.
- Add a preflight function that verifies every non-empty parameter key is a
  public declared config field on `strategy.config_type`.
- For candidate value type validation, materialize config snapshots before
  execution using `strategy.config_type(**candidate)`.

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/unit/research/test_parameter_study_preflight.py tests/unit/research/test_parameter_grid_validation.py -q
```

Expected: pass.

### Task 4: Implement Config-Aware Candidate Flow And Constraint Semantics

**Files:**
- Modify: `tests/unit/research/test_parameter_grid_validation.py`
- Modify: `tests/integration/research/test_parameter_study_grid_search.py`
- Modify: `tests/integration/research/test_parameter_study_failures.py`
- Modify: `src/quantcraft/research/parameter_exploration.py`

**Step 1: Write failing tests**

Add or rewrite tests for:

- `constraint` receives full `strategy_config` mapping, including defaults.
- Mutating the mapping inside `constraint` fails or cannot affect stored rows.
- `constraint=False` creates a rejected row with
  `rejection_stage="constraint"`.
- `constraint` non-bool return creates failed row with
  `failure_stage="constraint"`.
- `constraint` exception creates failed row with
  `failure_stage="constraint"`.
- `fail_fast=True` re-raises constraint exceptions with notes including:

```text
stage=constraint
candidate_parameters={...}
strategy_config={...}
```

- `StrategyConfig.validate()` failure creates rejected row with
  `rejection_stage="strategy_config"`, records `error_type` and
  `error_message`, and does not call `engine.run(...)`.

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/unit/research/test_parameter_grid_validation.py tests/integration/research/test_parameter_study_grid_search.py tests/integration/research/test_parameter_study_failures.py -q
```

Expected: failures until candidate flow is rewritten.

**Step 3: Implement candidate flow**

In `grid_search(...)`:

- Validate grid, `max_candidates`, and objective before candidate iteration.
- For each candidate:
  - build `candidate_parameters = MappingProxyType(dict(candidate))`
  - materialize `config = self.strategy.config_type(**candidate)`
  - on `StrategyConfigValidationError`, append rejected row with
    `rejection_stage="strategy_config"`
  - convert `config.to_mapping()` to immutable `strategy_config`
  - call `constraint(strategy_config)` if present
  - on `False`, append rejected row with `rejection_stage="constraint"`
  - on constraint exception/non-bool, use `_raise_or_record(...)` with
    `failure_stage="constraint"`
  - construct `strategy_instance = self.strategy(config)`
  - on construction exception, use `failure_stage="strategy_construction"`
  - call `engine.run(bars=self.bars, strategy=strategy_instance, label=...)`
  - extract metrics
  - append success row

Do not call `constraint` before config materialization.

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/unit/research/test_parameter_grid_validation.py tests/integration/research/test_parameter_study_grid_search.py tests/integration/research/test_parameter_study_failures.py -q
```

Expected: pass.

### Task 5: Rewrite Integration Study Contracts

**Files:**
- Modify: `tests/integration/research/test_parameter_study_grid_search.py`
- Modify: `tests/integration/research/test_parameter_study_selected_run.py`
- Modify: `tests/integration/research/test_parameter_study_metric_states.py`
- Modify: `tests/integration/research/test_parameter_study_canonical_grid_contract.py`
- Modify: `tests/smoke/local/test_public_beta_examples.py`
- Modify: `src/quantcraft/research/parameter_exploration.py`

**Step 1: Write failing tests**

Update parameterized strategies to receive config through:

```python
class RoundTripConfig(StrategyConfig):
    fast: int = 5
    slow: int = 20

    def validate(self) -> None:
        if self.fast >= self.slow:
            raise StrategyConfigValidationError("fast must be less than slow")


class ParameterizedRoundTripStrategy(Strategy[RoundTripConfig]):
    def init(self) -> None:
        self.fast = ta.sma(self.data.close, length=self.config.fast)
        self.slow = ta.sma(self.data.close, length=self.config.slow)
```

Assert fresh strategy instances indirectly by recording unique instance ids in
the engine calls or through strategy lifecycle state.

Update selected-run assertions:

```python
best = result.best()
assert dict(best.candidate_parameters) == {"fast": 5, "slow": 20}
assert dict(best.strategy_config) == {"fast": 5, "slow": 20}
```

Avoid using `report.run.strategy_parameters` as the canonical study config
source. If existing reporting still emits it until Stage 3, tests may assert it
only as legacy report behavior outside the Stage 2 study contract.

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/integration/research/test_parameter_study_selected_run.py tests/integration/research/test_parameter_study_metric_states.py tests/integration/research/test_parameter_study_canonical_grid_contract.py tests/smoke/local/test_public_beta_examples.py -q
```

Expected: failures until tests and implementation align.

**Step 3: Implement remaining integration fixes**

Update any helper, fixture, or assertion still depending on:

- `strategy_factory`
- `row.parameters`
- record `"parameters"`
- `failure_stage="strategy_factory"`

Use:

- `strategy=...`
- `row.candidate_parameters`
- `row.strategy_config`
- record `"candidate_parameters"`
- record `"strategy_config"`
- `failure_stage="strategy_construction"`

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/integration/research/test_parameter_study_selected_run.py tests/integration/research/test_parameter_study_metric_states.py tests/integration/research/test_parameter_study_canonical_grid_contract.py tests/smoke/local/test_public_beta_examples.py -q
```

Expected: pass.

### Task 6: Update Public Docs And Active Specs

**Files:**
- Modify: `docs/site/guides/parameter-exploration.md`
- Modify: `docs/site/examples.md`
- Modify: `docs/site/reference/public-api.md`
- Modify: `docs/site/quickstart.md` only if it references parameter study
- Modify: `docs/product-specs/strategy-configuration-contract.md`
- Modify: `docs/product-specs/strategy-configuration-contract-test-scenarios.md`
- Modify: `docs/product-specs/parameter-exploration.md`
- Modify: `docs/product-specs/parameter-exploration-test-scenarios.md`
- Modify: `docs/product-specs/wfa-prerequisite-roadmap.md` only if needed to
  close the Stage 2 compatibility open question

**Step 1: Update docs**

Replace public examples like:

```python
ParameterStudy(
    engine=engine,
    bars=bars,
    strategy_factory=lambda p: SmaCross(fast=p["fast"], slow=p["slow"]),
)
```

with:

```python
class SmaConfig(StrategyConfig):
    fast: int = 5
    slow: int = 20

    def validate(self) -> None:
        if self.fast >= self.slow:
            raise StrategyConfigValidationError("fast must be less than slow")


class SmaCross(Strategy[SmaConfig]):
    ...


study = ParameterStudy(engine=engine, bars=bars, strategy=SmaCross)
```

Document:

- `parameters` as search space input only
- `candidate_parameters` as partial row override
- `strategy_config` as full row snapshot
- `constraint` as optional study-level pruning over full `strategy_config`
- `StrategyConfig.validate()` as domain invariant hook
- `parameters={}` default-config run
- no `strategy_factory` compatibility path

Do not rewrite historical plan files only to erase past decisions.

**Step 2: Run docs checks**

Run:

```bash
uv run poe repo-check
```

Expected: pass or actionable docs/structure failures to fix.

### Task 7: Search Cleanup And Full Verification

**Files:**
- Potentially modify any active source/docs/tests found by search.
- Update: this plan's `## Evaluator Review` section after verification.

**Step 1: Search for removed active API**

Run:

```bash
rg -n "strategy_factory" src tests docs/site README.md
rg -n "row\\.parameters|\\[\"parameters\"\\]|failure_stage=.*strategy_factory" src tests docs/site README.md
```

Expected:

- No `strategy_factory` in active source, active tests, public docs, or README.
- No row-level `.parameters` assertions.
- No record-level `"parameters"` for grid rows.
- Historical docs under `docs/plans` and product docs may retain explicit
  historical references only where needed to explain the migration background.

**Step 2: Run full verification**

Run:

```bash
uv run poe verify
uv run poe verify-runtime
```

Expected: pass.

**Step 3: Evaluator review**

Update `## Evaluator Review` with:

- findings first
- verification evidence with command outputs summarized
- final disposition

## Evaluator Review

- Findings: No blocker or important issues remain after the final evaluator
  pass.
- Scope review:
  - `ParameterStudy` now accepts `strategy=StrategyClass` and no active
    `strategy_factory` construction path remains.
  - `GridSearchRow.parameters` and record `"parameters"` were removed from the
    active grid-search row contract. Rows now expose `candidate_parameters` and
    full `strategy_config`.
  - `StrategyConfig.validate()` runs during materialization after primitive
    field validation. Validation failures become rejected rows with
    `rejection_stage="strategy_config"` and no backtest execution.
  - `constraint` receives immutable full `strategy_config` mappings and
    `False` outcomes become rejected rows with
    `rejection_stage="constraint"`.
  - Failed-row stages now use `strategy_construction`, `backtest`,
    `constraint`, and `metric_extraction`.
  - Public docs, smoke examples, active tests, and active product specs were
    updated away from the removed factory-centered API.
  - Historical plan files were not rewritten merely to erase audit history.
  - Stage 3 reporting cleanup and WFA implementation remain out of scope.
- Independent review evidence:
  - Product/spec/plan alignment reviewer found no blocker or important issues
    after checking the Stage 2 goal, active specs, plan, and implemented API.
  - Testing/spec reviewer initially found active-spec drift around old callable
    construction and unresolved constraint row semantics. Those issues were
    fixed in the product and test specs, then re-reviewed with no remaining
    blocker or important findings.
  - Architecture/maintainability reviewer initially found research code
    reaching into `StrategyConfig` internals and active docs preserving legacy
    callable/factory paths. `StrategyConfig` now owns override-name validation
    and diagnostic mapping, research uses those canonical helpers, and
    re-review found no remaining blocker or important findings.
  - Final narrow third-party review confirmed
    `strategy-configuration-contract.md` and
    `strategy-configuration-contract-test-scenarios.md` now resolve Stage 2
    semantics consistently: constraints receive full `strategy_config`;
    constraint-rejected and runtime-failed rows expose materialized
    `strategy_config`; no active legacy callable/factory path remains.
- Simplification pass evidence:
  - A behavior-preserving `code-simplifier` pass replaced the mixed
    tuple-or-row `prepared_candidates` flow with an explicit
    `_RunnableCandidate` value object and `_prepare_candidate(...)` helper.
    This keeps the same two-phase guarantee that all strategy config
    materialization happens before any constraint/backtest execution, while
    making candidate preparation and candidate execution easier to reason
    about independently.
  - Targeted simplification verification passed:
    `uv run pytest tests/unit/research/test_parameter_grid_validation.py tests/integration/research/test_parameter_study_failures.py tests/integration/research/test_parameter_study_grid_search.py -q`
    returned `41 passed`.
  - `uv run mypy src` passed after the simplification.
- Auto-fail search evidence:
  - `rg -n "strategy_factory" src tests docs/site README.md` returned no
    matches.
  - `rg -n "row\\.parameters|\\[\"parameters\"\\]|failure_stage=.*strategy_factory" src tests docs/site README.md`
    returned no matches.
  - `rg -n "_field_for_override|__config_fields__" src/quantcraft/research/parameter_exploration.py`
    returned no matches.
  - `rg -n 'Factory-based|factory paths|legacy callable construction API remains|advanced.*old callable|old callable.*advanced|strategy_factory|strategy factory' docs/product-specs docs/site README.md src tests`
    returned no matches.
  - `rg -n 'whether constraints receive|whether constraint-rejected|Stage 2, do constraints|Stage 2, should constraint' docs/product-specs/strategy-configuration-contract.md docs/product-specs/strategy-configuration-contract-test-scenarios.md`
    returned no matches.
- Targeted verification evidence:
  - `uv run pytest tests/unit/strategy/test_strategy_config_materialization.py tests/unit/research/test_parameter_grid_validation.py -q`
    passed with `51 passed` after adding the config canonical-helper and
    strategy-config rejection coverage.
  - `uv run pytest tests/unit/strategy/test_strategy_config_materialization.py tests/unit/research/test_parameter_grid_validation.py tests/unit/research/test_grid_search_records.py tests/unit/research/test_grid_search_result_selection.py tests/unit/research/test_parameter_study_preflight.py tests/integration/research/test_parameter_study_grid_search.py tests/integration/research/test_parameter_study_failures.py tests/integration/research/test_parameter_study_selected_run.py tests/integration/research/test_parameter_study_metric_states.py tests/integration/research/test_parameter_study_canonical_grid_contract.py tests/smoke/local/test_public_beta_examples.py -q`
    passed earlier in the evaluator pass before the final review-driven test
    additions.
- Full verification evidence:
  - `uv run poe verify-runtime` passed on the final working tree after the
    last documentation fixes:
    - `ruff check .`: all checks passed.
    - `mypy src`: success, no issues in 59 source files.
    - `pytest -q`: `684 passed, 4 skipped`.
    - `coverage_check.py`: coverage policy check passed.
    - `uv build`: source distribution and wheel built successfully.
    - `repo_check.py`: repository checks passed.
    - `notebook_validate.py`: five notebooks validated.
    - `pytest tests/perf -q -x --run-perf`: `3 passed`.
  - `uv run poe repo-check` passed separately on the final working tree:
    `repository checks passed`.
  - `uv run poe test-live` passed separately on the final working tree:
    `1 passed`.
  - `uv run poe live-smoke` passed separately on the final working tree:
    `binance:spot:3`, `binance:usdm:3`, `bybit:spot:3`, and
    `bitget:spot:3`.
- Final disposition: Accepted for this Stage 2 working-tree implementation.
