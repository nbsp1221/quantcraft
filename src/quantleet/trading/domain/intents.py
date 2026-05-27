from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

OrderSide = Literal["buy", "sell"]
OrderType = Literal["market", "limit", "stop_market", "stop_limit"]
TriggerCondition = Literal["crosses_above", "crosses_below"]
TriggerType = Literal["last"]


@dataclass(frozen=True, slots=True)
class OrderIntent:
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    trigger_price: float | None = None
    trigger_condition: TriggerCondition | None = None
    trigger_type: TriggerType | None = None
    limit_price: float | None = None
    tag: str | None = None

    def __post_init__(self) -> None:
        _validate_positive_quantity(
            "OrderIntent requires a positive finite quantity",
            self.quantity,
        )
        _validate_limit_shape(self.order_type, self.limit_price)
        _validate_stop_family_shape(
            self.order_type,
            self.trigger_price,
            self.trigger_condition,
            self.trigger_type,
            self.limit_price,
        )
        _validate_non_stop_shape(
            self.order_type,
            self.trigger_price,
            self.trigger_condition,
            self.trigger_type,
        )


def _is_stop_order_type(order_type: str) -> bool:
    return order_type in {"stop_market", "stop_limit"}


def _validate_positive_quantity(message: str, quantity: float) -> None:
    if not math.isfinite(quantity) or quantity <= 0.0:
        raise ValueError(message)


def _validate_limit_shape(order_type: OrderType, limit_price: float | None) -> None:
    if order_type == "limit" and limit_price is None:
        raise ValueError("limit orders require a limit_price")


def _validate_stop_family_shape(
    order_type: OrderType,
    trigger_price: float | None,
    trigger_condition: TriggerCondition | None,
    trigger_type: TriggerType | None,
    limit_price: float | None,
) -> None:
    if not _is_stop_order_type(order_type):
        return
    if trigger_price is None:
        raise ValueError(f"{order_type} orders require a trigger_price")
    if trigger_condition is None:
        raise ValueError(f"{order_type} orders require a trigger_condition")
    if trigger_type is None:
        raise ValueError(f"{order_type} orders require a trigger_type")
    if order_type == "stop_market" and limit_price is not None:
        raise ValueError("stop_market orders cannot specify a limit_price")
    if order_type == "stop_limit" and limit_price is None:
        raise ValueError("stop_limit orders require a limit_price")


def _validate_non_stop_shape(
    order_type: OrderType,
    trigger_price: float | None,
    trigger_condition: TriggerCondition | None,
    trigger_type: TriggerType | None,
    triggered_at: int | None = None,
) -> None:
    if _is_stop_order_type(order_type):
        return
    if trigger_price is not None:
        raise ValueError("trigger_price is only valid for stop-family orders")
    if trigger_condition is not None:
        raise ValueError("trigger_condition is only valid for stop-family orders")
    if trigger_type is not None:
        raise ValueError("trigger_type is only valid for stop-family orders")
    if triggered_at is not None:
        raise ValueError("triggered_at is only valid for stop-family orders")
