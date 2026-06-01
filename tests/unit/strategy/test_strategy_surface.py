from __future__ import annotations

from inspect import signature

import pytest

from quantleet.backtest.strategy_runtime import _StrategyDriver
from quantleet.strategy import (
    Strategy,
    StrategyConfig,
    StrategyConfigMutationError,
    StrategyConfigValidationError,
)
from quantleet.trading.domain.events import BarEvent


class ThresholdConfig(StrategyConfig):
    threshold: float = 10.0


class ConfiguredStrategy(Strategy[ThresholdConfig]):
    def __init__(self, config: ThresholdConfig | None = None) -> None:
        super().__init__(config)
        self.seen_in_init: float | None = None
        self.seen_in_on_bar: float | None = None

    def init(self) -> None:
        self.seen_in_init = self.config.threshold

    def on_bar(self, bar: BarEvent) -> None:
        self.seen_in_on_bar = self.config.threshold


def _closed_bar(close: float = 12.0, *, symbol: str = "BTC/USDT") -> BarEvent:
    return BarEvent(
        bar_type="time",
        bar_spec="1m",
        symbol=symbol,
        timestamp=1,
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1.0,
        is_closed=True,
    )


def test_strategy_config_is_available_without_user_init_for_ordinary_strategy() -> None:
    class NoInitStrategy(Strategy[ThresholdConfig]):
        def init(self) -> None:
            self.initial_threshold = self.config.threshold

        def on_bar(self, bar: BarEvent) -> None:
            self.buy(quantity=1.0)

    strategy = NoInitStrategy()
    runtime = _StrategyDriver(strategy)

    runtime.initialize()
    runtime.handle_bar(_closed_bar())

    assert strategy.initial_threshold == 10.0
    assert strategy.config.to_mapping() == {"threshold": 10.0}
    assert len(runtime.order_state().pending) == 1


def test_strategy_accepts_explicit_config_instance() -> None:
    strategy = ConfiguredStrategy(ThresholdConfig(threshold=25.0))
    runtime = _StrategyDriver(strategy)

    runtime.initialize()
    runtime.handle_bar(_closed_bar())

    assert strategy.seen_in_init == 25.0
    assert strategy.seen_in_on_bar == 25.0


def test_config_less_strategy_has_empty_config_and_runtime_state() -> None:
    class EmptyStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(quantity=1.0)

    strategy = EmptyStrategy()
    runtime = _StrategyDriver(strategy)

    runtime.initialize()
    runtime.handle_bar(_closed_bar())

    assert strategy.config.to_mapping() == {}
    assert len(runtime.order_state().pending) == 1


def test_base_strategy_does_not_expose_parameters_reporting_hook() -> None:
    assert "parameters" not in Strategy.__dict__


def test_strategy_config_reassignment_is_rejected() -> None:
    strategy = ConfiguredStrategy()

    with pytest.raises(StrategyConfigMutationError):
        strategy.config = ThresholdConfig(threshold=1.0)


def test_strategy_config_deletion_is_rejected() -> None:
    strategy = ConfiguredStrategy()

    with pytest.raises(StrategyConfigMutationError):
        del strategy.config

    assert strategy.config.to_mapping() == {"threshold": 10.0}


def test_strategy_rejects_config_subclass_that_widens_declared_schema() -> None:
    class ExtendedThresholdConfig(ThresholdConfig):
        extra: int = 1

    with pytest.raises(StrategyConfigValidationError, match="expected config ThresholdConfig"):
        ConfiguredStrategy(ExtendedThresholdConfig(threshold=5.0, extra=2))


def test_config_mutation_during_lifecycle_fails_before_order_intake() -> None:
    class MutatingStrategy(Strategy[ThresholdConfig]):
        def on_bar(self, bar: BarEvent) -> None:
            self.config.threshold = 1.0
            self.buy(quantity=1.0)

    strategy = MutatingStrategy()
    runtime = _StrategyDriver(strategy)
    runtime.initialize()

    with pytest.raises(StrategyConfigMutationError):
        runtime.handle_bar(_closed_bar())

    assert runtime.order_state().pending == ()


def test_default_buy_and_sell_requests_are_market_orders() -> None:
    class DefaultOrderStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(quantity=1.0, tag="entry")
            self.sell(quantity=0.5, tag="exit")

    strategy = DefaultOrderStrategy()
    runtime = _StrategyDriver(strategy)
    runtime.initialize()

    runtime.handle_bar(_closed_bar())

    pending = runtime.order_state().pending
    assert [(request.side, request.order_type, request.tag) for request in pending] == [
        ("buy", "market", "entry"),
        ("sell", "market", "exit"),
    ]


def test_buy_and_sell_public_signature_defaults_to_market_orders() -> None:
    assert signature(Strategy.buy).parameters["order_type"].default == "market"
    assert signature(Strategy.sell).parameters["order_type"].default == "market"


def test_explicit_matching_symbols_are_preserved_on_order_requests() -> None:
    class ExplicitSymbolStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(symbol="BTC/USDT", quantity=1.0, tag="entry")
            self.sell(symbol="BTC/USDT", quantity=0.5, tag="exit")

    strategy = ExplicitSymbolStrategy()
    runtime = _StrategyDriver(strategy)
    runtime.initialize()

    runtime.handle_bar(_closed_bar(symbol="BTC/USDT"))

    assert [(request.side, request.symbol) for request in runtime.order_state().pending] == [
        ("buy", "BTC/USDT"),
        ("sell", "BTC/USDT"),
    ]


def test_explicit_buy_symbol_mismatch_is_rejected_and_clears_pending_requests() -> None:
    class MismatchedBuySymbolStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(symbol="ETH/USDT", quantity=1.0, tag="mismatch")

    strategy = MismatchedBuySymbolStrategy()
    runtime = _StrategyDriver(strategy)
    runtime.initialize()

    with pytest.raises(ValueError, match="explicit symbol"):
        runtime.handle_bar(_closed_bar(symbol="BTC/USDT"))

    assert runtime.order_state().pending == ()


def test_explicit_symbol_mismatch_is_rejected_and_clears_pending_requests() -> None:
    class MismatchedSymbolStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(quantity=1.0, tag="before-mismatch")
            self.sell(symbol="ETH/USDT", quantity=0.5, tag="mismatch")

    strategy = MismatchedSymbolStrategy()
    runtime = _StrategyDriver(strategy)
    runtime.initialize()

    with pytest.raises(ValueError, match="explicit symbol"):
        runtime.handle_bar(_closed_bar(symbol="BTC/USDT"))

    assert runtime.order_state().pending == ()


def test_stop_order_requests_infer_trigger_direction_from_active_close() -> None:
    class StopOrderStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(
                quantity=1.0,
                order_type="stop_market",
                stop_price=13.0,
                tag="above-entry",
            )
            self.sell(
                quantity=0.5,
                order_type="stop_market",
                stop_price=11.0,
                tag="below-exit",
            )

    strategy = StopOrderStrategy()
    runtime = _StrategyDriver(strategy)
    runtime.initialize()

    runtime.handle_bar(_closed_bar(close=12.0))

    assert [
        (request.side, request.stop_price, request.trigger_condition, request.tag)
        for request in runtime.order_state().pending
    ] == [
        ("buy", 13.0, "crosses_above", "above-entry"),
        ("sell", 11.0, "crosses_below", "below-exit"),
    ]


def test_stop_order_rejects_ambiguous_active_close_trigger() -> None:
    class AmbiguousStopStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(quantity=1.0, order_type="stop_market", stop_price=bar.close)

    strategy = AmbiguousStopStrategy()
    runtime = _StrategyDriver(strategy)
    runtime.initialize()

    with pytest.raises(ValueError, match="ambiguous"):
        runtime.handle_bar(_closed_bar(close=12.0))

    assert runtime.order_state().pending == ()
