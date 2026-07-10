from __future__ import annotations

import pytest

from quantcraft.research._parameter_search import (
    _GridSearchResult,
    _GridSearchRow,
    _ParameterSearch,
)
from tests.unit.research.support_parameter_study import (
    CountingEngine,
    NoTradeStrategy,
    RoundTripStrategy,
    make_bars,
)


def test_internal_parameter_study_covers_success_rejection_and_records() -> None:
    result = _ParameterSearch(
        engine=CountingEngine(),
        bars=make_bars(),
        strategy=RoundTripStrategy,
    ).grid_search(
        parameters={"fast": [2, 3], "slow": [3, 4]},
        constraint=lambda config: config["fast"] < config["slow"],
        objective=("returns.total_return", "max"),
    )

    assert result.candidate_count == 4
    assert result.successful_count == 3
    assert result.rejected_count == 1
    assert result.failed_count == 0
    assert result.eligible_count == 3
    assert result.best().backtest is not None
    assert len(result.top(2)) == 2
    assert len(result.to_records()) == 4


def test_internal_parameter_study_records_strategy_and_constraint_failures() -> None:
    def broken_constraint(config):
        if config["fast"] == 2:
            raise RuntimeError("constraint boom")
        return True

    result = _ParameterSearch(
        engine=CountingEngine(),
        bars=make_bars(),
        strategy=RoundTripStrategy,
    ).grid_search(
        parameters={"fast": [2, 5], "slow": [3]},
        constraint=broken_constraint,
        objective=("returns.total_return", "max"),
    )

    assert result.failed_count == 1
    assert result.successful_count == 1
    assert {row.error_type for row in result.rows} >= {"RuntimeError"}


def test_internal_grid_result_selection_validation_errors() -> None:
    row = _GridSearchRow.rejected(
        run_index=0,
        candidate_parameters={"fast": 3},
        strategy_config={"fast": 3},
        rejection_stage="constraint",
    )
    result = _GridSearchResult(rows=(row,), objective=("returns.total_return", "max"))

    assert result.successful() == ()
    assert result.rejected() == (row,)
    assert result.failed() == ()
    with pytest.raises(ValueError, match="no eligible"):
        result.best()
    with pytest.raises(TypeError, match="positive integer"):
        result.top(1.5)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="positive integer"):
        result.top(0)
    assert _GridSearchResult(rows=(row,)).eligible_count == 0


@pytest.mark.parametrize(
    ("parameters", "error"),
    [
        ([], TypeError),
        ({1: [1]}, TypeError),
        ({"": [1]}, ValueError),
        ({"x": "abc"}, TypeError),
        ({"x": []}, ValueError),
        ({"x": [1, 1]}, ValueError),
        ({"x": [float("inf")]}, ValueError),
        ({"x": [object()]}, TypeError),
    ],
)
def test_internal_parameter_grid_validation_errors(parameters, error) -> None:
    study = _ParameterSearch(engine=CountingEngine(), bars=make_bars(), strategy=NoTradeStrategy)

    with pytest.raises(error):
        study.grid_search(parameters=parameters)


def test_internal_parameter_grid_accepts_json_scalars() -> None:
    result = _ParameterSearch(
        engine=CountingEngine(),
        bars=make_bars(),
        strategy=NoTradeStrategy,
    ).grid_search(parameters={"x": [None, "alpha", True, 1, 1.5]})

    assert result.candidate_count == 5


def test_internal_parameter_study_preflight_validation() -> None:
    with pytest.raises(TypeError, match="engine"):
        _ParameterSearch(engine=object(), bars=make_bars(), strategy=NoTradeStrategy)
    with pytest.raises(TypeError, match="bars"):
        _ParameterSearch(engine=CountingEngine(), bars=object(), strategy=NoTradeStrategy)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="Strategy class"):
        _ParameterSearch(engine=CountingEngine(), bars=make_bars(), strategy=object)  # type: ignore[arg-type]

    study = _ParameterSearch(engine=CountingEngine(), bars=make_bars(), strategy=NoTradeStrategy)
    with pytest.raises(TypeError, match="max_candidates"):
        study.grid_search(parameters={"x": [1]}, max_candidates=True)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="max_candidates"):
        study.grid_search(parameters={"x": [1]}, max_candidates=0)
    with pytest.raises(ValueError, match="exceeds max_candidates"):
        study.grid_search(parameters={"x": [1, 2]}, max_candidates=1)


def test_internal_parameter_study_fail_fast_adds_context_notes() -> None:
    def broken_constraint(config):
        raise RuntimeError("constraint boom")

    study = _ParameterSearch(engine=CountingEngine(), bars=make_bars(), strategy=NoTradeStrategy)

    with pytest.raises(RuntimeError) as exc_info:
        study.grid_search(parameters={"x": [1]}, constraint=broken_constraint, fail_fast=True)

    assert any("stage=constraint" in note for note in exc_info.value.__notes__)
    assert any("candidate_parameters" in note for note in exc_info.value.__notes__)
