from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Protocol

from quantcraft.data import BarSeries, HistoricalDataSource
from quantcraft.research.validation.results import (
    ValidationArtifact,
    ValidationDiagnostic,
    ValidationProvenance,
    ValidationReport,
    ValidationStatus,
    ValidationStepResult,
)
from quantcraft.strategy import Strategy, StrategyConfig


@dataclass(frozen=True, slots=True)
class ValidationContext:
    source: HistoricalDataSource | BarSeries
    strategy: type[Strategy[StrategyConfig]]
    config: StrategyConfig | None
    engine: object
    artifacts: Mapping[str, ValidationArtifact] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifacts", MappingProxyType(dict(self.artifacts)))


class ValidationStep(Protocol):
    name: str

    def run(self, context: ValidationContext) -> ValidationStepResult: ...


class ValidationPipeline:
    __slots__ = ("steps",)

    def __init__(self, steps: Sequence[ValidationStep]) -> None:
        self.steps = tuple(steps)

    def run(
        self,
        *,
        source: HistoricalDataSource | BarSeries,
        strategy: type[Strategy[StrategyConfig]],
        config: StrategyConfig | None,
        engine: object,
    ) -> ValidationReport:
        step_results: list[ValidationStepResult] = []
        artifacts: dict[str, ValidationArtifact] = {}
        stopped = False

        for step in self.steps:
            if stopped:
                result = _skipped_result(step.name)
            else:
                context = ValidationContext(
                    source=source,
                    strategy=strategy,
                    config=config,
                    engine=engine,
                    artifacts=artifacts,
                )
                result = step.run(context)
                if result.status in {"failed", "rejected"}:
                    stopped = True
            _merge_artifacts(artifacts, result.artifacts)
            step_results.append(result)

        diagnostics = tuple(
            diagnostic for result in step_results for diagnostic in result.diagnostics
        )
        return ValidationReport(
            status=_report_status(tuple(step_results)),
            summary=_report_summary(tuple(step_results)),
            step_results=tuple(step_results),
            diagnostics=diagnostics,
            artifacts=artifacts,
            provenance=_report_provenance(source=source, strategy=strategy),
        )


def _merge_artifacts(
    target: dict[str, ValidationArtifact], source: Mapping[str, ValidationArtifact]
) -> None:
    for name, artifact in source.items():
        if name in target:
            raise ValueError(f"duplicate validation artifact name {name!r}")
        if artifact.name != name:
            raise ValueError(
                f"artifact mapping key {name!r} does not match artifact name {artifact.name!r}"
            )
        target[name] = artifact


def _report_status(results: tuple[ValidationStepResult, ...]) -> ValidationStatus:
    statuses = {result.status for result in results}
    if "failed" in statuses:
        return "failed"
    if "rejected" in statuses:
        return "rejected"
    if "inconclusive" in statuses:
        return "inconclusive"
    return "success"


def _report_summary(results: tuple[ValidationStepResult, ...]) -> Mapping[str, object]:
    return {
        "step_count": len(results),
        "successful_step_count": sum(1 for result in results if result.status == "success"),
        "inconclusive_step_count": sum(1 for result in results if result.status == "inconclusive"),
        "failed_step_count": sum(1 for result in results if result.status == "failed"),
        "rejected_step_count": sum(1 for result in results if result.status == "rejected"),
        "skipped_step_count": sum(1 for result in results if result.status == "skipped"),
    }


def _skipped_result(name: str) -> ValidationStepResult:
    diagnostic = ValidationDiagnostic(
        severity="info",
        code="pipeline_step_skipped_after_stop",
        message="Step skipped because a previous validation step stopped the pipeline.",
        step_name=name,
    )
    return ValidationStepResult(
        name=name,
        status="skipped",
        summary={"skipped": True},
        records=(),
        diagnostics=(diagnostic,),
        artifacts={},
        provenance=ValidationProvenance(),
    )


def _report_provenance(
    *, source: HistoricalDataSource | BarSeries, strategy: type[Strategy[StrategyConfig]]
) -> ValidationProvenance:
    data: dict[str, object] = {}
    if isinstance(source, BarSeries):
        data.update(
            {
                "symbol": source.symbol,
                "timeframe": source.timeframe,
                "bar_count": len(source.rows),
                "start_timestamp": source.rows[0].timestamp if source.rows else None,
                "end_timestamp": source.rows[-1].timestamp if source.rows else None,
            }
        )
    return ValidationProvenance(
        strategy={"module": strategy.__module__, "qualname": strategy.__qualname__},
        data=data,
        objective={},
        split={},
        candidates={},
        selection={},
        runs={},
    )
