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
