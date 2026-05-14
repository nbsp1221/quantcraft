from __future__ import annotations

import pytest

from quantleet.data import BarSeries, TimeBar
from quantleet.research import WalkForwardStudy
from tests.unit.research.support_parameter_study import (
    CountingEngine,
    NoTradeStrategy,
    make_bars,
    make_engine,
)


class NotAStrategy:
    pass


def _run_valid_study(engine: object) -> object:
    return WalkForwardStudy(
        engine=engine,
        bars=make_bars(closes=(100.0,) * 8),
        strategy=NoTradeStrategy,
    ).run(
        parameters={"x": [1]},
        objective=("returns.total_return", "max"),
        train_size=4,
        test_size=2,
    )


def test_constructor_preflight_rejects_invalid_engine_bars_and_strategy() -> None:
    with pytest.raises(TypeError, match="engine"):
        WalkForwardStudy(
            engine=object(),
            bars=make_bars(),
            strategy=NoTradeStrategy,
        )
    with pytest.raises(TypeError, match="BarSeries"):
        WalkForwardStudy(
            engine=make_engine(),
            bars=[],  # type: ignore[arg-type]
            strategy=NoTradeStrategy,
        )
    with pytest.raises(ValueError, match="at least one"):
        WalkForwardStudy(
            engine=make_engine(),
            bars=BarSeries(symbol="TEST", timeframe="1m", bar_type="time", rows=()),
            strategy=NoTradeStrategy,
        )
    with pytest.raises(TypeError, match="Strategy class"):
        WalkForwardStudy(
            engine=make_engine(),
            bars=make_bars(),
            strategy=lambda config: NoTradeStrategy(config),  # type: ignore[arg-type]
        )
    with pytest.raises(TypeError, match="Strategy class"):
        WalkForwardStudy(
            engine=make_engine(),
            bars=make_bars(),
            strategy=NotAStrategy,  # type: ignore[arg-type]
        )


def test_preflight_rejects_empty_parameter_mapping_before_backtests() -> None:
    engine = CountingEngine()

    with pytest.raises(ValueError, match="parameters"):
        WalkForwardStudy(
            engine=engine,
            bars=make_bars(closes=(100.0,) * 8),
            strategy=NoTradeStrategy,
        ).run(
            parameters={},
            objective=("returns.total_return", "max"),
            train_size=5,
            test_size=2,
        )

    assert engine.calls == []


def test_preflight_rejects_invalid_window_and_mode_before_backtests() -> None:
    engine = CountingEngine()
    study = WalkForwardStudy(
        engine=engine,
        bars=make_bars(closes=(100.0,) * 8),
        strategy=NoTradeStrategy,
    )

    with pytest.raises(TypeError, match="train_size"):
        study.run(
            parameters={"x": [1]},
            objective=("returns.total_return", "max"),
            train_size=True,
            test_size=2,
        )
    with pytest.raises(ValueError, match="unsupported"):
        study.run(
            parameters={"x": [1]},
            objective=("returns.total_return", "max"),
            train_size=5,
            test_size=2,
            mode="expanding",  # type: ignore[arg-type]
        )

    assert engine.calls == []


def test_preflight_rejects_duplicate_or_out_of_order_timestamps() -> None:
    engine = CountingEngine()
    rows = make_bars(closes=(100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0)).rows
    bad_bars = BarSeries(
        symbol="TEST",
        timeframe="1m",
        bar_type="time",
        rows=(
            rows[0],
            rows[2],
            TimeBar(timestamp=120, open=101.0, high=102.0, low=100.0, close=101.0, volume=1.0),
            *rows[3:],
        ),
    )

    with pytest.raises(ValueError, match="strictly increasing"):
        WalkForwardStudy(engine=engine, bars=bad_bars, strategy=NoTradeStrategy).run(
            parameters={"x": [1]},
            objective=("returns.total_return", "max"),
            train_size=4,
            test_size=2,
        )

    assert engine.calls == []


def test_preflight_rejects_strategy_instance_and_unknown_config_field() -> None:
    with pytest.raises(TypeError, match="Strategy class"):
        WalkForwardStudy(
            engine=make_engine(),
            bars=make_bars(),
            strategy=NoTradeStrategy(),  # type: ignore[arg-type]
        )

    engine = CountingEngine()
    with pytest.raises(Exception, match="unknown strategy config field"):
        WalkForwardStudy(
            engine=engine,
            bars=make_bars(closes=(100.0,) * 8),
            strategy=NoTradeStrategy,
        ).run(
            parameters={"missing": [1]},
            objective=("returns.total_return", "max"),
            train_size=5,
            test_size=2,
        )
    assert engine.calls == []


@pytest.mark.parametrize(
    ("parameters", "match"),
    [
        ({"x": []}, "at least one value"),
        ({"x": [float("inf")]}, "finite"),
        ({"x": [[1]]}, "unsupported type"),
    ],
)
def test_preflight_rejects_invalid_parameter_values_before_backtests(
    parameters: object,
    match: str,
) -> None:
    engine = CountingEngine()

    with pytest.raises((TypeError, ValueError), match=match):
        WalkForwardStudy(
            engine=engine,
            bars=make_bars(closes=(100.0,) * 8),
            strategy=NoTradeStrategy,
        ).run(
            parameters=parameters,  # type: ignore[arg-type]
            objective=("returns.total_return", "max"),
            train_size=4,
            test_size=2,
        )

    assert engine.calls == []


@pytest.mark.parametrize(
    ("objective", "match"),
    [
        ("sharpe", "tuple"),
        (lambda result: 1.0, "tuple"),
        (("returns.total_return", "largest"), "direction"),
        (("missing.metric", "max"), "unknown"),
    ],
)
def test_preflight_rejects_invalid_objectives_before_backtests(
    objective: object,
    match: str,
) -> None:
    engine = CountingEngine()

    with pytest.raises((TypeError, ValueError), match=match):
        WalkForwardStudy(
            engine=engine,
            bars=make_bars(closes=(100.0,) * 8),
            strategy=NoTradeStrategy,
        ).run(
            parameters={"x": [1]},
            objective=objective,  # type: ignore[arg-type]
            train_size=4,
            test_size=2,
        )

    assert engine.calls == []


def test_explicit_total_run_cap_fails_before_execution() -> None:
    engine = CountingEngine()

    with pytest.raises(ValueError, match="planned total runs"):
        WalkForwardStudy(
            engine=engine,
            bars=make_bars(closes=(100.0,) * 10),
            strategy=NoTradeStrategy,
        ).run(
            parameters={"x": [1, 2]},
            objective=("returns.total_return", "max"),
            train_size=4,
            test_size=2,
            max_total_runs=2,
        )

    assert engine.calls == []


def test_explicit_total_run_cap_can_allow_execution() -> None:
    engine = CountingEngine()

    result = WalkForwardStudy(
        engine=engine,
        bars=make_bars(closes=(100.0,) * 8),
        strategy=NoTradeStrategy,
    ).run(
        parameters={"x": [1]},
        objective=("returns.total_return", "max"),
        train_size=4,
        test_size=2,
        max_total_runs=4,
    )

    assert result.execution_scale.max_total_runs == 4
    assert result.execution_scale.planned_total_runs == 4
    assert len(engine.calls) == 4


def test_max_candidates_cap_fails_before_execution() -> None:
    engine = CountingEngine()

    with pytest.raises(ValueError, match="max_candidates"):
        WalkForwardStudy(
            engine=engine,
            bars=make_bars(closes=(100.0,) * 8),
            strategy=NoTradeStrategy,
        ).run(
            parameters={"x": [1, 2]},
            objective=("returns.total_return", "max"),
            train_size=4,
            test_size=2,
            max_candidates=1,
        )

    assert engine.calls == []
