from __future__ import annotations

import pytest

from quantcraft.data import BarSeries, TimeBar
from quantcraft.research import RollingSplitPolicy
from tests.integration.research.support_parameter_studies import walk_forward_bars


def test_rolling_split_policy_returns_start_inclusive_end_exclusive_windows() -> None:
    windows = RollingSplitPolicy(train_size=4, test_size=2).split(walk_forward_bars(8))

    assert [
        (w.train_start_index, w.train_end_index, w.test_start_index, w.test_end_index)
        for w in windows
    ] == [
        (0, 4, 4, 6),
        (2, 6, 6, 8),
    ]
    assert windows[0].train_start_timestamp == 60
    assert windows[0].test_end_timestamp == 360


def test_rolling_split_policy_rejects_non_chronological_bars() -> None:
    bars = BarSeries(
        symbol="TEST",
        timeframe="1m",
        bar_type="time",
        rows=(
            TimeBar(timestamp=2, open=1, high=1, low=1, close=1, volume=1),
            TimeBar(timestamp=1, open=1, high=1, low=1, close=1, volume=1),
            TimeBar(timestamp=3, open=1, high=1, low=1, close=1, volume=1),
        ),
    )

    with pytest.raises(ValueError, match="strictly increasing"):
        RollingSplitPolicy(train_size=1, test_size=1).split(bars)
