from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from statistics import mean, median
from types import MappingProxyType
from typing import Literal

from quantcraft.backtest import BacktestResult, BacktestStrategyConstructionError
from quantcraft.data import BarSeries
from quantcraft.research._study_metrics import (
    METRIC_KEYS,
    Constraint,
    JSONScalar,
    MetricState,
    MetricValue,
    Objective,
    extract_metrics,
    normalize_metrics,
    validate_objective,
)
from quantcraft.research.parameter_exploration import (
    GridSearchResult,
    GridSearchRow,
    ParameterStudy,
    _candidate_count,
    _validate_max_candidates,
    _validate_parameter_grid,
)
from quantcraft.strategy import Strategy, StrategyConfig

FoldStatus = Literal["success", "failed"]
FoldFailureStage = Literal[
    "train_search",
    "selection",
    "test_strategy_construction",
    "test_backtest",
    "test_metric_extraction",
]
DiagnosticSeverity = Literal["info", "warning"]
DiagnosticCode = Literal[
    "fold_execution_failed",
    "no_selected_config",
    "undefined_oos_objective",
    "no_closed_trades",
    "zero_successful_oos_folds",
]


@dataclass(frozen=True, slots=True)
class _FoldWindow:
    fold_index: int
    train_start_index: int
    train_end_index: int
    test_start_index: int
    test_end_index: int
    train_start_timestamp: int
    train_end_timestamp: int
    test_start_timestamp: int
    test_end_timestamp: int


@dataclass(frozen=True, slots=True)
class WalkForwardExecutionScale:
    fold_count: int
    raw_candidate_count_per_fold: int
    planned_train_candidate_runs: int
    planned_selected_test_runs: int
    planned_total_runs: int
    max_candidates: int | None
    max_total_runs: int | None


@dataclass(frozen=True, slots=True)
class WalkForwardFold:
    fold_index: int
    status: FoldStatus
    train_start_index: int
    train_end_index: int
    test_start_index: int
    test_end_index: int
    train_start_timestamp: int
    train_end_timestamp: int
    test_start_timestamp: int
    test_end_timestamp: int
    train_result: GridSearchResult | None
    selected_train_row: GridSearchRow | None
    selected_config: Mapping[str, JSONScalar] | None
    selected_test_result: BacktestResult | None
    train_metrics: Mapping[str, MetricValue]
    train_metric_states: Mapping[str, MetricState]
    test_metrics: Mapping[str, MetricValue]
    test_metric_states: Mapping[str, MetricState]
    failure_stage: FoldFailureStage | None
    error_type: str | None
    error_message: str | None

    def __post_init__(self) -> None:
        if self.selected_config is not None:
            object.__setattr__(
                self,
                "selected_config",
                MappingProxyType(dict(self.selected_config)),
            )
        object.__setattr__(self, "train_metrics", MappingProxyType(dict(self.train_metrics)))
        object.__setattr__(
            self,
            "train_metric_states",
            MappingProxyType(dict(self.train_metric_states)),
        )
        object.__setattr__(self, "test_metrics", MappingProxyType(dict(self.test_metrics)))
        object.__setattr__(
            self,
            "test_metric_states",
            MappingProxyType(dict(self.test_metric_states)),
        )


@dataclass(frozen=True, slots=True)
class WalkForwardOosSummary:
    fold_count: int
    successful_fold_count: int
    failed_fold_count: int
    failure_rate: float
    objective_metric_path: str
    objective_direction: Literal["max", "min"]
    objective_metric_state_counts: Mapping[str, int]
    metric_state_counts: Mapping[str, Mapping[str, int]]
    metric_summaries: Mapping[str, Mapping[str, int | float]]
    objective_mean: float | None
    objective_median: float | None
    objective_min: float | None
    objective_max: float | None
    positive_fold_ratio: float | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "objective_metric_state_counts",
            MappingProxyType(dict(self.objective_metric_state_counts)),
        )
        object.__setattr__(
            self,
            "metric_state_counts",
            MappingProxyType(
                {
                    key: MappingProxyType(dict(value))
                    for key, value in self.metric_state_counts.items()
                }
            ),
        )
        object.__setattr__(
            self,
            "metric_summaries",
            MappingProxyType(
                {key: MappingProxyType(dict(value)) for key, value in self.metric_summaries.items()}
            ),
        )


@dataclass(frozen=True, slots=True)
class WalkForwardDiagnostic:
    severity: DiagnosticSeverity
    code: DiagnosticCode
    message: str
    fold_indexes: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class WalkForwardResult:
    folds: tuple[WalkForwardFold, ...]
    objective: Objective
    mode: Literal["rolling"]
    train_size: int
    test_size: int
    step_size: int
    execution_scale: WalkForwardExecutionScale
    oos_summary: WalkForwardOosSummary
    diagnostics: tuple[WalkForwardDiagnostic, ...]

    @property
    def fold_count(self) -> int:
        return len(self.folds)

    @property
    def successful_fold_count(self) -> int:
        return len([fold for fold in self.folds if fold.status == "success"])

    @property
    def failed_fold_count(self) -> int:
        return len([fold for fold in self.folds if fold.status == "failed"])

    def to_records(self) -> list[dict[str, object]]:
        metric_path, direction = self.objective
        return [
            _fold_to_record(fold, metric_path=metric_path, direction=direction)
            for fold in self.folds
        ]

    def to_candidate_records(self) -> list[dict[str, object]]:
        records: list[dict[str, object]] = []
        for fold in self.folds:
            if fold.train_result is None:
                continue
            for record in fold.train_result.to_records():
                enriched: dict[str, object] = {
                    "fold_index": fold.fold_index,
                    "train_start_index": fold.train_start_index,
                    "train_end_index": fold.train_end_index,
                    "test_start_index": fold.test_start_index,
                    "test_end_index": fold.test_end_index,
                    "train_start_timestamp": fold.train_start_timestamp,
                    "train_end_timestamp": fold.train_end_timestamp,
                    "test_start_timestamp": fold.test_start_timestamp,
                    "test_end_timestamp": fold.test_end_timestamp,
                }
                enriched.update(record)
                records.append(enriched)
        return records


class WalkForwardStudy:
    __slots__ = ("engine", "bars", "strategy")

    def __init__(
        self,
        *,
        engine: object,
        bars: BarSeries,
        strategy: type[Strategy[StrategyConfig]],
    ) -> None:
        if not hasattr(engine, "run") or not callable(engine.run):
            raise TypeError("engine must expose a callable run method")
        if not isinstance(bars, BarSeries):
            raise TypeError("bars must be a BarSeries instance")
        if not bars.rows:
            raise ValueError("bars must contain at least one TimeBar")
        if not isinstance(strategy, type) or not issubclass(strategy, Strategy):
            raise TypeError("strategy must be a Strategy class")
        self.engine = engine
        self.bars = bars
        self.strategy = strategy

    def run(
        self,
        *,
        parameters: Mapping[str, Sequence[JSONScalar]],
        objective: Objective,
        constraint: Constraint | None = None,
        train_size: int,
        test_size: int,
        step_size: int | None = None,
        mode: Literal["rolling"] = "rolling",
        max_candidates: int | None = 1000,
        max_total_runs: int | None = None,
    ) -> WalkForwardResult:
        resolved_objective = validate_objective(objective)
        grid = _validate_parameter_grid(parameters)
        if not grid:
            raise ValueError("parameters must include at least one parameter")
        self.strategy.config_type.validate_override_names(tuple(grid))
        limit = _validate_max_candidates(max_candidates)
        total_limit = _validate_max_total_runs(max_total_runs)
        raw_candidate_count = _candidate_count(grid)
        if limit is not None and raw_candidate_count > limit:
            raise ValueError(
                f"raw candidate count {raw_candidate_count} exceeds max_candidates {limit}"
            )
        _validate_mode(mode)
        resolved_step_size = _validate_windows(train_size, test_size, step_size)
        _validate_chronological_bars(self.bars)
        windows = _fold_windows(
            self.bars,
            train_size=train_size,
            test_size=test_size,
            step_size=resolved_step_size,
        )
        if not windows:
            raise ValueError(
                "bars cannot produce a complete fold "
                f"for train_size={train_size}, test_size={test_size}, "
                f"available_bars={len(self.bars.rows)}"
            )
        execution_scale = _execution_scale(
            fold_count=len(windows),
            raw_candidate_count=raw_candidate_count,
            max_candidates=limit,
            max_total_runs=total_limit,
        )
        if total_limit is not None and execution_scale.planned_total_runs > total_limit:
            raise ValueError(
                "planned total runs "
                f"{execution_scale.planned_total_runs} exceeds max_total_runs {total_limit}"
            )

        folds = tuple(
            self._run_fold(
                window=window,
                parameters=grid,
                constraint=constraint,
                objective=resolved_objective,
                max_candidates=limit,
            )
            for window in windows
        )
        summary = _build_oos_summary(folds, resolved_objective)
        diagnostics = _build_diagnostics(folds, resolved_objective)
        return WalkForwardResult(
            folds=folds,
            objective=resolved_objective,
            mode=mode,
            train_size=train_size,
            test_size=test_size,
            step_size=resolved_step_size,
            execution_scale=execution_scale,
            oos_summary=summary,
            diagnostics=diagnostics,
        )

    def _run_fold(
        self,
        *,
        window: _FoldWindow,
        parameters: Mapping[str, Sequence[JSONScalar]],
        constraint: Constraint | None,
        objective: Objective,
        max_candidates: int | None,
    ) -> WalkForwardFold:
        train_bars = _slice_bars(self.bars, window.train_start_index, window.train_end_index)
        test_bars = _slice_bars(self.bars, window.test_start_index, window.test_end_index)
        train_result: GridSearchResult | None = None
        try:
            train_result = ParameterStudy(
                engine=self.engine,
                bars=train_bars,
                strategy=self.strategy,
            ).grid_search(
                parameters=parameters,
                constraint=constraint,
                objective=objective,
                max_candidates=max_candidates,
                fail_fast=False,
            )
        except Exception as error:
            return _failed_fold(window, train_result, "train_search", error)

        try:
            selected_row = train_result.best(objective)
        except ValueError as error:
            return _failed_fold(window, train_result, "selection", error)

        selected_config: StrategyConfig
        selected_config_mapping: Mapping[str, JSONScalar]
        try:
            selected_config = self.strategy.config_type(**dict(selected_row.candidate_parameters))
            selected_config_mapping = MappingProxyType(selected_config.to_mapping())
        except Exception as error:
            return _failed_fold(
                window,
                train_result,
                "test_strategy_construction",
                error,
                selected_row,
            )

        try:
            test_result = self.engine.run(
                bars=test_bars,
                strategy=self.strategy,
                config=selected_config,
                label=f"walk-forward-fold-{window.fold_index}-test",
            )
        except BacktestStrategyConstructionError as error:
            return _failed_fold(
                window,
                train_result,
                "test_strategy_construction",
                error.original,
                selected_row,
                selected_config_mapping,
            )
        except Exception as error:
            return _failed_fold(
                window,
                train_result,
                "test_backtest",
                error,
                selected_row,
                selected_config_mapping,
            )

        try:
            test_metrics, test_metric_states = normalize_metrics(extract_metrics(test_result))
        except Exception as error:
            return _failed_fold(
                window,
                train_result,
                "test_metric_extraction",
                error,
                selected_row,
                selected_config_mapping,
                test_result,
            )

        return _fold_from_window(
            window,
            status="success",
            train_result=train_result,
            selected_train_row=selected_row,
            selected_config=selected_config_mapping,
            selected_test_result=test_result,
            train_metrics=selected_row.metrics,
            train_metric_states=selected_row.metric_states,
            test_metrics=test_metrics,
            test_metric_states=test_metric_states,
            failure_stage=None,
            error_type=None,
            error_message=None,
        )


def _validate_max_total_runs(value: int | None) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("max_total_runs must be a positive integer or None")
    if value <= 0:
        raise ValueError("max_total_runs must be a positive integer or None")
    return value


def _validate_mode(mode: object) -> None:
    if mode != "rolling":
        raise ValueError(f"unsupported walk-forward mode {mode!r}; only 'rolling' is supported")


def _validate_windows(train_size: object, test_size: object, step_size: object) -> int:
    _validate_positive_int("train_size", train_size)
    test = _validate_positive_int("test_size", test_size)
    if step_size is None:
        return test
    return _validate_positive_int("step_size", step_size)


def _validate_positive_int(name: str, value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be a positive integer")
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _validate_chronological_bars(bars: BarSeries) -> None:
    previous: int | None = None
    for row in bars.rows:
        if previous is not None and row.timestamp <= previous:
            raise ValueError("bars timestamps must be strictly increasing")
        previous = row.timestamp


def _fold_windows(
    bars: BarSeries,
    *,
    train_size: int,
    test_size: int,
    step_size: int,
) -> tuple[_FoldWindow, ...]:
    windows: list[_FoldWindow] = []
    start = 0
    fold_index = 0
    total = len(bars.rows)
    while start + train_size + test_size <= total:
        train_start = start
        train_end = start + train_size
        test_start = train_end
        test_end = test_start + test_size
        windows.append(
            _FoldWindow(
                fold_index=fold_index,
                train_start_index=train_start,
                train_end_index=train_end,
                test_start_index=test_start,
                test_end_index=test_end,
                train_start_timestamp=bars.rows[train_start].timestamp,
                train_end_timestamp=bars.rows[train_end - 1].timestamp,
                test_start_timestamp=bars.rows[test_start].timestamp,
                test_end_timestamp=bars.rows[test_end - 1].timestamp,
            )
        )
        fold_index += 1
        start += step_size
    return tuple(windows)


def _execution_scale(
    *,
    fold_count: int,
    raw_candidate_count: int,
    max_candidates: int | None,
    max_total_runs: int | None,
) -> WalkForwardExecutionScale:
    planned_train = fold_count * raw_candidate_count
    planned_test = fold_count
    return WalkForwardExecutionScale(
        fold_count=fold_count,
        raw_candidate_count_per_fold=raw_candidate_count,
        planned_train_candidate_runs=planned_train,
        planned_selected_test_runs=planned_test,
        planned_total_runs=planned_train + planned_test,
        max_candidates=max_candidates,
        max_total_runs=max_total_runs,
    )


def _slice_bars(bars: BarSeries, start: int, end: int) -> BarSeries:
    return BarSeries(
        symbol=bars.symbol,
        timeframe=bars.timeframe,
        bar_type=bars.bar_type,
        rows=bars.rows[start:end],
    )


def _failed_fold(
    window: _FoldWindow,
    train_result: GridSearchResult | None,
    failure_stage: FoldFailureStage,
    error: BaseException,
    selected_row: GridSearchRow | None = None,
    selected_config: Mapping[str, JSONScalar] | None = None,
    selected_test_result: BacktestResult | None = None,
) -> WalkForwardFold:
    return _fold_from_window(
        window,
        status="failed",
        train_result=train_result,
        selected_train_row=selected_row,
        selected_config=selected_config,
        selected_test_result=selected_test_result,
        train_metrics=selected_row.metrics if selected_row is not None else {},
        train_metric_states=selected_row.metric_states if selected_row is not None else {},
        test_metrics={},
        test_metric_states={},
        failure_stage=failure_stage,
        error_type=type(error).__name__,
        error_message=str(error),
    )


def _fold_from_window(
    window: _FoldWindow,
    *,
    status: FoldStatus,
    train_result: GridSearchResult | None,
    selected_train_row: GridSearchRow | None,
    selected_config: Mapping[str, JSONScalar] | None,
    selected_test_result: BacktestResult | None,
    train_metrics: Mapping[str, MetricValue],
    train_metric_states: Mapping[str, MetricState],
    test_metrics: Mapping[str, MetricValue],
    test_metric_states: Mapping[str, MetricState],
    failure_stage: FoldFailureStage | None,
    error_type: str | None,
    error_message: str | None,
) -> WalkForwardFold:
    return WalkForwardFold(
        fold_index=window.fold_index,
        status=status,
        train_start_index=window.train_start_index,
        train_end_index=window.train_end_index,
        test_start_index=window.test_start_index,
        test_end_index=window.test_end_index,
        train_start_timestamp=window.train_start_timestamp,
        train_end_timestamp=window.train_end_timestamp,
        test_start_timestamp=window.test_start_timestamp,
        test_end_timestamp=window.test_end_timestamp,
        train_result=train_result,
        selected_train_row=selected_train_row,
        selected_config=selected_config,
        selected_test_result=selected_test_result,
        train_metrics=train_metrics,
        train_metric_states=train_metric_states,
        test_metrics=test_metrics,
        test_metric_states=test_metric_states,
        failure_stage=failure_stage,
        error_type=error_type,
        error_message=error_message,
    )


def _build_oos_summary(
    folds: tuple[WalkForwardFold, ...],
    objective: Objective,
) -> WalkForwardOosSummary:
    metric_path, direction = objective
    successful = tuple(fold for fold in folds if fold.status == "success")
    metric_state_counts: dict[str, Counter[str]] = {key: Counter() for key in METRIC_KEYS}
    metric_values: dict[str, list[float]] = {key: [] for key in METRIC_KEYS}
    positive_return_count = 0
    finite_return_count = 0
    for fold in successful:
        for key in METRIC_KEYS:
            state = fold.test_metric_states.get(key, "undefined")
            metric_state_counts[key][state] += 1
            value = fold.test_metrics.get(key)
            if (
                state == "defined"
                and isinstance(value, int | float)
                and not isinstance(value, bool)
            ):
                metric_values[key].append(float(value))
        return_value = fold.test_metrics.get("returns.total_return")
        return_state = fold.test_metric_states.get("returns.total_return")
        if (
            return_state == "defined"
            and isinstance(return_value, int | float)
            and not isinstance(return_value, bool)
            and math.isfinite(float(return_value))
        ):
            finite_return_count += 1
            if return_value > 0:
                positive_return_count += 1

    fold_count = len(folds)
    failed_count = fold_count - len(successful)
    metric_summaries = {
        key: {
            "count": len(values),
            "mean": mean(values),
            "median": median(values),
            "min": min(values),
            "max": max(values),
        }
        for key, values in metric_values.items()
        if values
    }
    objective_values = metric_values[metric_path]
    return WalkForwardOosSummary(
        fold_count=fold_count,
        successful_fold_count=len(successful),
        failed_fold_count=failed_count,
        failure_rate=(failed_count / fold_count) if fold_count else 0.0,
        objective_metric_path=metric_path,
        objective_direction=direction,
        objective_metric_state_counts=dict(metric_state_counts[metric_path]),
        metric_state_counts={key: dict(value) for key, value in metric_state_counts.items()},
        metric_summaries=metric_summaries,
        objective_mean=mean(objective_values) if objective_values else None,
        objective_median=median(objective_values) if objective_values else None,
        objective_min=min(objective_values) if objective_values else None,
        objective_max=max(objective_values) if objective_values else None,
        positive_fold_ratio=(
            positive_return_count / finite_return_count if finite_return_count else None
        ),
    )


def _build_diagnostics(
    folds: tuple[WalkForwardFold, ...],
    objective: Objective,
) -> tuple[WalkForwardDiagnostic, ...]:
    metric_path, _direction = objective
    diagnostics: list[WalkForwardDiagnostic] = []
    failed = tuple(fold.fold_index for fold in folds if fold.status == "failed")
    no_selected = tuple(
        fold.fold_index
        for fold in folds
        if fold.status == "failed" and fold.failure_stage == "selection"
    )
    undefined_oos = tuple(
        fold.fold_index
        for fold in folds
        if fold.status == "success" and fold.test_metric_states.get(metric_path) == "undefined"
    )
    no_trades = tuple(
        fold.fold_index
        for fold in folds
        if fold.status == "success"
        and fold.test_metric_states.get("trades.closed_count") == "defined"
        and fold.test_metrics.get("trades.closed_count") == 0
    )

    if failed:
        diagnostics.append(
            WalkForwardDiagnostic(
                severity="warning",
                code="fold_execution_failed",
                message="one or more walk-forward folds failed",
                fold_indexes=failed,
            )
        )
    if no_selected:
        diagnostics.append(
            WalkForwardDiagnostic(
                severity="warning",
                code="no_selected_config",
                message="one or more folds did not select a config",
                fold_indexes=no_selected,
            )
        )
    if undefined_oos:
        diagnostics.append(
            WalkForwardDiagnostic(
                severity="warning",
                code="undefined_oos_objective",
                message="one or more successful OOS folds have an undefined objective metric",
                fold_indexes=undefined_oos,
            )
        )
    if no_trades:
        diagnostics.append(
            WalkForwardDiagnostic(
                severity="info",
                code="no_closed_trades",
                message="one or more successful OOS folds have no closed trades",
                fold_indexes=no_trades,
            )
        )
    if not any(fold.status == "success" for fold in folds):
        diagnostics.append(
            WalkForwardDiagnostic(
                severity="warning",
                code="zero_successful_oos_folds",
                message="no folds produced a successful selected OOS test",
            )
        )
    return tuple(diagnostics)


def _fold_to_record(
    fold: WalkForwardFold,
    *,
    metric_path: str,
    direction: str,
) -> dict[str, object]:
    record: dict[str, object] = {
        "fold_index": fold.fold_index,
        "train_start_index": fold.train_start_index,
        "train_end_index": fold.train_end_index,
        "test_start_index": fold.test_start_index,
        "test_end_index": fold.test_end_index,
        "train_start_timestamp": fold.train_start_timestamp,
        "train_end_timestamp": fold.train_end_timestamp,
        "test_start_timestamp": fold.test_start_timestamp,
        "test_end_timestamp": fold.test_end_timestamp,
        "objective_metric_path": metric_path,
        "objective_direction": direction,
        "status": fold.status,
        "train_status": "success" if fold.train_result is not None else "failed",
        "test_status": "success" if fold.status == "success" else "failed",
        "selected_config": dict(fold.selected_config) if fold.selected_config is not None else None,
        "failure_stage": fold.failure_stage,
        "error_type": fold.error_type,
        "error_message": fold.error_message,
    }
    for key in METRIC_KEYS:
        train_state = fold.train_metric_states.get(key, "undefined")
        train_value = fold.train_metrics.get(key)
        test_state = fold.test_metric_states.get(key, "undefined")
        test_value = fold.test_metrics.get(key)
        record[f"train.{key}"] = train_value if train_state == "defined" else None
        record[f"train.{key}_state"] = train_state
        record[f"test.{key}"] = test_value if test_state == "defined" else None
        record[f"test.{key}_state"] = test_state
    return record


__all__ = [
    "WalkForwardDiagnostic",
    "WalkForwardExecutionScale",
    "WalkForwardFold",
    "WalkForwardOosSummary",
    "WalkForwardResult",
    "WalkForwardStudy",
]
