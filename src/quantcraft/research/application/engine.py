from __future__ import annotations

from dataclasses import dataclass

from quantcraft.data import BarSeries
from quantcraft.data.domain import HistoricalDataSource
from quantcraft.research.application.backtest import BacktestResult, _run_backtest
from quantcraft.research.application.strategy import Strategy
from quantcraft.trading.domain.costs import CostConfig


@dataclass(frozen=True, slots=True)
class BacktestEngine:
    initial_cash: float
    costs: CostConfig

    def run(
        self,
        *,
        strategy: Strategy,
        bars: BarSeries | None = None,
        source: HistoricalDataSource | None = None,
    ) -> BacktestResult:
        if (bars is None) == (source is None):
            raise ValueError("provide exactly one of bars or source")

        if bars is not None:
            return _run_backtest(
                bars=_validated_bars(bars),
                strategy=strategy,
                initial_cash=self.initial_cash,
                costs=self.costs,
            )

        if source is None:
            raise ValueError("source must be provided")

        return _run_backtest(
            bars=_validated_bars(source.load()),
            strategy=strategy,
            initial_cash=self.initial_cash,
            costs=self.costs,
        )


def _validated_bars(bars: object) -> BarSeries:
    if not isinstance(bars, BarSeries):
        raise ValueError("bars must be a BarSeries instance")
    return bars
