from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Literal

ValidationStatus = Literal["success", "inconclusive", "failed", "rejected", "skipped"]

_ALLOWED_VALIDATION_STATUSES = frozenset(
    ("success", "inconclusive", "failed", "rejected", "skipped")
)


def _copy_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class ValidationDiagnostic:
    severity: Literal["info", "warning", "error"]
    code: str
    message: str
    step_name: str | None = None
    fold_index: int | None = None
    candidate_index: int | None = None
    error_type: str | None = None
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationArtifact:
    name: str
    kind: Literal["backtest_result", "candidate_records", "fold_records", "summary", "custom"]
    value: object


@dataclass(frozen=True, slots=True)
class ValidationProvenance:
    strategy: Mapping[str, object] = field(default_factory=dict)
    data: Mapping[str, object] = field(default_factory=dict)
    objective: Mapping[str, object] = field(default_factory=dict)
    split: Mapping[str, object] = field(default_factory=dict)
    candidates: Mapping[str, object] = field(default_factory=dict)
    selection: Mapping[str, object] = field(default_factory=dict)
    runs: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("strategy", "data", "objective", "split", "candidates", "selection", "runs"):
            object.__setattr__(self, name, _copy_mapping(getattr(self, name)))


@dataclass(frozen=True, slots=True)
class ValidationStepResult:
    name: str
    status: ValidationStatus
    summary: Mapping[str, object]
    records: tuple[Mapping[str, object], ...]
    diagnostics: tuple[ValidationDiagnostic, ...]
    artifacts: Mapping[str, ValidationArtifact]
    provenance: ValidationProvenance

    def __post_init__(self) -> None:
        if self.status not in _ALLOWED_VALIDATION_STATUSES:
            raise ValueError(f"unsupported validation status {self.status!r}")
        object.__setattr__(self, "summary", _copy_mapping(self.summary))
        object.__setattr__(self, "records", tuple(_copy_mapping(record) for record in self.records))
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        object.__setattr__(self, "artifacts", MappingProxyType(dict(self.artifacts)))


@dataclass(frozen=True, slots=True)
class ValidationReport:
    status: ValidationStatus
    step_results: tuple[ValidationStepResult, ...]
    diagnostics: tuple[ValidationDiagnostic, ...]
    artifacts: Mapping[str, ValidationArtifact]
    provenance: ValidationProvenance

    def __post_init__(self) -> None:
        if self.status not in _ALLOWED_VALIDATION_STATUSES:
            raise ValueError(f"unsupported validation status {self.status!r}")
        object.__setattr__(self, "step_results", tuple(self.step_results))
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        object.__setattr__(self, "artifacts", MappingProxyType(dict(self.artifacts)))

    def to_records(self) -> list[dict[str, object]]:
        records: list[dict[str, object]] = []
        for result in self.step_results:
            for record in result.records:
                enriched: dict[str, object] = {
                    "step_name": result.name,
                    "step_status": result.status,
                }
                enriched.update(record)
                records.append(enriched)
        return records
