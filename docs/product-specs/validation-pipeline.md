# Validation Pipeline Beta Reset

- Status: governing
- Scope: current first-slice research validation substrate and WFA public flow
- Supersedes for current research-validation work:
  - `parameter-exploration.md`
  - `parameter-exploration-test-scenarios.md`
  - `walk-forward-analysis-resume.md`
  - `walk-forward-analysis-resume-test-scenarios.md`

## Summary

Quantcraft's research layer is reset around a validation pipeline substrate. The
first slice intentionally breaks the earlier beta `ParameterStudy`, `GridSearch*`,
`WalkForwardStudy`, and old WFA dataclass public APIs. Compatibility wrappers,
deprecated aliases, and migration shims are not part of this contract.

The current first-slice public research validation surface is:

- `ValidationPipeline`
- `ValidationStep`
- `ValidationContext`
- `ValidationReport`
- `ValidationStepResult`
- `ValidationDiagnostic`
- `ValidationProvenance`
- `ValidationArtifact`
- `ValidationStatus`
- `SplitWindow`
- `RollingSplitPolicy`
- `WalkForwardValidation`
- `WalkForwardValidationResult`
- `WalkForwardFoldResult`

`MetricSelectionPolicy` is intentionally not public. Users configure WFA
selection by passing an objective tuple directly to `WalkForwardValidation`.

Supported first-slice objective metric paths are:

- `equity.final`
- `returns.total_return`
- `risk.max_drawdown`
- `risk.sharpe_ratio`
- `trades.closed_count`
- `trades.win_rate`
- `trades.profit_factor`
- `costs.total_fees`
- `exposure.ratio`
- `execution.order_rejection_count`

## Non-Goals

This first slice does not include:

- public `MetricSelectionPolicy`;
- compatibility wrappers for old beta study APIs;
- Monte Carlo, bootstrap, purged CV, multiple-testing, cost-sensitivity, trust
  reports, promotion gates, paper/live, shorting, leverage, or margin;
- placeholder source modules for deferred validation features;
- changes to `BacktestEngine`, `Strategy`, or `StrategyConfig` semantics.

## Validation Pipeline Contract

`ValidationStep` is the public extension seam:

```python
class ValidationStep(Protocol):
    name: str

    def run(self, context: ValidationContext) -> ValidationStepResult: ...
```

`ValidationPipeline` is strict and linear in the first slice:

```python
pipeline = ValidationPipeline([step_a, step_b])
report = pipeline.run(source=bars, strategy=StrategyClass, config=config, engine=engine)
```

Pipeline execution rules:

- steps execute in the order supplied;
- `success` continues;
- `inconclusive` continues;
- `rejected` stops the pipeline;
- `failed` stops the pipeline;
- later unexecuted steps are recorded as `skipped` with diagnostic code
  `pipeline_step_skipped_after_stop`;
- duplicate artifact names across step results fail during report aggregation.

## Result Contract

Validation result objects expose structured evidence:

- `summary`: compact machine-readable metrics;
- `records`: row-shaped export records;
- `diagnostics`: warnings, errors, skip reasons, or rejection details;
- `artifacts`: named in-memory artifacts such as backtest results or fold data;
- `provenance`: typed sections for strategy, data, objective, split,
  candidates, selection, and runs.

WFA and candidate-selection provenance must include objective metric/direction,
split window data, raw/eligible/rejected/failed candidate counts, selected
candidate identity/config, and train/OOS run labels when applicable.

## Walk-Forward Validation Contract

The first public WFA flow is `WalkForwardValidation`:

```python
validation = WalkForwardValidation(
    engine=engine,
    bars=bars,
    strategy=SmaCross,
    split_policy=RollingSplitPolicy(train_size=120, test_size=30),
    objective=("returns.total_return", "max"),
)

result = validation.run(
    parameters={"fast": [5, 10, 20], "slow": [30, 50, 100]},
    constraint=lambda config: config["fast"] < config["slow"],
)
```

`RollingSplitPolicy` produces start-inclusive/end-exclusive train/test windows.
The default `step_size` is `test_size`.
Window index fields are start-inclusive/end-exclusive. Timestamp end fields
(`train_end_timestamp`, `test_end_timestamp`) name the last included bar in
that window, not the exclusive end boundary.

`WalkForwardValidationResult.to_records()` returns fold records.
`WalkForwardValidationResult.to_candidate_records()` returns train-candidate
records enriched with fold window fields.
Successful fold OOS `BacktestResult` artifacts are available both under the
owning fold's `artifacts` map and under the top-level result `artifacts` map
using names such as `walk_forward_fold_0_oos_backtest`.
Candidate search remains a research diagnostic, not an optimizer guarantee or a trading recommendation.

## Public Documentation Requirements

Current public documentation must describe `WalkForwardValidation` and the
validation pipeline surface, not `ParameterStudy` or `WalkForwardStudy` as the
current public API. Historical planning docs may remain historical, but current
README, site guides, reference docs, and examples must route users to this
contract.
