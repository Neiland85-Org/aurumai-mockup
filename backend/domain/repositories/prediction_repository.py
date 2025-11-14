"""
Prediction Repository Interface
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from domain.entities.prediction import Prediction


class IPredictionRepository(ABC):
    """Repository interface for Prediction entities"""

    @abstractmethod
    async def save(self, prediction: Prediction) -> Prediction:
        """Persist a prediction and return the stored entity"""
        raise NotImplementedError

    @abstractmethod
    async def get_latest(self, machine_id: str) -> Optional[Prediction]:
        """Fetch latest prediction for a machine, if any"""
        raise NotImplementedError

    @abstractmethod
    async def get_history(self, machine_id: str, limit: int = 50) -> List[Prediction]:
        """Fetch last N predictions for a machine"""
        raise NotImplementedError

    @abstractmethod
    async def get_range(
        self,
        machine_id: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[Prediction]:
        """Fetch predictions within a time range"""
        raise NotImplementedError

    @abstractmethod
    async def get_high_risk_predictions(self, risk_threshold: float = 0.7, limit: int = 100) -> List[Prediction]:
        """Fetch predictions above a risk threshold"""
        raise NotImplementedError
