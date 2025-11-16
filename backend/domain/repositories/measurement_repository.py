"""
Measurement Repository Interface
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Mapping, Sequence
from uuid import UUID

from domain.entities.measurement import FeatureVector, RawMeasurement
from domain.value_objects import Measurement, TimeSeriesPoint

MetricRecord = Mapping[str, float]
AggregationRecord = Mapping[str, float]


class IMeasurementRepository(ABC):
    """Repository interface for time series measurements"""

    @abstractmethod
    async def save_measurement(self, measurement: Measurement) -> bool:
        """Save a single measurement"""
        pass

    @abstractmethod
    async def save_batch(self, measurements: Sequence[Measurement]) -> int:
        """Save multiple measurements, returns count saved"""
        pass

    @abstractmethod
    async def save_timeseries_point(self, point: TimeSeriesPoint) -> bool:
        """Save a complete time series point (multiple metrics)"""
        pass

    @abstractmethod
    async def get_latest(
        self, machine_id: UUID, metric_names: Sequence[str], limit: int = 100
    ) -> Sequence[MetricRecord]:
        """Get latest measurements for specified metrics"""
        pass

    @abstractmethod
    async def get_range(
        self,
        machine_id: UUID,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
    ) -> Sequence[MetricRecord]:
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
    ) -> Sequence[AggregationRecord]:
        """Get aggregated measurements (avg, min, max) per interval"""
        pass

    # Aliases for compatibility with use cases
    async def get_latest_raw_measurement(self, machine_id: str) -> RawMeasurement | None:
        """Get latest raw measurement for a machine"""
        # This should be implemented by concrete repositories
        return None

    async def save_raw_measurement(self, measurement: RawMeasurement) -> RawMeasurement:
        """Save raw measurement data"""
        # This should be implemented by concrete repositories
        return measurement

    async def get_latest_features(self, machine_id: str) -> FeatureVector | None:
        """Get latest feature vector for a machine"""
        # This should be implemented by concrete repositories
        return None

    async def save_feature_vector(self, features: FeatureVector) -> FeatureVector:
        """Save feature vector"""
        # This should be implemented by concrete repositories
        return features
