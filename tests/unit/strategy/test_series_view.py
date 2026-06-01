from __future__ import annotations

import math

import pytest

from quantleet.strategy.series import SeriesView


def test_series_view_respects_visible_length_and_history_order() -> None:
    series = SeriesView((10.0, 20.0, 30.0), visible_length=2)

    assert len(series) == 2
    assert series.latest == 20.0
    assert series[0] == 20.0
    assert series[1] == 10.0
    assert math.isnan(series[2])

    series._advance()

    assert len(series) == 3
    assert series.latest == 30.0
    assert series[0] == 30.0
    assert series[1] == 20.0
    assert series[2] == 10.0
    assert math.isnan(series[3])


def test_series_view_rejects_invalid_visibility_bounds() -> None:
    with pytest.raises(ValueError, match="visible_length"):
        SeriesView((10.0,), visible_length=-1)

    with pytest.raises(ValueError, match="visible_length"):
        SeriesView((10.0,), visible_length=2)

    series = SeriesView((10.0,), visible_length=0)

    with pytest.raises(ValueError, match="visible_length"):
        series._set_visible_length(2)


def test_series_view_append_advances_visibility_by_one() -> None:
    series = SeriesView(())

    series._append(10.0)
    series._append(20.0)

    assert len(series) == 2
    assert series[0] == 20.0
    assert series[1] == 10.0
    assert series._all_values() == (10.0, 20.0)


def test_series_view_rejects_negative_index() -> None:
    series = SeriesView((10.0,))

    with pytest.raises(ValueError, match="negative indices"):
        _ = series[-1]
