from __future__ import annotations

from typing import ClassVar

from quantleet.backtest import BacktestEngine
from quantleet.data import BarSeries, TimeBar
from quantleet.research import GridSearchResult, WalkForwardStudy
from quantleet.strategy import Strategy, StrategyConfig, StrategyConfigValidationError
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent


def crossing_bars(length: int = 12) -> BarSeries:
    closes = tuple(100.0 + ((index % 4) - 1) * 2.0 + index for index in range(length))
    return BarSeries(
        symbol="TEST",
        timeframe="1m",
        bar_type="time",
        rows=tuple(
            TimeBar(
                timestamp=(index + 1) * 60,
                open=close,
                high=close + 1.0,
                low=close - 1.0,
                close=close,
                volume=1.0,
            )
            for index, close in enumerate(closes)
        ),
    )


def engine() -> BacktestEngine:
    return BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )


class WfaRoundTripConfig(StrategyConfig):
    fast: int = 2
    slow: int = 4

    def validate(self) -> None:
        if self.fast >= self.slow:
            raise StrategyConfigValidationError("fast must be less than slow")


class WfaRoundTripStrategy(Strategy[WfaRoundTripConfig]):
    constructed_count: ClassVar[int] = 0
    instance_numbers: ClassVar[list[int]] = []
    constructed_configs: ClassVar[list[dict[str, object]]] = []

    def __init__(self, config: WfaRoundTripConfig | None = None) -> None:
        super().__init__(config)
        type(self).constructed_count += 1
        type(self).instance_numbers.append(type(self).constructed_count)
        type(self).constructed_configs.append(self.config.to_mapping())

    def init(self) -> None:
        self._seen = 0

    def on_bar(self, bar: BarEvent) -> None:
        self._seen += 1
        if self._seen == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen >= 2 and self.position.is_open:
            self.sell(quantity=1.0, tag="exit")


def test_canonical_rolling_wfa_workflow_composes_real_public_contracts() -> None:
    WfaRoundTripStrategy.constructed_count = 0
    WfaRoundTripStrategy.instance_numbers = []
    WfaRoundTripStrategy.constructed_configs = []

    result = WalkForwardStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy=WfaRoundTripStrategy,
    ).run(
        parameters={"fast": [2, 3], "slow": [3, 5]},
        objective=("returns.total_return", "max"),
        constraint=lambda config: config["fast"] < config["slow"],
        train_size=6,
        test_size=3,
    )

    assert result.fold_count == 2
    assert result.successful_fold_count == 2
    assert all(isinstance(fold.train_result, GridSearchResult) for fold in result.folds)
    assert all(fold.selected_test_result is not None for fold in result.folds)
    assert all(fold.selected_config is not None for fold in result.folds)
    assert all(
        fold.selected_test_result is not None
        and fold.selected_test_result.report.run.strategy_config == dict(fold.selected_config or {})
        for fold in result.folds
    )
    assert len(WfaRoundTripStrategy.constructed_configs) > result.execution_scale.fold_count
    assert all(fold.selected_test_result is not None for fold in result.folds)
    assert result.to_records()[0]["selected_config"] == dict(result.folds[0].selected_config or {})


def test_wfa_selection_uses_train_result_and_selected_test_config_snapshot() -> None:
    result = WalkForwardStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy=WfaRoundTripStrategy,
    ).run(
        parameters={"fast": [2, 3], "slow": [3, 5]},
        objective=("returns.total_return", "max"),
        train_size=6,
        test_size=3,
    )

    first_fold = result.folds[0]

    assert first_fold.selected_train_row is not None
    assert first_fold.selected_config == first_fold.selected_train_row.strategy_config
    assert first_fold.selected_test_result is not None
    assert first_fold.selected_test_result.report.run.strategy_config == dict(
        first_fold.selected_config or {}
    )
