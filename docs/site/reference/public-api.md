# Public API Reference

This curated reference lists the first-beta imports users should prefer.

## Data

- `quantcraft.data.TimeBar`
- `quantcraft.data.BarSeries`
- `quantcraft.data.DataFrameDataSource`
- `quantcraft.data.CSVDataSource`
- `quantcraft.data.CCXTDataSource`

## Backtesting

- `quantcraft.backtest.BacktestEngine`
- `quantcraft.backtest.CostConfig`
- `quantcraft.backtest.BacktestResult`
- `BacktestResult.report`
- `BacktestResult.plot()`

`BacktestEngine.run(...)` accepts a strategy class plus an optional
`StrategyConfig` instance through `config=...`; plain dictionaries are not a
supported direct-run config input.

## Strategy Authoring

- `quantcraft.strategy.Strategy`
- `quantcraft.strategy.StrategyConfig`
- `Strategy.buy(...)`
- `Strategy.sell(...)`

## Research Validation

- `quantcraft.research.ValidationPipeline`
- `quantcraft.research.ValidationStep`
- `quantcraft.research.ValidationContext`
- `quantcraft.research.ValidationReport`
- `quantcraft.research.ValidationStepResult`
- `quantcraft.research.ValidationDiagnostic`
- `quantcraft.research.ValidationProvenance`
- `quantcraft.research.ValidationArtifact`
- `quantcraft.research.ValidationStatus`
- `quantcraft.research.SplitWindow`
- `quantcraft.research.RollingSplitPolicy`
- `quantcraft.research.WalkForwardValidation`
- `quantcraft.research.WalkForwardValidationResult`
- `quantcraft.research.WalkForwardFoldResult`
- `quantcraft.research.ta`
- `quantcraft.research.qc`

`WalkForwardValidation` is a research validation workflow. It uses rolling
train/test folds over one materialized `BarSeries`; it is not a live trading,
paper trading, optimizer-guarantee, or continuous-account reporting surface.

`MetricSelectionPolicy` is not public in the first validation slice. Users pass
objective tuples directly to `WalkForwardValidation`.

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

Lower-level trading-domain objects are supporting implementation contracts, not
the primary first-beta import surface for user documentation.
