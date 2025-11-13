"""
Measurement Value Objects - Telemetry data points
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from uuid import UUID


@dataclass(frozen=True)
class Measurement:
    """
    Single measurement value object

    Immutable representation of a single sensor reading.
    """
    machine_id: UUID
    sensor_id: UUID
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    quality: float = 1.0  # Quality indicator 0.0 to 1.0

    def is_valid(self) -> bool:
        """Check if measurement is valid"""
        return 0.0 <= self.quality <= 1.0 and self.value is not None


@dataclass(frozen=True)
class TimeSeriesPoint:
    """
    Time series data point

    Represents multiple metrics at a single timestamp.
    Used for efficient batch operations.
    """
    tenant_id: UUID
    site_id: UUID
    machine_id: UUID
    timestamp: datetime
    metrics: Dict[str, float]  # metric_name -> value

    def get_metric(self, name: str) -> float:
        """Get metric value by name"""
        return self.metrics.get(name, 0.0)

    def has_metric(self, name: str) -> bool:
        """Check if metric exists"""
        return name in self.metrics
