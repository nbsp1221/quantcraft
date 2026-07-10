# Validation Pipeline Architecture Research

- Date: 2026-07-09
- Status: advisory research
- Canonical: no
- Scope: local source review of validation, optimization, splitting, simulation, and reporting architecture in representative backtesting and quant research libraries

## Summary

Quantcraft should not differentiate by adding a longer checklist of isolated
validation helpers. The stronger opportunity is to make strategy validation a
composable, inspectable, and reproducible developer workflow.

The market scan supports an architecture-first direction:

> Build a validation pipeline substrate before adding more validation features.

The substrate should let users compose studies, split policies, cost scenarios,
Monte Carlo simulations, diagnostics, artifacts, and provenance under one
consistent result contract. Only after that foundation exists should Quantcraft
add richer judgment layers such as pass/fail gates, promotion rules, or trust
reports.

This report is advisory. It records market evidence and design implications. It
does not change Quantcraft's product contract by itself.

## Reviewed Libraries

This review used local source checkouts under `/tmp/quantcraft-market-research`
for:

- `freqtrade`
- `backtesting.py`
- `vectorbt`
- `quantstats`
- `pyfolio`
- `empyrical`
- `mlfinlab`
- `nautilus_trader`

The review focused on how these projects structure validation, optimization,
splitting, configuration, result objects, metrics, and extension seams.

## Main Finding

Most tools have validation-related features, but those features are usually tied
to one of three shapes:

1. command-level workflows, such as backtest, hyperopt, lookahead analysis, or
   recursive analysis;
2. analysis helpers, such as splitters, optimization helpers, Monte Carlo
   helpers, or risk metric functions;
3. platform orchestration, where data, venues, strategies, and backtest runs are
   configured as explicit run specifications.

The useful design lesson is not to copy any single feature. The useful lesson is
that Quantcraft needs first-class architecture for evidence generation:

- reusable split policies;
- reusable selection policies;
- validation steps with preconditions and diagnostics;
- consistent result records;
- explicit artifacts;
- provenance for data, config, strategy, selected candidates, and trial counts;
- clear separation between evidence generation and final judgment.

## Library Lessons

### Freqtrade: Analysis Modes Are Separate From Normal Backtesting

Freqtrade separates general backtesting from specialized analysis commands such
as lookahead analysis and recursive analysis. Its lookahead workflow compares a
baseline backtest against sliced or perturbed runs to detect biased signals. Its
recursive analysis varies startup candle counts to detect unstable indicator
behavior.

Useful patterns:

- validation is a separate mode, not hidden inside the main backtest engine;
- analysis flows can force safer settings before execution;
- validation steps can declare preconditions, such as minimum trade counts;
- baseline-versus-variant comparison is a reusable validation pattern;
- analysis results should preserve both failure and rejection reasons.

Quantcraft implication:

- Do not push validation behavior into `BacktestEngine` directly.
- Model validation as explicit steps that can run baseline and variant backtests.
- Return structured diagnostics instead of only raising errors or returning raw
  booleans.

### Vectorbt: Split Policies Should Be Reusable Objects

Vectorbt exposes reusable splitters for range, rolling, expanding, and related
split patterns. The important architectural move is that splitting is not owned
by one walk-forward function. The split policy can be reused across different
analyses.

Useful patterns:

- split generation is a separate abstraction;
- train/test or set semantics can be represented independently of the backtest;
- splitters are useful beyond walk-forward analysis.

Quantcraft implication:

- `WalkForwardStudy` should not be the only owner of rolling window logic.
- Quantcraft should introduce `SplitPolicy` concepts before adding more
  validation studies.
- Future studies such as OOS testing, purged cross-validation, cost sensitivity,
  and bootstrap analysis should be able to reuse the same split contract.

### NautilusTrader: Config-First Orchestration Enables Reproducibility

NautilusTrader uses explicit run configuration objects for backtest nodes,
venues, data, actors, strategies, and execution settings. It is much heavier
than Quantcraft should be at beta scale, but its orchestration model is a strong
reference for reproducible runs.

Useful patterns:

- execution inputs are explicit configuration objects;
- run orchestration is separated from engine internals;
- multiple runs can be represented as a batch of run configurations;
- config validation happens before execution;
- venue, data, strategy, and execution settings are separable concerns.

Quantcraft implication:

- Validation pipelines should be config/spec driven.
- Each run should be traceable by strategy config, data identity, split policy,
  cost scenario, objective, and selection rule.
- Provenance should be part of the result contract, not an afterthought.

### Backtesting.py: Ergonomics Still Matter

`backtesting.py` keeps optimization ergonomics compact. Its optimization surface
is easy to understand because common concepts such as objective, constraint,
method, maximum tries, random state, and optional heatmap output are exposed in a
small API.

Useful patterns:

- simple APIs lower the cost of first use;
- objective and constraint hooks are natural extension points;
- optional inspection outputs are useful for research workflows.

Quantcraft implication:

- A validation pipeline should not become a verbose enterprise configuration
  system.
- The public API should remain readable from a notebook or small script.
- Advanced validation should be composable without making the first valid example
  look intimidating.

### QuantStats: Simulation Results Need Interpretation Objects

QuantStats includes Monte Carlo helpers that do more than return raw simulated
paths. The project emphasizes summary statistics, probabilities, percentiles,
confidence bands, and plotting-oriented outputs.

Useful patterns:

- simulation output should be packaged for interpretation;
- users need summary statistics and probability estimates, not just arrays;
- visualization or tabular export should be easy after simulation.

Quantcraft implication:

- Future Monte Carlo support should return a result object with paths, summary,
  percentiles, drawdown distribution, probability estimates, diagnostics, and
  records.
- Monte Carlo should be one validation step in a pipeline, not an isolated helper
  that cannot share context or provenance.

### MLFinLab: Advanced Validation Needs Explicit Trial And Leakage Semantics

MLFinLab's public repository contains many incomplete or placeholder
implementations, but its vocabulary is still valuable. It names concepts such as
purged k-fold cross-validation, combinatorial purged k-fold, embargo, information
sets, haircut Sharpe ratios, profit hurdles, and multiple-testing adjustments.

Useful patterns:

- advanced validation requires explicit leakage boundaries;
- cross-validation should be represented as a generator or policy;
- multiple-testing adjustments require trial-count and search-space information;
- statistical judgment is unsafe without provenance for how a candidate was
  selected.

Quantcraft implication:

- Quantcraft should not add advanced statistical claims before it can record how
  many candidates were searched and how winners were selected.
- Candidate count, search space, selected-from population, objective, and
  rejection lineage should become first-class provenance data.
- Purging and embargo should be modeled as split policies, not hard-coded into a
  single study.

### Pyfolio And Empyrical: Metrics Are A Separate Layer

Pyfolio and Empyrical are mainly portfolio analytics and risk metric layers, not
full validation pipeline systems. Their value is in reusable metric computation
and report generation.

Useful patterns:

- metric computation is separable from execution;
- report generation is separable from raw backtest mechanics;
- reusable metrics should not own orchestration.

Quantcraft implication:

- Keep metric extraction, validation orchestration, and reporting as separate
  concerns.
- Validation steps may consume metrics, but metrics should not define the whole
  validation architecture.

## Quantcraft Architecture Implications

Quantcraft already has useful research pieces, especially parameter studies,
walk-forward analysis, structured rows, status fields, and record export. Those
pieces should be treated as evidence, not as compatibility constraints.

Because Quantcraft is still beta and has little real user pressure, API
compatibility should not dominate this redesign. Existing research APIs should
survive only when they naturally fit the new architecture. If they force awkward
adapters, deprecated aliases, or preservation of weak concepts, they should be
removed or rewritten.

The recommended principle is:

> Beta reset, architecture first, value first.

## Recommended Validation Vocabulary

The following vocabulary is the best fit for Quantcraft:

- `Study`: a standalone research operation, such as parameter search or
  walk-forward analysis.
- `Step`: a pipeline unit that produces validation evidence.
- `Pipeline`: orchestration of multiple validation steps.
- `Context`: shared execution inputs and artifacts.
- `Record`: row-shaped export data.
- `Diagnostic`: warning, information, rejection reason, or failure detail.
- `Artifact`: reusable output from a step.
- `Policy`: replaceable rule, such as split, selection, or judgment behavior.
- `Scenario`: a controlled variant, such as cost, slippage, bootstrap, or Monte
  Carlo assumptions.
- `Provenance`: trace data describing where a result came from.

## Recommended Package Shape

A likely package shape is:

```text
quantcraft.research.validation
  context.py
  diagnostics.py
  pipeline.py
  provenance.py
  results.py
  scenarios.py
  selectors.py
  splits.py
  steps.py
```

This package should start small. Its first job is not to implement every
validation method. Its first job is to make future validation methods share one
language and result contract.

## Recommended Core Interfaces

A minimal first design could include:

```python
class ValidationContext:
    source: DataSource | BarSeries
    strategy: type[Strategy]
    config: StrategyConfigInstance
    engine: BacktestEngine
    artifacts: dict[str, object]
```

```python
class ValidationStep(Protocol):
    name: str

    def run(self, context: ValidationContext) -> ValidationStepResult:
        ...
```

```python
class ValidationStepResult:
    name: str
    status: Literal["success", "rejected", "failed", "skipped"]
    summary: Mapping[str, object]
    records: list[Mapping[str, object]]
    diagnostics: list[Diagnostic]
    artifacts: Mapping[str, object]
    provenance: Provenance
```

```python
class SplitPolicy(Protocol):
    def split(self, bars: BarSeries) -> Sequence[SplitWindow]:
        ...
```

These examples are directional, not final product contracts.

## Recommended Implementation Sequence

The recommended sequence is:

1. record this research;
2. define validation vocabulary, package structure, and interface contracts;
3. audit the existing research subsystem as remove, rewrite, or reuse material;
4. introduce the new validation core;
5. rebuild or remove existing parameter and walk-forward APIs according to the
   new model;
6. update docs, examples, and tests around the new API;
7. add validation features incrementally.

Feature expansion should follow the substrate:

1. validation core result model;
2. pipeline and step execution;
3. split policies;
4. parameter search under the new model;
5. walk-forward under the new model;
6. cost and slippage sensitivity;
7. baseline-versus-variant comparison;
8. Monte Carlo and bootstrap;
9. purged and embargoed split policies;
10. multiple-testing and profit-hurdle adjustments;
11. trust reports or promotion gates.

## Anti-Goals

The redesign should avoid:

- preserving weak beta APIs only for compatibility;
- adding isolated validation helpers before the shared substrate exists;
- hiding validation inside `BacktestEngine`;
- mixing metric calculation, orchestration, and reporting into one layer;
- claiming statistical confidence before trial counts and selection provenance are
  recorded;
- copying heavyweight platform complexity before Quantcraft needs it.

## Strategic Conclusion

The market does not need another generic backtesting library with a few extra
validation functions. Quantcraft's stronger path is to become a developer-first
strategy validation toolkit where evidence generation is composable,
inspectable, reproducible, and conservative by default.

The core differentiation is not the presence of walk-forward analysis, Monte
Carlo simulation, or cost sensitivity individually. The differentiation is the
consistent developer experience for combining those checks and understanding why
a strategy candidate deserves to move forward or be rejected.
