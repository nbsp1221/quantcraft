from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real

from quantcraft.trading.domain.intents import OrderIntent, OrderSide, OrderType


@dataclass(frozen=True, slots=True)
class PendingOrderRequest:
    symbol: str
    side: OrderSide
    quantity: float | None = None
    qty_percent: float | None = None
    order_type: OrderType = "market"
    limit_price: float | None = None
    tag: str | None = None

    def __post_init__(self) -> None:
        has_quantity = self.quantity is not None
        has_qty_percent = self.qty_percent is not None
        if has_quantity == has_qty_percent:
            raise ValueError("PendingOrderRequest requires exactly one sizing mode")
        if self.quantity is not None:
            if not _is_finite_number(self.quantity) or self.quantity <= 0.0:
                raise ValueError("quantity must be a positive finite float")
        if self.qty_percent is not None:
            if not _is_finite_number(self.qty_percent):
                raise ValueError("qty_percent must be numeric")
            if not (0.0 < self.qty_percent <= 100.0):
                raise ValueError("qty_percent must satisfy 0 < qty_percent <= 100")
        if self.order_type == "limit" and self.limit_price is None:
            raise ValueError("limit orders require a limit_price")
        if self.limit_price is not None and (
            not _is_finite_number(self.limit_price) or self.limit_price <= 0.0
        ):
            raise ValueError("limit_price must be a positive finite float")

    def to_order_intent(self, *, quantity: float) -> OrderIntent:
        return OrderIntent(
            symbol=self.symbol,
            side=self.side,
            quantity=quantity,
            order_type=self.order_type,
            limit_price=self.limit_price,
            tag=self.tag,
        )


def _is_finite_number(value: object) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(float(value))


__all__ = ["PendingOrderRequest"]
