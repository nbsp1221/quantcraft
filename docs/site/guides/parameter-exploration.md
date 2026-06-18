# Parameter Exploration

`ParameterStudy` runs a finite grid of strategy parameters against a
materialized series.

```python
from quantcraft.research import ParameterStudy, qc, ta
from quantcraft.strategy import Strategy, StrategyConfig, StrategyConfigValidationError


class SmaConfig(StrategyConfig):
    fast: int = 2
    slow: int = 3

    def validate(self) -> None:
        if self.fast >= self.slow:
            raise StrategyConfigValidationError("fast must be less than slow")


class ParameterizedSmaStrategy(Strategy[SmaConfig]):
    def init(self) -> None:
        self.fast = ta.sma(self.data.close, length=self.config.fast)
        self.slow = ta.sma(self.data.close, length=self.config.slow)

    def on_bar(self, bar) -> None:
        if qc.is_na(self.fast[0]) or qc.is_na(self.slow[0]):
            return
        if qc.crossover(self.fast, self.slow):
            self.buy(quantity=1.0)
        elif self.position.is_open and qc.crossunder(self.fast, self.slow):
            self.sell(quantity=1.0)


grid = ParameterStudy(
    engine=engine,
    bars=bars,
    strategy=ParameterizedSmaStrategy,
).grid_search(
    parameters={"fast": [2, 3], "slow": [3, 4]},
    constraint=lambda config: config["fast"] < config["slow"],
    objective=("returns.total_return", "max"),
)

records = grid.to_records()
best = grid.best()
selected_config = best.strategy_config
selected_report = best.backtest.report if best.backtest is not None else None
```

Grid search is a research diagnostic. It is not an optimizer guarantee or a
trading recommendation.
