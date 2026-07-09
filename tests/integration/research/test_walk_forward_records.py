from __future__ import annotations

import json

from quantcraft.research import RollingSplitPolicy, WalkForwardValidation
from tests.integration.research.support_parameter_studies import (
    WfaRoundTripStrategy,
    engine,
    walk_forward_bars,
)


def test_real_wfa_records_are_portable_and_joinable() -> None:
    result = WalkForwardValidation(
        engine=engine(),
        bars=walk_forward_bars(),
        strategy=WfaRoundTripStrategy,
        split_policy=RollingSplitPolicy(train_size=6, test_size=3),
        objective=("returns.total_return", "max"),
    ).run(parameters={"fast": [2, 3], "slow": [3, 5]})

    fold_records = result.to_records()
    candidate_records = result.to_candidate_records()

    assert len(fold_records) == len(result.folds)
    assert {record["fold_index"] for record in fold_records} == {0, 1}
    assert {record["fold_index"] for record in candidate_records} == {0, 1}
    assert "selected_config" in fold_records[0]
    assert "candidate_parameters" in candidate_records[0]
    assert result.provenance.objective == {
        "metric_path": "returns.total_return",
        "direction": "max",
    }
    json.dumps(fold_records, allow_nan=False)
    json.dumps(candidate_records, allow_nan=False)


def test_wfa_result_carries_required_candidate_and_fold_provenance() -> None:
    result = WalkForwardValidation(
        engine=engine(),
        bars=walk_forward_bars(),
        strategy=WfaRoundTripStrategy,
        split_policy=RollingSplitPolicy(train_size=6, test_size=3),
        objective=("returns.total_return", "max"),
    ).run(parameters={"fast": [2, 3], "slow": [3, 5]})

    first_fold = result.folds[0]

    assert first_fold.provenance.candidates["raw_count"] == 4
    assert "eligible_count" in first_fold.provenance.candidates
    assert "selected_candidate_index" in first_fold.provenance.selection
    assert "selected_config" in first_fold.provenance.selection
    assert "selected_train_run_label" in first_fold.provenance.runs
    assert "oos_test_run_label" in first_fold.provenance.runs
    assert first_fold.window.train_start_index == 0
    assert first_fold.window.test_start_index == 6
