from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from quantcraft.trading.domain.events import BarEvent
from quantcraft.trading.domain.intents import OrderIntent
from quantcraft.trading.domain.state import TradingState

if TYPE_CHECKING:
    from quantcraft.research.application.strategy import Strategy


class PositionView:
    __slots__ = ("_is_open", "_quantity", "_average_entry_price")

    def __init__(self) -> None:
        self._is_open = False
        self._quantity = 0.0
        self._average_entry_price = 0.0

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def quantity(self) -> float:
        return self._quantity

    @property
    def average_entry_price(self) -> float:
        return self._average_entry_price

    def _refresh(self, state: TradingState) -> None:
        self._quantity = state.position_quantity
        self._average_entry_price = state.average_entry_price
        self._is_open = state.position_quantity > 0.0


@dataclass(frozen=True, slots=True)
class _StrategyOrderState:
    active: tuple[OrderIntent, ...]
    pending: tuple[OrderIntent, ...]


class _StrategyDriver:
    _DEFAULT_FLAT_STATE = TradingState(cash=0.0, equity=0.0)

    def __init__(self, strategy: Strategy) -> None:
        self._strategy = strategy

    def initialize(self) -> None:
        if self._strategy._initialized:
            return None
        self._strategy.init()
        self._strategy._initialized = True
        return None

    def sync_position(self, state: TradingState) -> None:
        self._strategy.position._refresh(state)

    def handle_bar(self, bar: BarEvent, *, state: TradingState | None = None) -> None:
        self._append_bar(bar)
        self.sync_position(self._DEFAULT_FLAT_STATE if state is None else state)
        self._strategy._handle_bar(bar)

    def activate_pending_order_intents(self) -> _StrategyOrderState:
        self._strategy._active_order_intents = (
            self._strategy._active_order_intents + tuple(self._strategy._pending_order_intents)
        )
        self._strategy._pending_order_intents.clear()
        return self.order_state()

    def order_state(self) -> _StrategyOrderState:
        return _StrategyOrderState(
            active=self._strategy._active_order_intents,
            pending=tuple(self._strategy._pending_order_intents),
        )

    def replace_active_order_intents(self, intents: tuple[OrderIntent, ...]) -> None:
        self._strategy._active_order_intents = intents

    def _append_bar(self, bar: BarEvent) -> None:
        self._strategy.data.open._append(bar.open)
        self._strategy.data.high._append(bar.high)
        self._strategy.data.low._append(bar.low)
        self._strategy.data.close._append(bar.close)
        self._strategy.data.volume._append(bar.volume)
