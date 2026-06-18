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

## Research

- `quantcraft.strategy.Strategy`
- `quantcraft.strategy.StrategyConfig`
- `Strategy.buy(...)`
- `Strategy.sell(...)`
- `quantcraft.research.ParameterStudy`
- `ParameterStudy.grid_search(...)`
- `quantcraft.research.WalkForwardStudy`
- `WalkForwardStudy.run(...)`
- `quantcraft.research.WalkForwardResult`
- `quantcraft.research.WalkForwardFold`
- `quantcraft.research.WalkForwardDiagnostic`
- `quantcraft.research.WalkForwardOosSummary`
- `quantcraft.research.WalkForwardExecutionScale`
- `quantcraft.research.ta`
- `quantcraft.research.qc`

`quantcraft.research.Strategy` remains available as a migration-compatible
re-export.

`WalkForwardStudy` is a research validation workflow. It uses rolling
train/test folds over one materialized `BarSeries`; it is not a live trading,
paper trading, optimizer-guarantee, or continuous-account reporting surface.

Lower-level trading-domain objects are supporting implementation contracts, not
the primary first-beta import surface for user documentation.
