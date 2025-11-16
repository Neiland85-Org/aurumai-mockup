"""
Prediction Repository Interface
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence

from domain.entities.prediction import Prediction


class IPredictionRepository(ABC):
    """Repository interface for Prediction entities"""

    @abstractmethod
    async def save(self, prediction: Prediction) -> Prediction:
        """Persist a prediction and return the stored entity"""
        raise NotImplementedError

    @abstractmethod
    async def get_latest(self, machine_id: str) -> Prediction | None:
        """Fetch latest prediction for a machine, if any"""
        raise NotImplementedError

    @abstractmethod
    async def get_history(
        self, machine_id: str, limit: int = 50
    ) -> Sequence[Prediction]:
        """Fetch last N predictions for a machine"""
        raise NotImplementedError

    @abstractmethod
    async def get_range(
        self,
        machine_id: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> Sequence[Prediction]:
        """Fetch predictions within a time range"""
        raise NotImplementedError

    @abstractmethod
    async def get_high_risk_predictions(
        self, risk_threshold: float = 0.7, limit: int = 100
    ) -> Sequence[Prediction]:
        """Fetch predictions above a risk threshold"""
        raise NotImplementedError
