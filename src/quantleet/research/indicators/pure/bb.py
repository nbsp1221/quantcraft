from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import talib

_DEFAULT_LENGTH: Final[int] = 20
_DEFAULT_STDDEV: Final[float] = 2.0


@dataclass(frozen=True, slots=True)
class PureBollingerBandsResult[SeriesT]:
    upper: SeriesT
    middle: SeriesT
    lower: SeriesT


def bb(
    values: np.ndarray,
    length: int = _DEFAULT_LENGTH,
    stddev: int | float = _DEFAULT_STDDEV,
) -> PureBollingerBandsResult[np.ndarray]:
    _validate_length(length)
    upper, middle, lower = talib.BBANDS(
        np.asarray(values, dtype=float),
        timeperiod=length,
        nbdevup=float(stddev),
        nbdevdn=float(stddev),
    )
    return PureBollingerBandsResult(
        upper=upper,
        middle=middle,
        lower=lower,
    )


def _validate_length(length: int) -> None:
    if length <= 0:
        raise ValueError("length must be positive")
