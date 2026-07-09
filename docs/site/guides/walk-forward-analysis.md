# Walk-Forward Validation

`WalkForwardValidation` checks whether settings selected on one training window
also survive the next unseen OOS windows. It is the first public flow built on
Quantcraft's validation pipeline reset.

Use it after a small strategy-parameter search space is worth challenging. It is
validation evidence, not an optimizer guarantee, trading recommendation,
paper-trading loop, live-trading loop, or continuous account simulation.

```python
from quantcraft.backtest import BacktestEngine, CostConfig
from quantcraft.data import DataFrameDataSource
from quantcraft.research import RollingSplitPolicy, WalkForwardValidation, qc, ta
from quantcraft.strategy import Strategy, StrategyConfig, StrategyConfigValidationError


class SmaConfig(StrategyConfig):
    fast: int = 5
    slow: int = 20

    def validate(self) -> None:
        if self.fast >= self.slow:
            raise StrategyConfigValidationError("fast must be less than slow")


class SmaCross(Strategy[SmaConfig]):
    def init(self) -> None:
        self.fast_ma = ta.sma(self.data.close, length=self.config.fast)
        self.slow_ma = ta.sma(self.data.close, length=self.config.slow)

    def on_bar(self, bar) -> None:
        if qc.crossover(self.fast_ma, self.slow_ma):
            self.buy(qty_percent=1.0)
        elif self.position.is_open and qc.crossunder(self.fast_ma, self.slow_ma):
            self.sell(qty_percent=1.0)


bars = DataFrameDataSource(frame=df, symbol="BTC/USDT", timeframe="1h").load()
engine = BacktestEngine(
    initial_cash=10_000.0,
    costs=CostConfig(tick_size=0.01, slippage_ticks=0.0, fee_rate=0.0),
)

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

fold_records = result.to_records()
candidate_records = result.to_candidate_records()
diagnostics = result.diagnostics
```

The first validation workflow is intentionally narrow:

- input is one materialized `BarSeries`
- folds use bar-count windows through `RollingSplitPolicy`
- mode is rolling only
- users pass the objective directly as `(metric_path, "max" | "min")`
- metric-selection internals are not public
- successful folds retain train/OOS evidence through validation artifacts and
  provenance

Do not read fold summaries as a stitched portfolio, live-equivalent account, or
future-performance claim.
