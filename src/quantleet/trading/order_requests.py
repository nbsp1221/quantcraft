from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real

from quantleet.trading.domain.intents import (
    OrderIntent,
    OrderSide,
    OrderType,
    TriggerCondition,
    _is_stop_order_type,
)


@dataclass(frozen=True, slots=True)
class PendingOrderRequest:
    symbol: str
    side: OrderSide
    quantity: float | None = None
    qty_percent: float | None = None
    order_type: OrderType = "market"
    stop_price: float | None = None
    trigger_condition: TriggerCondition | None = None
    limit_price: float | None = None
    tag: str | None = None

    def __post_init__(self) -> None:
        _validate_request_sizing(self.quantity, self.qty_percent)
        _validate_request_order_shape(
            self.order_type,
            self.stop_price,
            self.trigger_condition,
            self.limit_price,
        )
        _validate_request_positive_price("limit_price", self.limit_price)
        _validate_request_positive_price("stop_price", self.stop_price)
        _validate_request_non_stop_shape(
            self.order_type,
            self.stop_price,
            self.trigger_condition,
        )

    def to_order_intent(self, *, quantity: float) -> OrderIntent:
        return OrderIntent(
            symbol=self.symbol,
            side=self.side,
            quantity=quantity,
            order_type=self.order_type,
            trigger_price=self.stop_price,
            trigger_condition=self.trigger_condition,
            trigger_type="last" if _is_stop_order_type(self.order_type) else None,
            limit_price=self.limit_price,
            tag=self.tag,
        )


def _is_finite_number(value: object) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(float(value))


def _validate_request_sizing(
    quantity: float | None,
    qty_percent: float | None,
) -> None:
    if (quantity is not None) == (qty_percent is not None):
        raise ValueError("PendingOrderRequest requires exactly one sizing mode")
    if quantity is not None and (not _is_finite_number(quantity) or quantity <= 0.0):
        raise ValueError("quantity must be a positive finite float")
    if qty_percent is not None:
        _validate_request_qty_percent(qty_percent)


def _validate_request_qty_percent(qty_percent: float) -> None:
    if not _is_finite_number(qty_percent):
        raise ValueError("qty_percent must be numeric")
    if not (0.0 < qty_percent <= 100.0):
        raise ValueError("qty_percent must satisfy 0 < qty_percent <= 100")


def _validate_request_order_shape(
    order_type: OrderType,
    stop_price: float | None,
    trigger_condition: TriggerCondition | None,
    limit_price: float | None,
) -> None:
    if order_type == "limit" and limit_price is None:
        raise ValueError("limit orders require a limit_price")
    if _is_stop_order_type(order_type):
        _validate_request_stop_family_shape(
            order_type,
            stop_price,
            trigger_condition,
            limit_price,
        )


def _validate_request_stop_family_shape(
    order_type: OrderType,
    stop_price: float | None,
    trigger_condition: TriggerCondition | None,
    limit_price: float | None,
) -> None:
    if stop_price is None:
        raise ValueError(f"{order_type} orders require a stop_price")
    if trigger_condition is None:
        raise ValueError(f"{order_type} orders require a trigger_condition")
    if order_type == "stop_market" and limit_price is not None:
        raise ValueError("stop_market orders cannot specify a limit_price")
    if order_type == "stop_limit" and limit_price is None:
        raise ValueError("stop_limit orders require a limit_price")


def _validate_request_positive_price(field_name: str, value: float | None) -> None:
    if value is not None and (not _is_finite_number(value) or value <= 0.0):
        raise ValueError(f"{field_name} must be a positive finite float")


def _validate_request_non_stop_shape(
    order_type: OrderType,
    stop_price: float | None,
    trigger_condition: TriggerCondition | None,
) -> None:
    if _is_stop_order_type(order_type):
        return
    if stop_price is not None:
        raise ValueError("stop_price is only valid for stop-family orders")
    if trigger_condition is not None:
        raise ValueError("trigger_condition is only valid for stop-family orders")


__all__ = ["PendingOrderRequest"]
