from __future__ import annotations

from abc import ABC, abstractmethod

from quantcraft.data.domain.bars import BarSeries


class HistoricalDataSource(ABC):
    @abstractmethod
    def load(self) -> BarSeries:
        raise NotImplementedError
