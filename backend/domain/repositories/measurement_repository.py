"""
Measurement Repository Interface
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional, Any
from uuid import UUID
from domain.value_objects import TimeSeriesPoint, Measurement


class IMeasurementRepository(ABC):
    """Repository interface for time series measurements"""

    @abstractmethod
    async def save_measurement(self, measurement: Measurement) -> bool:
        """Save a single measurement"""
        pass

    @abstractmethod
    async def save_batch(self, measurements: List[Measurement]) -> int:
        """Save multiple measurements, returns count saved"""
        pass

    @abstractmethod
    async def save_timeseries_point(self, point: TimeSeriesPoint) -> bool:
        """Save a complete time series point (multiple metrics)"""
        pass

    @abstractmethod
    async def get_latest(
        self, machine_id: UUID, metric_names: List[str], limit: int = 100
    ) -> List[Dict]:
        """Get latest measurements for specified metrics"""
        pass

    @abstractmethod
    async def get_range(
        self,
        machine_id: UUID,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
    ) -> List[Dict]:
        """Get measurements within a time range"""
        pass

    @abstractmethod
    async def get_aggregated(
        self,
        machine_id: UUID,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        interval_seconds: int,
    ) -> List[Dict]:
        """Get aggregated measurements (avg, min, max) per interval"""
        pass

    # Aliases for compatibility with use cases
    async def get_latest_raw_measurement(self, machine_id: str) -> Optional[Dict]:
        """Get latest raw measurement for a machine"""
        # This should be implemented by concrete repositories
        return None

    async def save_raw_measurement(self, machine_id: str, data: Dict) -> bool:
        """Save raw measurement data"""
        # This should be implemented by concrete repositories
        return False

    async def get_latest_features(self, machine_id: str) -> Optional[Any]:
        """Get latest feature vector for a machine"""
        # This should be implemented by concrete repositories
        return None

    async def save_feature_vector(self, machine_id: str, features: Dict) -> bool:
        """Save feature vector"""
        # This should be implemented by concrete repositories
        return False
