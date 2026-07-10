from __future__ import annotations

import importlib.util

import pytest

import quantcraft.research as research
from quantcraft.research import (
    RollingSplitPolicy,
    SplitWindow,
    ValidationArtifact,
    ValidationDiagnostic,
    ValidationPipeline,
    ValidationProvenance,
    ValidationReport,
    ValidationStepResult,
    WalkForwardFoldResult,
    WalkForwardValidationResult,
)
from quantcraft.research.validation import ValidationStep


def test_validation_public_exports_replace_old_beta_studies() -> None:
    for name in (
        "ValidationPipeline",
        "ValidationStep",
        "ValidationContext",
        "ValidationReport",
        "ValidationStepResult",
        "ValidationDiagnostic",
        "ValidationProvenance",
        "ValidationArtifact",
        "ValidationStatus",
        "SplitWindow",
        "RollingSplitPolicy",
        "WalkForwardValidation",
        "WalkForwardValidationResult",
        "WalkForwardFoldResult",
    ):
        assert hasattr(research, name)

    for old_name in (
        "MetricSelectionPolicy",
        "ParameterStudy",
        "GridSearchResult",
        "GridSearchRow",
        "WalkForwardStudy",
        "WalkForwardResult",
        "WalkForwardFold",
    ):
        with pytest.raises(AttributeError):
            getattr(research, old_name)

    assert importlib.util.find_spec("quantcraft.research.parameter_exploration") is None
    assert importlib.util.find_spec("quantcraft.research.walk_forward") is None
    assert importlib.util.find_spec("quantcraft.research.strategy") is None
    assert importlib.util.find_spec("quantcraft.research.series") is None


def test_validation_dataclass_public_schema_is_constructible() -> None:
    diagnostic = ValidationDiagnostic(severity="info", code="ok", message="message")
    artifact = ValidationArtifact(name="summary", kind="summary", value={"ok": True})
    provenance = ValidationProvenance(
        strategy={"module": "tests", "qualname": "Strategy"},
        data={},
        objective={},
        split={},
        candidates={},
        selection={},
        runs={},
    )
    step = ValidationStepResult(
        name="step",
        status="success",
        summary={"ok": True},
        records=({"row": 1},),
        diagnostics=(diagnostic,),
        artifacts={"summary": artifact},
        provenance=provenance,
    )
    report = ValidationReport(
        status="success",
        summary={"step_count": 1},
        step_results=(step,),
        diagnostics=(diagnostic,),
        artifacts={"summary": artifact},
        provenance=provenance,
    )
    window = SplitWindow(
        fold_index=0,
        train_start_index=0,
        train_end_index=2,
        test_start_index=2,
        test_end_index=3,
        train_start_timestamp=1,
        train_end_timestamp=2,
        test_start_timestamp=3,
        test_end_timestamp=3,
    )

    assert isinstance(ValidationPipeline([]), ValidationPipeline)
    assert isinstance(RollingSplitPolicy(train_size=2, test_size=1), RollingSplitPolicy)
    assert report.to_records() == [{"step_name": "step", "step_status": "success", "row": 1}]
    assert window.train_end_index == 2
    assert ValidationStep is not None


def test_validation_public_wfa_results_reject_unknown_status() -> None:
    window = SplitWindow(
        fold_index=0,
        train_start_index=0,
        train_end_index=2,
        test_start_index=2,
        test_end_index=3,
        train_start_timestamp=1,
        train_end_timestamp=2,
        test_start_timestamp=3,
        test_end_timestamp=3,
    )

    with pytest.raises(ValueError, match="unsupported validation status"):
        WalkForwardFoldResult(
            fold_index=0,
            status="error",  # type: ignore[arg-type]
            window=window,
            train_result=None,
            selected_candidate_index=None,
            selected_config=None,
            selected_train_run_label=None,
            oos_test_run_label=None,
            train_metrics={},
            test_metrics={},
            diagnostics=(),
            artifacts={},
            provenance=ValidationProvenance(),
        )

    with pytest.raises(ValueError, match="unsupported validation status"):
        WalkForwardValidationResult(
            status="error",  # type: ignore[arg-type]
            folds=(),
            step_results=(),
            summary={},
            diagnostics=(),
            artifacts={},
            provenance=ValidationProvenance(),
        )
