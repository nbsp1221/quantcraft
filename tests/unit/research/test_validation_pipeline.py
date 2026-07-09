from __future__ import annotations

import pytest

from quantcraft.research import (
    ValidationArtifact,
    ValidationPipeline,
    ValidationProvenance,
    ValidationStepResult,
)
from tests.integration.research.support_parameter_studies import (
    WfaRoundTripStrategy,
    engine,
    walk_forward_bars,
)


class Step:
    def __init__(self, name: str, status: str, artifact_name: str | None = None) -> None:
        self.name = name
        self._status = status
        self._artifact_name = artifact_name

    def run(self, context):
        artifacts = {}
        if self._artifact_name is not None:
            artifacts[self._artifact_name] = ValidationArtifact(
                name=self._artifact_name,
                kind="custom",
                value=self.name,
            )
        return ValidationStepResult(
            name=self.name,
            status=self._status,
            summary={"status": self._status},
            records=({"name": self.name},),
            diagnostics=(),
            artifacts=artifacts,
            provenance=ValidationProvenance(),
        )


def run_pipeline(*steps: Step):
    return ValidationPipeline(steps).run(
        source=walk_forward_bars(),
        strategy=WfaRoundTripStrategy,
        config=None,
        engine=engine(),
    )


def test_pipeline_continues_after_success_and_inconclusive() -> None:
    report = run_pipeline(Step("a", "success"), Step("b", "inconclusive"), Step("c", "success"))

    assert report.status == "inconclusive"
    assert [result.name for result in report.step_results] == ["a", "b", "c"]


def test_pipeline_stops_after_failed_and_skips_remaining() -> None:
    report = run_pipeline(Step("a", "failed"), Step("b", "success"))

    assert report.status == "failed"
    assert [result.status for result in report.step_results] == ["failed", "skipped"]
    assert report.step_results[1].diagnostics[0].code == "pipeline_step_skipped_after_stop"


def test_pipeline_stops_after_rejected_and_skips_remaining() -> None:
    report = run_pipeline(Step("a", "rejected"), Step("b", "success"))

    assert report.status == "rejected"
    assert [result.status for result in report.step_results] == ["rejected", "skipped"]


def test_pipeline_rejects_duplicate_artifact_names() -> None:
    with pytest.raises(ValueError, match="duplicate validation artifact"):
        run_pipeline(Step("a", "success", "same"), Step("b", "success", "same"))


def test_validation_step_result_rejects_unknown_status() -> None:
    with pytest.raises(ValueError, match="unsupported validation status"):
        ValidationStepResult(
            name="bad",
            status="error",  # type: ignore[arg-type]
            summary={},
            records=(),
            diagnostics=(),
            artifacts={},
            provenance=ValidationProvenance(),
        )


class ConsumingStep:
    name = "consumer"

    def run(self, context):
        assert context.artifacts["upstream"].value == "producer"
        return ValidationStepResult(
            name=self.name,
            status="success",
            summary={"saw": tuple(context.artifacts)},
            records=(),
            diagnostics=(),
            artifacts={},
            provenance=ValidationProvenance(),
        )


def test_pipeline_threads_prior_step_artifacts_into_next_context() -> None:
    report = run_pipeline(Step("producer", "success", "upstream"), ConsumingStep())

    assert report.step_results[1].summary == {"saw": ("upstream",)}
