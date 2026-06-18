from __future__ import annotations

import pytest

from quantcraft.research import WalkForwardStudy
from tests.unit.research.support_parameter_study import (
    CountingEngine,
    NoTradeStrategy,
    make_bars,
    make_engine,
)


def test_rolling_windows_use_start_inclusive_end_exclusive_indexes_and_timestamps() -> None:
    study = WalkForwardStudy(
        engine=make_engine(),
        bars=make_bars(closes=tuple(float(100 + index) for index in range(12))),
        strategy=NoTradeStrategy,
    )

    result = study.run(
        parameters={"x": [1]},
        objective=("returns.total_return", "max"),
        train_size=4,
        test_size=2,
    )

    assert [(fold.train_start_index, fold.train_end_index) for fold in result.folds] == [
        (0, 4),
        (2, 6),
        (4, 8),
        (6, 10),
    ]
    assert [(fold.test_start_index, fold.test_end_index) for fold in result.folds] == [
        (4, 6),
        (6, 8),
        (8, 10),
        (10, 12),
    ]
    assert result.folds[0].train_start_timestamp == 60
    assert result.folds[0].train_end_timestamp == 240
    assert result.folds[0].test_start_timestamp == 300
    assert result.folds[0].test_end_timestamp == 360
    assert result.mode == "rolling"
    assert result.train_size == 4
    assert result.test_size == 2
    assert result.step_size == 2
    assert result.execution_scale.fold_count == 4
    assert result.execution_scale.planned_total_runs == 8


def test_explicit_step_size_omits_incomplete_trailing_windows() -> None:
    result = WalkForwardStudy(
        engine=make_engine(),
        bars=make_bars(closes=tuple(float(100 + index) for index in range(12))),
        strategy=NoTradeStrategy,
    ).run(
        parameters={"x": [1]},
        objective=("returns.total_return", "max"),
        train_size=4,
        test_size=2,
        step_size=3,
    )

    assert [fold.train_start_index for fold in result.folds] == [0, 3, 6]


def test_not_enough_bars_fails_before_execution() -> None:
    engine = CountingEngine()

    with pytest.raises(ValueError, match="complete fold"):
        WalkForwardStudy(
            engine=engine,
            bars=make_bars(closes=tuple(float(100 + index) for index in range(9))),
            strategy=NoTradeStrategy,
        ).run(
            parameters={"x": [1]},
            objective=("returns.total_return", "max"),
            train_size=6,
            test_size=4,
        )

    assert engine.calls == []
