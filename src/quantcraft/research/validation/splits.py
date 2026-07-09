from __future__ import annotations

from dataclasses import dataclass

from quantcraft.data import BarSeries


@dataclass(frozen=True, slots=True)
class SplitWindow:
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
class RollingSplitPolicy:
    train_size: int
    test_size: int
    step_size: int | None = None

    def __post_init__(self) -> None:
        _validate_positive_int("train_size", self.train_size)
        _validate_positive_int("test_size", self.test_size)
        if self.step_size is not None:
            _validate_positive_int("step_size", self.step_size)

    def split(self, bars: BarSeries) -> tuple[SplitWindow, ...]:
        if not isinstance(bars, BarSeries):
            raise TypeError("bars must be a BarSeries instance")
        _validate_chronological_bars(bars)
        step = self.step_size if self.step_size is not None else self.test_size
        windows: list[SplitWindow] = []
        start = 0
        fold_index = 0
        total = len(bars.rows)
        while start + self.train_size + self.test_size <= total:
            train_start = start
            train_end = start + self.train_size
            test_start = train_end
            test_end = test_start + self.test_size
            windows.append(
                SplitWindow(
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
            start += step
        return tuple(windows)


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
