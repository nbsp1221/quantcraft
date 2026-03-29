from __future__ import annotations

from dataclasses import is_dataclass

import pytest

from quantcraft.data.domain import OHLCVBar


def test_data_domain_exports_canonical_ohlcv_bar() -> None:
    bar = OHLCVBar(
        timestamp=1_700_000_000_000,
        open=1.0,
        high=2.0,
        low=0.5,
        close=1.5,
        volume=10.0,
    )

    assert is_dataclass(bar)
    assert bar.close == 1.5
    assert bar.volume == 10.0


@pytest.mark.parametrize(
    ("field_overrides", "match"),
    [
        ({"timestamp": True}, "invalid OHLCV row"),
        ({"open": float("inf")}, "invalid OHLCV row"),
        ({"volume": -1.0}, "invalid OHLCV row"),
        ({"high": 0.25}, "invalid OHLCV row"),
        ({"low": 3.0}, "invalid OHLCV row"),
    ],
)
def test_ohlcv_bar_rejects_invalid_rows(
    field_overrides: dict[str, float | int | bool],
    match: str,
) -> None:
    kwargs: dict[str, float | int] = {
        "timestamp": 1_700_000_000_000,
        "open": 1.0,
        "high": 2.0,
        "low": 0.5,
        "close": 1.5,
        "volume": 10.0,
    }
    kwargs.update(field_overrides)

    with pytest.raises(ValueError, match=match):
        OHLCVBar(**kwargs)
