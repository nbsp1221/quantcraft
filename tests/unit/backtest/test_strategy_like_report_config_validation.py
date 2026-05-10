from __future__ import annotations

import pytest

from quantleet.backtest import BacktestEngine
from quantleet.strategy import StrategyConfig
from quantleet.strategy.strategy import OHLCVDataView, PositionView, SeriesView
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent
from tests.integration.research.support_backtest_runner import fixture_bar_series


class _StrategyLikeWithoutConfig:
    _pending_order_requests: list[object]

    def __init__(self) -> None:
        self._reset_runtime_state()

    def _reset_runtime_state(self) -> None:
        self._pending_order_requests = []
        self.data = OHLCVDataView(
            open=SeriesView(()),
            high=SeriesView(()),
            low=SeriesView(()),
            close=SeriesView(()),
            volume=SeriesView(()),
        )
        self.position = PositionView()

    def init(self) -> None:
        pass

    @property
    def display_name(self) -> str | None:
        return None

    def _handle_bar(self, bar: BarEvent) -> None:
        pass


class _StrategyLikeWithDictConfig(_StrategyLikeWithoutConfig):
    def __init__(self) -> None:
        super().__init__()
        self.config = {}


class _InitialConfig(StrategyConfig):
    value: int = 1


class _ReplacementConfig(StrategyConfig):
    value: int = 2


class _ConfigReplacingStrategyLike(_StrategyLikeWithoutConfig):
    def __init__(self) -> None:
        super().__init__()
        self.config = _InitialConfig()

    def _handle_bar(self, bar: BarEvent) -> None:
        self.config = _ReplacementConfig()


def test_strategy_like_without_config_metadata_fails_before_report() -> None:
    with pytest.raises(ValueError, match="StrategyConfig config metadata"):
        _engine().run(
            bars=fixture_bar_series(),
            strategy=_StrategyLikeWithoutConfig(),
        )


def test_strategy_like_with_non_strategy_config_metadata_fails_before_report() -> None:
    with pytest.raises(ValueError, match="StrategyConfig config metadata"):
        _engine().run(
            bars=fixture_bar_series(),
            strategy=_StrategyLikeWithDictConfig(),
        )


def test_strategy_like_report_config_is_copied_before_runtime_mutation() -> None:
    result = _engine().run(
        bars=fixture_bar_series(),
        strategy=_ConfigReplacingStrategyLike(),
    )

    assert result.report.run.strategy_config == {"value": 1}


def _engine() -> BacktestEngine:
    return BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )
