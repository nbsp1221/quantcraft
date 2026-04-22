from __future__ import annotations

from abc import ABC, abstractmethod

from quantcraft.research.series import OHLCVDataView, SeriesView
from quantcraft.trading.domain.events import BarEvent
from quantcraft.trading.domain.intents import OrderType
from quantcraft.trading.domain.state import TradingState
from quantcraft.trading.order_requests import PendingOrderRequest


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


class Strategy(ABC):
    def __init__(self) -> None:
        self._reset_runtime_state()

    def _reset_runtime_state(self) -> None:
        self._pending_order_requests: list[PendingOrderRequest] = []
        self._handling_bar = False
        self._active_bar_symbol: str | None = None
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

    @abstractmethod
    def on_bar(self, bar: BarEvent) -> None:
        raise NotImplementedError

    def _handle_bar(self, bar: BarEvent) -> None:
        if not bar.is_closed:
            raise ValueError("Strategy.handle_bar requires a closed bar")
        self._handling_bar = True
        self._active_bar_symbol = bar.symbol
        try:
            self.on_bar(bar)
        except Exception:
            self._pending_order_requests.clear()
            raise
        finally:
            self._handling_bar = False
            self._active_bar_symbol = None

    def buy(
        self,
        *,
        symbol: str | None = None,
        quantity: float | None = None,
        qty_percent: float | None = None,
        order_type: OrderType = "market",
        limit_price: float | None = None,
        tag: str | None = None,
    ) -> None:
        self._assert_order_intake_allowed()
        self._pending_order_requests.append(
            PendingOrderRequest(
                symbol=self._resolve_order_symbol(symbol),
                side="buy",
                quantity=quantity,
                qty_percent=qty_percent,
                order_type=order_type,
                limit_price=limit_price,
                tag=tag,
            )
        )

    def sell(
        self,
        *,
        symbol: str | None = None,
        quantity: float | None = None,
        qty_percent: float | None = None,
        order_type: OrderType = "market",
        limit_price: float | None = None,
        tag: str | None = None,
    ) -> None:
        self._assert_order_intake_allowed()
        self._pending_order_requests.append(
            PendingOrderRequest(
                symbol=self._resolve_order_symbol(symbol),
                side="sell",
                quantity=quantity,
                qty_percent=qty_percent,
                order_type=order_type,
                limit_price=limit_price,
                tag=tag,
            )
        )

    def _assert_order_intake_allowed(self) -> None:
        if not self._handling_bar:
            raise ValueError("Order intake methods may only be used during on_bar")

    def _resolve_order_symbol(self, symbol: str | None) -> str:
        active_bar_symbol = self._active_bar_symbol
        if symbol is not None:
            if active_bar_symbol is not None and symbol != active_bar_symbol:
                raise ValueError(
                    "explicit symbol must match the active series symbol "
                    "in the current single-symbol on_bar workflow"
                )
            return symbol
        if active_bar_symbol is None:
            raise RuntimeError("active bar symbol is missing during on_bar order intake")
        return active_bar_symbol


__all__ = ["Strategy"]
