from __future__ import annotations

import importlib
from dataclasses import FrozenInstanceError, is_dataclass
from typing import get_type_hints

import pytest


def _domain_exports() -> tuple[object | None, object | None, object | None]:
    domain_module = importlib.import_module("quantcraft.data.domain")
    time_bar_type = getattr(domain_module, "TimeBar", None)
    bar_series_type = getattr(domain_module, "BarSeries", None)
    source_type = getattr(domain_module, "HistoricalDataSource", None)
    return time_bar_type, bar_series_type, source_type


def _public_exports() -> tuple[object | None, object | None]:
    data_module = importlib.import_module("quantcraft.data")
    time_bar_type = getattr(data_module, "TimeBar", None)
    bar_series_type = getattr(data_module, "BarSeries", None)
    return time_bar_type, bar_series_type


def _require_time_bar_type() -> type:
    time_bar_type, _, _ = _domain_exports()
    assert time_bar_type is not None, "quantcraft.data.domain must export TimeBar"
    return time_bar_type


def _require_bar_series_type() -> type:
    _, bar_series_type, _ = _domain_exports()
    assert bar_series_type is not None, "quantcraft.data.domain must export BarSeries"
    return bar_series_type


def _time_bar_kwargs() -> dict[str, float | int]:
    return {
        "timestamp": 1_700_000_000_000,
        "open": 1.0,
        "high": 2.0,
        "low": 0.5,
        "close": 1.5,
        "volume": 10.0,
    }


def _time_bar_instance() -> object:
    time_bar_type = _require_time_bar_type()
    return time_bar_type(**_time_bar_kwargs())


def test_data_domain_and_public_surface_export_time_bar_and_bar_series() -> None:
    domain_time_bar, domain_bar_series, source_type = _domain_exports()
    public_time_bar, public_bar_series = _public_exports()

    assert domain_time_bar is not None
    assert domain_bar_series is not None
    assert source_type is not None
    assert public_time_bar is domain_time_bar
    assert public_bar_series is domain_bar_series


def test_time_bar_is_a_frozen_dataclass_with_ohlcv_fields() -> None:
    bar = _time_bar_instance()

    assert is_dataclass(bar)
    assert bar.close == 1.5
    assert bar.volume == 10.0

    with pytest.raises(FrozenInstanceError):
        bar.close = 2.0  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_overrides", "match"),
    [
        ({"timestamp": True}, "invalid time bar"),
        ({"open": float("inf")}, "invalid time bar"),
        ({"volume": -1.0}, "invalid time bar"),
        ({"high": 0.25}, "invalid time bar"),
        ({"low": 3.0}, "invalid time bar"),
    ],
)
def test_time_bar_rejects_invalid_rows(
    field_overrides: dict[str, float | int | bool],
    match: str,
) -> None:
    time_bar_type = _require_time_bar_type()
    kwargs: dict[str, float | int] = _time_bar_kwargs()
    kwargs.update(field_overrides)

    with pytest.raises(ValueError, match=match):
        time_bar_type(**kwargs)


def test_bar_series_is_a_frozen_dataclass_for_time_bars() -> None:
    bar_series_type = _require_bar_series_type()
    bars = (_time_bar_instance(),)

    series = bar_series_type(
        symbol="BTC/USDT",
        timeframe="1m",
        bar_type="time",
        rows=bars,
    )

    assert is_dataclass(series)
    assert series.symbol == "BTC/USDT"
    assert series.timeframe == "1m"
    assert series.bar_type == "time"
    assert series.rows == bars

    with pytest.raises(FrozenInstanceError):
        series.symbol = "ETH/USDT"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_overrides", "match"),
    [
        ({"symbol": ""}, "invalid bar series metadata"),
        ({"timeframe": ""}, "invalid bar series metadata"),
        ({"bar_type": "tick"}, "bar_type must be 'time'"),
    ],
)
def test_bar_series_rejects_invalid_metadata(
    field_overrides: dict[str, object],
    match: str,
) -> None:
    bar_series_type = _require_bar_series_type()
    kwargs: dict[str, object] = {
        "symbol": "BTC/USDT",
        "timeframe": "1m",
        "bar_type": "time",
        "rows": (_time_bar_instance(),),
    }
    kwargs.update(field_overrides)

    with pytest.raises(ValueError, match=match):
        bar_series_type(**kwargs)


def test_bar_series_requires_a_tuple_of_time_bars() -> None:
    bar_series_type = _require_bar_series_type()
    time_bar = _time_bar_instance()

    with pytest.raises(ValueError, match="rows must be a tuple of TimeBar"):
        bar_series_type(
            symbol="BTC/USDT",
            timeframe="1m",
            bar_type="time",
            rows=[time_bar],
        )

    with pytest.raises(ValueError, match="rows must be a tuple of TimeBar"):
        bar_series_type(
            symbol="BTC/USDT",
            timeframe="1m",
            bar_type="time",
            rows=(time_bar, object()),
        )


def test_historical_data_source_contract_loads_bar_series() -> None:
    _, bar_series_type, source_type = _domain_exports()

    assert bar_series_type is not None, "quantcraft.data.domain must export BarSeries"
    assert source_type is not None, "quantcraft.data.domain must export HistoricalDataSource"

    annotations = get_type_hints(source_type.load)
    assert annotations["return"] == bar_series_type
