from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, cast

from quantcraft.backtest import BacktestStrategyConstructionError
from quantcraft.data import BarSeries
from quantcraft.research._parameter_search import (
    _candidate_count,
    _GridSearchResult,
    _GridSearchRow,
    _ParameterSearch,
    _validate_max_candidates,
    _validate_parameter_grid,
)
from quantcraft.research._study_metrics import (
    METRIC_KEYS,
    Constraint,
    JSONScalar,
    Objective,
    extract_metrics,
    normalize_metrics,
    validate_objective,
)
from quantcraft.research.validation.results import (
    ValidationArtifact,
    ValidationDiagnostic,
    ValidationProvenance,
    ValidationStatus,
    ValidationStepResult,
)
from quantcraft.research.validation.splits import RollingSplitPolicy, SplitWindow
from quantcraft.strategy import Strategy, StrategyConfig


@dataclass(frozen=True, slots=True)
class WalkForwardFoldResult:
    fold_index: int
    status: ValidationStatus
    window: SplitWindow
    train_result: ValidationStepResult | None
    selected_candidate_index: int | None
    selected_config: Mapping[str, object] | None
    selected_train_run_label: str | None
    oos_test_run_label: str | None
    train_metrics: Mapping[str, object]
    test_metrics: Mapping[str, object]
    diagnostics: tuple[ValidationDiagnostic, ...]
    artifacts: Mapping[str, ValidationArtifact]
    provenance: ValidationProvenance

    def __post_init__(self) -> None:
        if self.selected_config is not None:
            object.__setattr__(
                self, "selected_config", MappingProxyType(dict(self.selected_config))
            )
        object.__setattr__(self, "train_metrics", MappingProxyType(dict(self.train_metrics)))
        object.__setattr__(self, "test_metrics", MappingProxyType(dict(self.test_metrics)))
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        object.__setattr__(self, "artifacts", MappingProxyType(dict(self.artifacts)))


@dataclass(frozen=True, slots=True)
class WalkForwardValidationResult:
    status: ValidationStatus
    folds: tuple[WalkForwardFoldResult, ...]
    step_results: tuple[ValidationStepResult, ...]
    summary: Mapping[str, object]
    diagnostics: tuple[ValidationDiagnostic, ...]
    artifacts: Mapping[str, ValidationArtifact]
    provenance: ValidationProvenance

    def __post_init__(self) -> None:
        object.__setattr__(self, "folds", tuple(self.folds))
        object.__setattr__(self, "step_results", tuple(self.step_results))
        object.__setattr__(self, "summary", MappingProxyType(dict(self.summary)))
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        object.__setattr__(self, "artifacts", MappingProxyType(dict(self.artifacts)))

    def to_records(self) -> list[dict[str, object]]:
        return [_fold_record(fold) for fold in self.folds]

    def to_candidate_records(self) -> list[dict[str, object]]:
        records: list[dict[str, object]] = []
        for step in self.step_results:
            for record in step.records:
                records.append(dict(record))
        return records


class WalkForwardValidation:
    __slots__ = ("engine", "bars", "strategy", "split_policy", "objective")

    def __init__(
        self,
        *,
        engine: object,
        bars: BarSeries,
        strategy: type[Strategy[StrategyConfig]],
        split_policy: RollingSplitPolicy,
        objective: tuple[str, Literal["max", "min"]],
    ) -> None:
        if not hasattr(engine, "run") or not callable(engine.run):
            raise TypeError("engine must expose a callable run method")
        if not isinstance(bars, BarSeries):
            raise TypeError("bars must be a BarSeries instance")
        if not isinstance(strategy, type) or not issubclass(strategy, Strategy):
            raise TypeError("strategy must be a Strategy class")
        if not isinstance(split_policy, RollingSplitPolicy):
            raise TypeError("split_policy must be a RollingSplitPolicy instance")
        self.engine = engine
        self.bars = bars
        self.strategy = strategy
        self.split_policy = split_policy
        self.objective = validate_objective(objective)

    def run(
        self,
        parameters: Mapping[str, Sequence[JSONScalar]],
        constraint: Callable[[Mapping[str, JSONScalar]], bool] | None = None,
        max_candidates: int | None = 1000,
        max_total_runs: int | None = None,
    ) -> WalkForwardValidationResult:
        grid = _validate_parameter_grid(parameters)
        if not grid:
            raise ValueError("parameters must include at least one parameter")
        self.strategy.config_type.validate_override_names(tuple(grid))
        limit = _validate_max_candidates(max_candidates)
        total_limit = _validate_max_total_runs(max_total_runs)
        raw_count = _candidate_count(grid)
        if limit is not None and raw_count > limit:
            raise ValueError(f"raw candidate count {raw_count} exceeds max_candidates {limit}")
        windows = self.split_policy.split(self.bars)
        if not windows:
            raise ValueError("bars cannot produce a complete fold")
        planned_total = len(windows) * (raw_count + 1)
        if total_limit is not None and planned_total > total_limit:
            raise ValueError(
                f"planned total runs {planned_total} exceeds max_total_runs {total_limit}"
            )

        folds = tuple(
            self._run_fold(
                window=window, parameters=grid, constraint=constraint, max_candidates=limit
            )
            for window in windows
        )
        step_results = tuple(fold.train_result for fold in folds if fold.train_result is not None)
        diagnostics = tuple(
            diagnostic
            for fold in folds
            for diagnostic in (
                fold.diagnostics
                + (fold.train_result.diagnostics if fold.train_result is not None else ())
            )
        )
        artifacts = {
            "walk_forward_fold_records": ValidationArtifact(
                name="walk_forward_fold_records",
                kind="fold_records",
                value=[_fold_record(f) for f in folds],
            ),
            "walk_forward_candidate_records": ValidationArtifact(
                name="walk_forward_candidate_records",
                kind="candidate_records",
                value=[dict(r) for step in step_results for r in step.records],
            ),
        }
        status = "failed" if any(fold.status == "failed" for fold in folds) else "success"
        summary = {
            "fold_count": len(folds),
            "successful_fold_count": sum(1 for fold in folds if fold.status == "success"),
            "failed_fold_count": sum(1 for fold in folds if fold.status == "failed"),
            "objective_metric_path": self.objective[0],
            "objective_direction": self.objective[1],
            "raw_candidate_count_per_fold": raw_count,
            "planned_total_runs": planned_total,
        }
        return WalkForwardValidationResult(
            status=cast(ValidationStatus, status),
            folds=folds,
            step_results=step_results,
            summary=summary,
            diagnostics=diagnostics,
            artifacts=artifacts,
            provenance=self._provenance(
                raw_count=raw_count,
                max_candidates=limit,
                windows=windows,
                summary=summary,
            ),
        )

    def _run_fold(
        self,
        *,
        window: SplitWindow,
        parameters: Mapping[str, Sequence[JSONScalar]],
        constraint: Constraint | None,
        max_candidates: int | None,
    ) -> WalkForwardFoldResult:
        train_bars = _slice_bars(self.bars, window.train_start_index, window.train_end_index)
        test_bars = _slice_bars(self.bars, window.test_start_index, window.test_end_index)
        train_result: _GridSearchResult | None = None
        selected: _GridSearchRow | None = None
        selected_config_mapping: Mapping[str, object] | None = None
        test_label = f"walk-forward-fold-{window.fold_index}-test"
        try:
            train_result = _ParameterSearch(
                engine=self.engine, bars=train_bars, strategy=self.strategy
            ).grid_search(
                parameters=parameters,
                constraint=constraint,
                objective=self.objective,
                max_candidates=max_candidates,
                fail_fast=False,
            )
            selected = train_result.best(self.objective)
            selected_config = self.strategy.config_type(**dict(selected.candidate_parameters))
            selected_config_mapping = MappingProxyType(selected_config.to_mapping())
        except Exception as error:
            return self._failed_fold(
                window=window,
                train_result=train_result,
                selected=selected,
                selected_config=selected_config_mapping,
                test_label=None,
                max_candidates=max_candidates,
                provenance_bars=train_bars,
                code="fold_selection",
                error=error,
            )
        try:
            test_result = self.engine.run(
                bars=test_bars,
                strategy=self.strategy,
                config=selected_config,
                label=test_label,
            )
            test_metrics, _states = normalize_metrics(extract_metrics(test_result))
        except BacktestStrategyConstructionError as error:
            return self._failed_fold(
                window=window,
                train_result=train_result,
                selected=selected,
                selected_config=selected_config_mapping,
                test_label=test_label,
                max_candidates=max_candidates,
                provenance_bars=test_bars,
                code="test_strategy_construction",
                error=error.original,
            )
        except Exception as error:
            return self._failed_fold(
                window=window,
                train_result=train_result,
                selected=selected,
                selected_config=selected_config_mapping,
                test_label=test_label,
                max_candidates=max_candidates,
                provenance_bars=test_bars,
                code="fold_execution",
                error=error,
            )

        step = _grid_step_result(
            fold_index=window.fold_index,
            window=window,
            result=train_result,
            objective=self.objective,
            strategy=self.strategy,
            bars=train_bars,
            max_candidates=max_candidates,
        )
        provenance = _fold_provenance(
            self.strategy,
            test_bars,
            self.objective,
            window,
            train_result,
            selected,
            test_label,
            max_candidates,
        )
        return WalkForwardFoldResult(
            fold_index=window.fold_index,
            status="success",
            window=window,
            train_result=step,
            selected_candidate_index=selected.run_index,
            selected_config=selected_config_mapping,
            selected_train_run_label=f"candidate-search-{selected.run_index}",
            oos_test_run_label=f"walk-forward-fold-{window.fold_index}-test",
            train_metrics=selected.metrics,
            test_metrics=test_metrics,
            diagnostics=(),
            artifacts={
                f"walk_forward_fold_{window.fold_index}_oos_backtest": ValidationArtifact(
                    f"walk_forward_fold_{window.fold_index}_oos_backtest",
                    "backtest_result",
                    test_result,
                )
            },
            provenance=provenance,
        )

    def _failed_fold(
        self,
        *,
        window: SplitWindow,
        train_result: _GridSearchResult | None,
        selected: _GridSearchRow | None,
        selected_config: Mapping[str, object] | None,
        test_label: str | None,
        max_candidates: int | None,
        provenance_bars: BarSeries,
        code: str,
        error: BaseException,
    ) -> WalkForwardFoldResult:
        diagnostic = ValidationDiagnostic(
            severity="error",
            code=code,
            message=str(error),
            fold_index=window.fold_index,
            error_type=type(error).__name__,
            error_message=str(error),
        )
        step = (
            None
            if train_result is None
            else _grid_step_result(
                fold_index=window.fold_index,
                window=window,
                result=train_result,
                objective=self.objective,
                strategy=self.strategy,
                bars=_slice_bars(self.bars, window.train_start_index, window.train_end_index),
                max_candidates=max_candidates,
            )
        )
        return WalkForwardFoldResult(
            fold_index=window.fold_index,
            status="failed",
            window=window,
            train_result=step,
            selected_candidate_index=selected.run_index if selected is not None else None,
            selected_config=selected_config,
            selected_train_run_label=f"candidate-search-{selected.run_index}"
            if selected is not None
            else None,
            oos_test_run_label=test_label,
            train_metrics=selected.metrics if selected is not None else {},
            test_metrics={},
            diagnostics=(diagnostic,),
            artifacts={},
            provenance=(
                ValidationProvenance()
                if train_result is None
                else _fold_provenance(
                    self.strategy,
                    provenance_bars,
                    self.objective,
                    window,
                    train_result,
                    selected,
                    test_label,
                    max_candidates,
                )
            ),
        )

    def _provenance(
        self,
        *,
        raw_count: int,
        max_candidates: int | None,
        windows: tuple[SplitWindow, ...],
        summary: Mapping[str, object],
    ) -> ValidationProvenance:
        return ValidationProvenance(
            strategy={"module": self.strategy.__module__, "qualname": self.strategy.__qualname__},
            data=_data_provenance(self.bars),
            objective={"metric_path": self.objective[0], "direction": self.objective[1]},
            split={
                "policy": "rolling",
                "train_size": self.split_policy.train_size,
                "test_size": self.split_policy.test_size,
                "step_size": self.split_policy.step_size or self.split_policy.test_size,
                "fold_count": len(windows),
            },
            candidates={
                "raw_count": raw_count,
                "max_candidates": max_candidates,
            },
            selection={},
            runs={"planned_total_runs": summary["planned_total_runs"]},
        )


def _grid_step_result(
    *,
    fold_index: int,
    window: SplitWindow,
    result: _GridSearchResult,
    objective: Objective,
    strategy: type[Strategy[StrategyConfig]],
    bars: BarSeries,
    max_candidates: int | None,
) -> ValidationStepResult:
    records = tuple(_candidate_record(fold_index, window, record) for record in result.to_records())
    diagnostics = tuple(
        ValidationDiagnostic(
            severity="error" if row.status == "failed" else "warning",
            code=f"candidate_{row.status}",
            message=row.error_message or row.rejection_stage or row.failure_stage or row.status,
            fold_index=fold_index,
            candidate_index=row.run_index,
            error_type=row.error_type,
            error_message=row.error_message,
        )
        for row in result.rows
        if row.status != "success"
    )
    return ValidationStepResult(
        name=f"walk_forward_fold_{fold_index}_train_candidates",
        status="success" if result.eligible_count else "rejected",
        summary={
            "raw_count": result.candidate_count,
            "eligible_count": result.eligible_count,
            "rejected_count": result.rejected_count,
            "failed_count": result.failed_count,
        },
        records=records,
        diagnostics=diagnostics,
        artifacts={
            f"walk_forward_fold_{fold_index}_candidate_records": ValidationArtifact(
                f"walk_forward_fold_{fold_index}_candidate_records",
                "candidate_records",
                [dict(record) for record in records],
            )
        },
        provenance=_fold_provenance(
            strategy, bars, objective, window, result, None, None, max_candidates
        ),
    )


def _fold_provenance(
    strategy: type[Strategy[StrategyConfig]],
    bars: BarSeries,
    objective: Objective,
    window: SplitWindow,
    result: _GridSearchResult,
    selected: _GridSearchRow | None,
    test_label: str | None,
    max_candidates: int | None,
) -> ValidationProvenance:
    selected_config = dict(selected.strategy_config) if selected is not None else None
    return ValidationProvenance(
        strategy={"module": strategy.__module__, "qualname": strategy.__qualname__},
        data=_data_provenance(bars),
        objective={"metric_path": objective[0], "direction": objective[1]},
        split={
            "policy": "rolling",
            "fold_index": window.fold_index,
            "train_start_index": window.train_start_index,
            "train_end_index": window.train_end_index,
            "test_start_index": window.test_start_index,
            "test_end_index": window.test_end_index,
        },
        candidates={
            "raw_count": result.candidate_count,
            "eligible_count": result.eligible_count,
            "rejected_count": result.rejected_count,
            "failed_count": result.failed_count,
            "max_candidates": max_candidates,
        },
        selection={
            "selected_candidate_index": selected.run_index if selected is not None else None,
            "selected_config": selected_config,
        },
        runs={
            "candidate_run_labels": tuple(
                f"candidate-search-{row.run_index}" for row in result.successful()
            ),
            "selected_train_run_label": f"candidate-search-{selected.run_index}"
            if selected is not None
            else None,
            "oos_test_run_label": test_label,
        },
    )


def _candidate_record(
    fold_index: int, window: SplitWindow, record: Mapping[str, object]
) -> Mapping[str, object]:
    enriched: dict[str, object] = {
        "fold_index": fold_index,
        "train_start_index": window.train_start_index,
        "train_end_index": window.train_end_index,
        "test_start_index": window.test_start_index,
        "test_end_index": window.test_end_index,
    }
    enriched.update(record)
    return MappingProxyType(enriched)


def _fold_record(fold: WalkForwardFoldResult) -> dict[str, object]:
    record: dict[str, object] = {
        "fold_index": fold.fold_index,
        "status": fold.status,
        "selected_candidate_index": fold.selected_candidate_index,
        "selected_config": dict(fold.selected_config) if fold.selected_config else None,
        "selected_train_run_label": fold.selected_train_run_label,
        "oos_test_run_label": fold.oos_test_run_label,
    }
    for key in METRIC_KEYS:
        record[f"train.{key}"] = _record_value(fold.train_metrics.get(key))
        record[f"test.{key}"] = _record_value(fold.test_metrics.get(key))
    return record


def _record_value(value: object) -> object:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _data_provenance(bars: BarSeries) -> Mapping[str, object]:
    return {
        "symbol": bars.symbol,
        "timeframe": bars.timeframe,
        "bar_count": len(bars.rows),
        "start_timestamp": bars.rows[0].timestamp if bars.rows else None,
        "end_timestamp": bars.rows[-1].timestamp if bars.rows else None,
    }


def _slice_bars(bars: BarSeries, start: int, end: int) -> BarSeries:
    return BarSeries(
        symbol=bars.symbol,
        timeframe=bars.timeframe,
        bar_type=bars.bar_type,
        rows=bars.rows[start:end],
    )


def _validate_max_total_runs(value: int | None) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("max_total_runs must be a positive integer or None")
    if value <= 0:
        raise ValueError("max_total_runs must be a positive integer or None")
    return value
