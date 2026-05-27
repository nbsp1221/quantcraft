from __future__ import annotations

import math
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from itertools import product
from types import MappingProxyType
from typing import Literal, Protocol, cast

from quantleet.backtest import BacktestResult, BacktestStrategyConstructionError
from quantleet.data import BarSeries
from quantleet.research._study_metrics import (
    METRIC_KEYS,
    UNDEFINED_METRIC_STATES,
    Constraint,
    JSONScalar,
    MetricState,
    MetricValue,
    Objective,
    extract_metrics,
    normalize_metrics,
    validate_objective,
)
from quantleet.strategy import Strategy, StrategyConfig, StrategyConfigValidationError

type FailureStage = Literal[
    "constraint",
    "strategy_construction",
    "backtest",
    "metric_extraction",
]
type RejectionStage = Literal["strategy_config", "constraint"]
type RowStatus = Literal["success", "rejected", "failed"]


@dataclass(frozen=True, slots=True)
class _RunnableCandidate:
    run_index: int
    candidate_parameters: Mapping[str, JSONScalar]
    config: StrategyConfig
    strategy_config: Mapping[str, JSONScalar]


class _GridSearchEngine(Protocol):
    def run(
        self,
        *,
        bars: BarSeries,
        strategy: type[Strategy[StrategyConfig]],
        config: StrategyConfig,
        label: str,
    ) -> BacktestResult: ...


@dataclass(frozen=True, slots=True)
class GridSearchRow:
    run_index: int
    status: RowStatus
    candidate_parameters: Mapping[str, JSONScalar]
    strategy_config: Mapping[str, JSONScalar]
    backtest: BacktestResult | None
    metrics: Mapping[str, MetricValue]
    metric_states: Mapping[str, MetricState]
    rejection_stage: RejectionStage | None
    failure_stage: FailureStage | None
    error_type: str | None
    error_message: str | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "candidate_parameters",
            MappingProxyType(dict(self.candidate_parameters)),
        )
        object.__setattr__(self, "strategy_config", MappingProxyType(dict(self.strategy_config)))
        object.__setattr__(self, "metrics", MappingProxyType(dict(self.metrics)))
        object.__setattr__(self, "metric_states", MappingProxyType(dict(self.metric_states)))

    @classmethod
    def success(
        cls,
        *,
        run_index: int,
        candidate_parameters: Mapping[str, JSONScalar],
        strategy_config: Mapping[str, JSONScalar],
        backtest: BacktestResult,
        metrics: Mapping[str, MetricValue],
    ) -> GridSearchRow:
        normalized_metrics, metric_states = normalize_metrics(metrics)
        return cls(
            run_index=run_index,
            status="success",
            candidate_parameters=candidate_parameters,
            strategy_config=strategy_config,
            backtest=backtest,
            metrics=normalized_metrics,
            metric_states=metric_states,
            rejection_stage=None,
            failure_stage=None,
            error_type=None,
            error_message=None,
        )

    @classmethod
    def rejected(
        cls,
        *,
        run_index: int,
        candidate_parameters: Mapping[str, JSONScalar],
        strategy_config: Mapping[str, JSONScalar],
        rejection_stage: RejectionStage,
        error: BaseException | None = None,
    ) -> GridSearchRow:
        return cls(
            run_index=run_index,
            status="rejected",
            candidate_parameters=candidate_parameters,
            strategy_config=strategy_config,
            backtest=None,
            metrics={},
            metric_states=UNDEFINED_METRIC_STATES,
            rejection_stage=rejection_stage,
            failure_stage=None,
            error_type=type(error).__name__ if error is not None else None,
            error_message=str(error) if error is not None else None,
        )

    @classmethod
    def failed(
        cls,
        *,
        run_index: int,
        candidate_parameters: Mapping[str, JSONScalar],
        strategy_config: Mapping[str, JSONScalar],
        failure_stage: FailureStage,
        error: BaseException,
    ) -> GridSearchRow:
        return cls(
            run_index=run_index,
            status="failed",
            candidate_parameters=candidate_parameters,
            strategy_config=strategy_config,
            backtest=None,
            metrics={},
            metric_states=UNDEFINED_METRIC_STATES,
            rejection_stage=None,
            failure_stage=failure_stage,
            error_type=type(error).__name__,
            error_message=str(error),
        )


@dataclass(frozen=True, slots=True)
class GridSearchResult:
    rows: tuple[GridSearchRow, ...]
    objective: Objective | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "rows", tuple(self.rows))
        if self.objective is not None:
            object.__setattr__(self, "objective", validate_objective(self.objective))

    @property
    def candidate_count(self) -> int:
        return len(self.rows)

    @property
    def successful_count(self) -> int:
        return len(self.successful())

    @property
    def rejected_count(self) -> int:
        return len(self.rejected())

    @property
    def failed_count(self) -> int:
        return len(self.failed())

    @property
    def eligible_count(self) -> int:
        if self.objective is None:
            return 0
        return len(self._eligible_rows(self.objective))

    def successful(self) -> tuple[GridSearchRow, ...]:
        return tuple(row for row in self.rows if row.status == "success")

    def rejected(self) -> tuple[GridSearchRow, ...]:
        return tuple(row for row in self.rows if row.status == "rejected")

    def failed(self) -> tuple[GridSearchRow, ...]:
        return tuple(row for row in self.rows if row.status == "failed")

    def best(self, objective: Objective | None = None) -> GridSearchRow:
        top_row = self.top(1, objective=objective)
        if not top_row:
            raise ValueError("no eligible rows for objective")
        return top_row[0]

    def top(self, n: int, objective: Objective | None = None) -> tuple[GridSearchRow, ...]:
        if not isinstance(n, int) or isinstance(n, bool):
            raise TypeError("n must be a positive integer")
        if n <= 0:
            raise ValueError("n must be a positive integer")

        resolved_objective = validate_objective(self.objective if objective is None else objective)
        metric_path, direction = resolved_objective
        reverse = direction == "max"
        eligible_rows = self._eligible_rows(resolved_objective)
        sorted_rows = sorted(
            eligible_rows,
            key=lambda row: (
                row.metrics[metric_path],
                -row.run_index if reverse else row.run_index,
            ),
            reverse=reverse,
        )
        return tuple(sorted_rows[:n])

    def to_records(self) -> list[dict[str, object]]:
        return [_row_to_record(row) for row in self.rows]

    def _eligible_rows(self, objective: Objective) -> tuple[GridSearchRow, ...]:
        metric_path, _direction = objective
        rows: list[GridSearchRow] = []
        for row in self.successful():
            value = row.metrics.get(metric_path)
            state = row.metric_states.get(metric_path)
            if state in {"defined", "positive_infinity", "negative_infinity"} and value is not None:
                rows.append(row)
        return tuple(rows)


class ParameterStudy:
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
        if not isinstance(strategy, type) or not issubclass(strategy, Strategy):
            raise TypeError("strategy must be a Strategy class")
        self.engine = engine
        self.bars = bars
        self.strategy = strategy

    def grid_search(
        self,
        *,
        parameters: Mapping[str, Sequence[JSONScalar]],
        constraint: Constraint | None = None,
        objective: Objective | None = None,
        max_candidates: int | None = 1000,
        fail_fast: bool = False,
    ) -> GridSearchResult:
        grid = _validate_parameter_grid(parameters)
        limit = _validate_max_candidates(max_candidates)
        resolved_objective = validate_objective(objective) if objective is not None else None
        candidate_count = _candidate_count(grid)
        if limit is not None and candidate_count > limit:
            raise ValueError(
                f"raw candidate count {candidate_count} exceeds max_candidates {limit}"
            )
        _validate_parameter_keys(grid, self.strategy.config_type)

        prepared_candidates = _prepare_grid_candidates(grid, self.strategy.config_type)

        rows: list[GridSearchRow] = []
        for prepared in prepared_candidates:
            if isinstance(prepared, GridSearchRow):
                rows.append(prepared)
                continue

            if not _evaluate_constraint(prepared, constraint, rows, fail_fast):
                continue

            backtest = _run_grid_candidate(
                prepared=prepared,
                engine=cast(_GridSearchEngine, self.engine),
                bars=self.bars,
                strategy=self.strategy,
                rows=rows,
                fail_fast=fail_fast,
            )
            if backtest is None:
                continue

            if not _extract_candidate_metrics(prepared, backtest, rows, fail_fast):
                continue

        return GridSearchResult(rows=tuple(rows), objective=resolved_objective)


def _prepare_grid_candidates(
    grid: Mapping[str, Sequence[JSONScalar]],
    config_type: type[StrategyConfig],
) -> list[_RunnableCandidate | GridSearchRow]:
    return [
        _prepare_candidate(
            run_index=run_index,
            candidate=candidate,
            config_type=config_type,
        )
        for run_index, candidate in _iter_candidates(grid)
    ]


def _evaluate_constraint(
    prepared: _RunnableCandidate,
    constraint: Constraint | None,
    rows: list[GridSearchRow],
    fail_fast: bool,
) -> bool:
    if constraint is None:
        return True

    try:
        outcome = constraint(prepared.strategy_config)
        if not isinstance(outcome, bool):
            raise TypeError("constraint must return bool")
    except Exception as error:
        _raise_or_record_prepared(
            rows=rows,
            fail_fast=fail_fast,
            error=error,
            stage="constraint",
            prepared=prepared,
        )
        return False

    if outcome:
        return True

    rows.append(
        GridSearchRow.rejected(
            run_index=prepared.run_index,
            candidate_parameters=prepared.candidate_parameters,
            strategy_config=prepared.strategy_config,
            rejection_stage="constraint",
        )
    )
    return False


def _run_grid_candidate(
    *,
    prepared: _RunnableCandidate,
    engine: _GridSearchEngine,
    bars: BarSeries,
    strategy: type[Strategy[StrategyConfig]],
    rows: list[GridSearchRow],
    fail_fast: bool,
) -> BacktestResult | None:
    try:
        return engine.run(
            bars=bars,
            strategy=strategy,
            config=prepared.config,
            label=f"grid-search-{prepared.run_index}",
        )
    except BacktestStrategyConstructionError as error:
        _raise_or_record_prepared(
            rows=rows,
            fail_fast=fail_fast,
            error=error.original,
            stage="strategy_construction",
            prepared=prepared,
        )
    except Exception as error:
        _raise_or_record_prepared(
            rows=rows,
            fail_fast=fail_fast,
            error=error,
            stage="backtest",
            prepared=prepared,
        )
    return None


def _extract_candidate_metrics(
    prepared: _RunnableCandidate,
    backtest: BacktestResult,
    rows: list[GridSearchRow],
    fail_fast: bool,
) -> bool:
    try:
        metrics = extract_metrics(backtest)
    except Exception as error:
        _raise_or_record_prepared(
            rows=rows,
            fail_fast=fail_fast,
            error=error,
            stage="metric_extraction",
            prepared=prepared,
        )
        return False

    rows.append(
        GridSearchRow.success(
            run_index=prepared.run_index,
            candidate_parameters=prepared.candidate_parameters,
            strategy_config=prepared.strategy_config,
            backtest=backtest,
            metrics=metrics,
        )
    )
    return True


def _validate_parameter_grid(
    parameters: object,
) -> dict[str, tuple[JSONScalar, ...]]:
    if not isinstance(parameters, Mapping):
        raise TypeError("parameters must be a mapping")

    grid: dict[str, tuple[JSONScalar, ...]] = {}
    for name, values in parameters.items():
        if not isinstance(name, str):
            raise TypeError("parameter name must be a string")
        if not name:
            raise ValueError("parameter name must be non-empty")
        if not isinstance(values, Sequence) or isinstance(values, str | bytes):
            raise TypeError(f"parameter {name!r} values must be an ordered sequence")
        if not values:
            raise ValueError(f"parameter {name!r} must include at least one value")

        normalized_values = tuple(_validate_json_scalar(name, value) for value in values)
        seen: set[tuple[type[JSONScalar], JSONScalar]] = set()
        for value in normalized_values:
            marker = (type(value), value)
            if marker in seen:
                raise ValueError(f"parameter {name!r} contains duplicate value {value!r}")
            seen.add(marker)
        grid[name] = normalized_values

    return grid


def _validate_parameter_keys(
    grid: Mapping[str, Sequence[JSONScalar]],
    config_type: type[StrategyConfig],
) -> None:
    config_type.validate_override_names(tuple(grid))


def _candidate_strategy_config_snapshot(
    config_type: type[StrategyConfig],
    candidate: Mapping[str, JSONScalar],
) -> Mapping[str, JSONScalar]:
    return MappingProxyType(config_type.diagnostic_mapping_from_overrides(candidate))


def _prepare_candidate(
    *,
    run_index: int,
    candidate: Mapping[str, JSONScalar],
    config_type: type[StrategyConfig],
) -> _RunnableCandidate | GridSearchRow:
    candidate_parameters: Mapping[str, JSONScalar] = MappingProxyType(dict(candidate))
    try:
        config = config_type(**candidate)
    except StrategyConfigValidationError as error:
        rejected_strategy_config = _candidate_strategy_config_snapshot(
            config_type,
            candidate,
        )
        return GridSearchRow.rejected(
            run_index=run_index,
            candidate_parameters=candidate_parameters,
            strategy_config=rejected_strategy_config,
            rejection_stage="strategy_config",
            error=error,
        )

    return _RunnableCandidate(
        run_index=run_index,
        candidate_parameters=candidate_parameters,
        config=config,
        strategy_config=MappingProxyType(config.to_mapping()),
    )


def _validate_json_scalar(name: str, value: object) -> JSONScalar:
    if value is None:
        return None
    if type(value) is str:
        return value
    if type(value) is bool:
        return value
    if type(value) is int:
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"parameter {name!r} value {value!r} of type float must be finite")
        return value
    raise TypeError(
        f"parameter {name!r} value {value!r} has unsupported type {type(value).__name__}"
    )


def _candidate_count(grid: Mapping[str, Sequence[JSONScalar]]) -> int:
    total = 1
    for values in grid.values():
        total *= len(values)
    return total


def _iter_candidates(
    grid: Mapping[str, Sequence[JSONScalar]],
) -> Iterator[tuple[int, dict[str, JSONScalar]]]:
    names = tuple(grid)
    for run_index, values in enumerate(product(*(grid[name] for name in names))):
        yield run_index, dict(zip(names, values, strict=True))


def _validate_max_candidates(value: int | None) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("max_candidates must be a positive integer or None")
    if value <= 0:
        raise ValueError("max_candidates must be a positive integer or None")
    return value


def _row_to_record(row: GridSearchRow) -> dict[str, object]:
    report = row.backtest.report if row.backtest is not None else None
    record: dict[str, object] = {
        "run_index": row.run_index,
        "status": row.status,
        "candidate_parameters": dict(row.candidate_parameters),
        "strategy_config": dict(row.strategy_config),
        "run.label": report.run.run_label if report is not None else None,
        "strategy.class_name": report.run.strategy_class_name if report is not None else None,
        "strategy.display_name": report.run.strategy_display_name if report is not None else None,
        "run.symbol": report.run.symbol if report is not None else None,
        "run.timeframe": report.run.timeframe if report is not None else None,
        "run.initial_cash": report.run.initial_cash if report is not None else None,
        "execution.model_name": (
            report.execution.execution_model_name if report is not None else None
        ),
        "rejection_stage": row.rejection_stage,
        "failure_stage": row.failure_stage,
        "error_type": row.error_type,
        "error_message": row.error_message,
    }
    for key in METRIC_KEYS:
        value = row.metrics.get(key)
        state = row.metric_states.get(key, "undefined")
        record[key] = value if state == "defined" else None
        record[f"{key}_state"] = state
    return record


def _raise_or_record(
    *,
    rows: list[GridSearchRow],
    fail_fast: bool,
    error: BaseException,
    stage: FailureStage,
    run_index: int,
    candidate_parameters: Mapping[str, JSONScalar],
    strategy_config: Mapping[str, JSONScalar],
) -> None:
    if fail_fast:
        error.add_note(f"stage={stage}")
        error.add_note(f"candidate_parameters={dict(candidate_parameters)!r}")
        error.add_note(f"strategy_config={dict(strategy_config)!r}")
        raise error
    rows.append(
        GridSearchRow.failed(
            run_index=run_index,
            candidate_parameters=candidate_parameters,
            strategy_config=strategy_config,
            failure_stage=stage,
            error=error,
        )
    )


def _raise_or_record_prepared(
    *,
    rows: list[GridSearchRow],
    fail_fast: bool,
    error: BaseException,
    stage: FailureStage,
    prepared: _RunnableCandidate,
) -> None:
    _raise_or_record(
        rows=rows,
        fail_fast=fail_fast,
        error=error,
        stage=stage,
        run_index=prepared.run_index,
        candidate_parameters=prepared.candidate_parameters,
        strategy_config=prepared.strategy_config,
    )


__all__ = ["GridSearchResult", "GridSearchRow", "ParameterStudy"]
