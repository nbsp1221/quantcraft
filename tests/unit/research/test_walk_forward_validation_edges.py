from __future__ import annotations

import pytest

from quantcraft.data import BarSeries
from quantcraft.research import RollingSplitPolicy, WalkForwardValidation
from tests.integration.research.support_parameter_studies import (
    WfaRoundTripStrategy,
    engine,
    walk_forward_bars,
)
from tests.unit.research.support_parameter_study import NoTradeStrategy


class FailingOosEngine:
    def __init__(self) -> None:
        self._engine = engine()

    def run(self, **kwargs):
        if kwargs.get("label", "").endswith("-test"):
            raise RuntimeError("oos exploded")
        return self._engine.run(**kwargs)


def test_walk_forward_validation_rejects_bad_constructor_inputs() -> None:
    with pytest.raises(TypeError, match="engine"):
        WalkForwardValidation(
            engine=object(),
            bars=walk_forward_bars(),
            strategy=WfaRoundTripStrategy,
            split_policy=RollingSplitPolicy(train_size=2, test_size=1),
            objective=("returns.total_return", "max"),
        )
    with pytest.raises(TypeError, match="bars"):
        WalkForwardValidation(
            engine=engine(),
            bars=object(),  # type: ignore[arg-type]
            strategy=WfaRoundTripStrategy,
            split_policy=RollingSplitPolicy(train_size=2, test_size=1),
            objective=("returns.total_return", "max"),
        )
    with pytest.raises(TypeError, match="Strategy class"):
        WalkForwardValidation(
            engine=engine(),
            bars=walk_forward_bars(),
            strategy=object,  # type: ignore[arg-type]
            split_policy=RollingSplitPolicy(train_size=2, test_size=1),
            objective=("returns.total_return", "max"),
        )
    with pytest.raises(TypeError, match="RollingSplitPolicy"):
        WalkForwardValidation(
            engine=engine(),
            bars=walk_forward_bars(),
            strategy=WfaRoundTripStrategy,
            split_policy=object(),  # type: ignore[arg-type]
            objective=("returns.total_return", "max"),
        )


def test_walk_forward_validation_rejects_bad_run_limits_and_windows() -> None:
    validation = WalkForwardValidation(
        engine=engine(),
        bars=walk_forward_bars(5),
        strategy=WfaRoundTripStrategy,
        split_policy=RollingSplitPolicy(train_size=3, test_size=2),
        objective=("returns.total_return", "max"),
    )

    with pytest.raises(TypeError, match="max_total_runs"):
        validation.run(parameters={"fast": [2], "slow": [3]}, max_total_runs=True)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="max_total_runs"):
        validation.run(parameters={"fast": [2], "slow": [3]}, max_total_runs=0)
    with pytest.raises(ValueError, match="planned total runs"):
        validation.run(parameters={"fast": [2], "slow": [3]}, max_total_runs=1)

    no_window = WalkForwardValidation(
        engine=engine(),
        bars=walk_forward_bars(4),
        strategy=WfaRoundTripStrategy,
        split_policy=RollingSplitPolicy(train_size=4, test_size=2),
        objective=("returns.total_return", "max"),
    )
    with pytest.raises(ValueError, match="complete fold"):
        no_window.run(parameters={"fast": [2], "slow": [3]})


def test_walk_forward_validation_records_failed_selection_fold() -> None:
    result = WalkForwardValidation(
        engine=engine(),
        bars=walk_forward_bars(8),
        strategy=NoTradeStrategy,
        split_policy=RollingSplitPolicy(train_size=4, test_size=2),
        objective=("trades.win_rate", "max"),
    ).run(parameters={"x": [1]})

    assert result.status == "failed"
    assert result.folds[0].status == "failed"
    assert result.folds[0].diagnostics


def test_walk_forward_validation_preserves_failed_oos_selection_provenance() -> None:
    result = WalkForwardValidation(
        engine=FailingOosEngine(),
        bars=walk_forward_bars(8),
        strategy=WfaRoundTripStrategy,
        split_policy=RollingSplitPolicy(train_size=4, test_size=2),
        objective=("returns.total_return", "max"),
    ).run(parameters={"fast": [2], "slow": [3]}, max_candidates=7)

    fold = result.folds[0]
    assert result.status == "failed"
    assert fold.status == "failed"
    assert fold.selected_candidate_index == 0
    assert fold.selected_config == {"fast": 2, "slow": 3}
    assert fold.selected_train_run_label == "candidate-search-0"
    assert fold.oos_test_run_label == "walk-forward-fold-0-test"
    assert fold.train_metrics["returns.total_return"] is not None
    assert fold.provenance.candidates["max_candidates"] == 7
    assert fold.provenance.data["bar_count"] == 2
    assert fold.provenance.selection["selected_candidate_index"] == 0


def test_walk_forward_validation_records_configured_candidate_cap() -> None:
    result = WalkForwardValidation(
        engine=engine(),
        bars=walk_forward_bars(8),
        strategy=WfaRoundTripStrategy,
        split_policy=RollingSplitPolicy(train_size=4, test_size=2),
        objective=("returns.total_return", "max"),
    ).run(parameters={"fast": [2], "slow": [3]}, max_candidates=7)

    assert result.provenance.candidates == {"raw_count": 1, "max_candidates": 7}


def test_walk_forward_validation_aggregates_candidate_diagnostics() -> None:
    result = WalkForwardValidation(
        engine=engine(),
        bars=walk_forward_bars(8),
        strategy=WfaRoundTripStrategy,
        split_policy=RollingSplitPolicy(train_size=4, test_size=2),
        objective=("returns.total_return", "max"),
    ).run(
        parameters={"fast": [2, 4], "slow": [3]},
        constraint=lambda candidate: candidate["fast"] < candidate["slow"],
    )

    assert result.status == "success"
    assert any(diagnostic.code == "candidate_rejected" for diagnostic in result.diagnostics)


def test_rolling_split_policy_validation_edges() -> None:
    with pytest.raises(TypeError, match="train_size"):
        RollingSplitPolicy(train_size=True, test_size=1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="test_size"):
        RollingSplitPolicy(train_size=1, test_size=0)
    with pytest.raises(ValueError, match="step_size"):
        RollingSplitPolicy(train_size=1, test_size=1, step_size=0)

    empty = BarSeries(symbol="T", timeframe="1m", bar_type="time", rows=())
    assert RollingSplitPolicy(train_size=1, test_size=1).split(empty) == ()

    with pytest.raises(TypeError, match="BarSeries"):
        RollingSplitPolicy(train_size=1, test_size=1).split(object())  # type: ignore[arg-type]
