from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

from quantcraft.data import BarSeries, TimeBar
from quantcraft.trading.domain.events import BarEvent, TickEvent
from quantcraft.trading.domain.intents import _is_stop_order_type
from quantcraft.trading.domain.orders import Order

_UNBOUNDED_LEVEL_SIZE = math.inf


SyntheticEvent = TickEvent | BarEvent


@dataclass(frozen=True, slots=True)
class _SegmentCrossingResult:
    prices: tuple[float, ...]
    newly_triggered_unfilled_stop_limit_ids: frozenset[int]


@dataclass(frozen=True, slots=True)
class _StopCrossingResult:
    prices: tuple[float, ...]
    newly_triggered_unfilled_stop_limit_id: int | None = None


class BacktestExecutionModel(Protocol):
    @property
    def name(self) -> str: ...

    def tick_events_for_bar(
        self,
        *,
        symbol: str,
        previous_close: float | None,
        bar: TimeBar,
        active_orders: tuple[Order, ...] = (),
    ) -> tuple[TickEvent, ...]: ...

    def events_from_bars(self, *, bars: BarSeries) -> tuple[SyntheticEvent, ...]: ...


@dataclass(frozen=True, slots=True)
class ConservativeOHLCVExecutionModel:
    @property
    def name(self) -> str:
        return "conservative_ohlcv"

    def infer_intrabar_prices(self, bar: TimeBar) -> tuple[float, float, float, float]:
        if bar.close >= bar.open:
            return (bar.open, bar.low, bar.high, bar.close)

        return (bar.open, bar.high, bar.low, bar.close)

    def tick_events_for_bar(
        self,
        *,
        symbol: str,
        previous_close: float | None,
        bar: TimeBar,
        active_orders: tuple[Order, ...] = (),
    ) -> tuple[TickEvent, ...]:
        prices: list[float] = [bar.open]
        del previous_close

        path = self.infer_intrabar_prices(bar)
        triggered_unfilled_stop_limit_ids = frozenset(
            order.id
            for order in active_orders
            if self._is_dormant_stop_limit(order)
            and order.symbol == symbol
            and order.is_triggered_by_price(price=bar.open)
            and not self._is_marketable_at_price(order=order, price=bar.open)
        )
        for start, end in zip(path, path[1:], strict=False):
            segment_crossings = self._crossing_prices_for_segment(
                symbol=symbol,
                start=start,
                end=end,
                active_orders=active_orders,
                triggered_unfilled_stop_limit_ids=triggered_unfilled_stop_limit_ids,
            )
            prices.extend(segment_crossings.prices)
            triggered_unfilled_stop_limit_ids |= (
                segment_crossings.newly_triggered_unfilled_stop_limit_ids
            )
            if end != prices[-1]:
                prices.append(end)

        return tuple(
            self._tick_event(symbol=symbol, timestamp=bar.timestamp, price=price)
            for price in prices
        )

    def events_from_bars(self, *, bars: BarSeries) -> tuple[SyntheticEvent, ...]:
        rows = bars.rows
        if any(
            current.timestamp >= nxt.timestamp for current, nxt in zip(rows, rows[1:], strict=False)
        ):
            raise ValueError("out-of-order time bars")

        events: list[SyntheticEvent] = []
        previous_close: float | None = None

        for row in rows:
            events.extend(
                self.tick_events_for_bar(
                    symbol=bars.symbol,
                    previous_close=previous_close,
                    bar=row,
                )
            )
            events.append(
                self._bar_event(
                    symbol=bars.symbol,
                    timeframe=bars.timeframe,
                    bar_type=bars.bar_type,
                    bar=row,
                )
            )
            previous_close = row.close

        return tuple(events)

    def _crossing_prices_for_segment(
        self,
        *,
        symbol: str,
        start: float,
        end: float,
        active_orders: tuple[Order, ...],
        triggered_unfilled_stop_limit_ids: frozenset[int],
    ) -> _SegmentCrossingResult:
        if start == end:
            return _SegmentCrossingResult((), frozenset())

        candidates: list[float] = []
        newly_triggered_unfilled_stop_limit_ids: set[int] = set()
        low = min(start, end)
        high = max(start, end)

        for order in active_orders:
            if order.symbol != symbol or not order.is_open:
                continue
            if self._has_working_limit(order, triggered_unfilled_stop_limit_ids):
                limit_candidate = self._limit_crossing_candidate(
                    order=order,
                    start=start,
                    low=low,
                    high=high,
                )
                if limit_candidate is not None:
                    candidates.append(limit_candidate)
                continue
            stop_crossing = self._stop_crossing_candidates(
                order=order,
                start=start,
                end=end,
                low=low,
                high=high,
            )
            candidates.extend(stop_crossing.prices)
            if stop_crossing.newly_triggered_unfilled_stop_limit_id is not None:
                newly_triggered_unfilled_stop_limit_ids.add(
                    stop_crossing.newly_triggered_unfilled_stop_limit_id
                )

        reverse = start > end
        ordered_prices = sorted(
            set(candidates),
            reverse=reverse,
        )
        return _SegmentCrossingResult(
            prices=tuple(price for price in ordered_prices if price != start),
            newly_triggered_unfilled_stop_limit_ids=frozenset(
                newly_triggered_unfilled_stop_limit_ids
            ),
        )

    def _limit_crossing_candidate(
        self,
        *,
        order: Order,
        start: float,
        low: float,
        high: float,
    ) -> float | None:
        if order.limit_price is None:
            return None
        if self._is_marketable_at_price(order=order, price=start):
            return None
        if not low <= order.limit_price <= high:
            return None
        return order.limit_price

    def _stop_crossing_candidates(
        self,
        *,
        order: Order,
        start: float,
        end: float,
        low: float,
        high: float,
    ) -> _StopCrossingResult:
        if not self._has_dormant_stop_crossing(order=order, start=start, low=low, high=high):
            return _StopCrossingResult(())
        prices = [order.trigger_price]
        newly_triggered_id = self._newly_triggered_unfilled_stop_limit_id(order)
        if newly_triggered_id is not None:
            prices.extend(self._post_trigger_limit_crossing(order=order, end=end))
        return _StopCrossingResult(
            prices=tuple(price for price in prices if price is not None),
            newly_triggered_unfilled_stop_limit_id=newly_triggered_id,
        )

    def _post_trigger_limit_crossing(self, *, order: Order, end: float) -> tuple[float, ...]:
        if order.limit_price is None or order.trigger_price is None:
            return ()
        if not self._crosses_between(
            price=order.limit_price,
            start=order.trigger_price,
            end=end,
        ):
            return ()
        return (order.limit_price,)

    @staticmethod
    def _has_working_limit(
        order: Order,
        triggered_unfilled_stop_limit_ids: frozenset[int],
    ) -> bool:
        return (
            ConservativeOHLCVExecutionModel._is_executable_limit(order)
            or order.id in triggered_unfilled_stop_limit_ids
        )

    def _has_dormant_stop_crossing(
        self,
        *,
        order: Order,
        start: float,
        low: float,
        high: float,
    ) -> bool:
        return (
            _is_stop_order_type(order.order_type)
            and not order.is_triggered
            and order.trigger_price is not None
            and not order.is_triggered_by_price(price=start)
            and low <= order.trigger_price <= high
        )

    def _newly_triggered_unfilled_stop_limit_id(self, order: Order) -> int | None:
        if order.order_type != "stop_limit" or order.trigger_price is None:
            return None
        if self._is_marketable_at_price(order=order, price=order.trigger_price):
            return None
        return order.id

    @staticmethod
    def _is_executable_limit(order: Order) -> bool:
        return order.is_executable and order.executable_order_type == "limit"

    @staticmethod
    def _is_dormant_stop_limit(order: Order) -> bool:
        return order.order_type == "stop_limit" and not order.is_triggered

    @staticmethod
    def _crosses_between(*, price: float, start: float, end: float) -> bool:
        return min(start, end) <= price <= max(start, end) and price != start

    @staticmethod
    def _is_marketable_at_price(*, order: Order, price: float) -> bool:
        if order.limit_price is None:
            return False
        if order.side == "buy":
            return price <= order.limit_price
        return price >= order.limit_price

    @staticmethod
    def _tick_event(*, symbol: str, timestamp: int, price: float) -> TickEvent:
        return TickEvent(
            timestamp=timestamp,
            symbol=symbol,
            bids=((price, _UNBOUNDED_LEVEL_SIZE),),
            asks=((price, _UNBOUNDED_LEVEL_SIZE),),
            last=price,
        )

    @staticmethod
    def _bar_event(*, symbol: str, timeframe: str, bar_type: str, bar: TimeBar) -> BarEvent:
        return BarEvent(
            bar_type=bar_type,
            bar_spec=timeframe,
            symbol=symbol,
            timestamp=bar.timestamp,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
            is_closed=True,
        )


__all__ = [
    "BacktestExecutionModel",
    "ConservativeOHLCVExecutionModel",
    "SyntheticEvent",
]
