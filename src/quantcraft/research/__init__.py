from __future__ import annotations

from importlib import import_module

__all__ = [
    "RollingSplitPolicy",
    "SplitWindow",
    "ValidationArtifact",
    "ValidationContext",
    "ValidationDiagnostic",
    "ValidationPipeline",
    "ValidationProvenance",
    "ValidationReport",
    "ValidationStatus",
    "ValidationStep",
    "ValidationStepResult",
    "WalkForwardFoldResult",
    "WalkForwardValidation",
    "WalkForwardValidationResult",
    "qc",
    "ta",
]

_VALIDATION_EXPORTS = frozenset(__all__) - {"qc", "ta"}


def __getattr__(name: str) -> object:
    if name in _VALIDATION_EXPORTS:
        return getattr(import_module("quantcraft.research.validation"), name)
    if name in {"qc", "ta"}:
        return import_module(f"quantcraft.research.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
