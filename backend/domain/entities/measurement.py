"""
Domain Entities: Measurement
Represents raw telemetry and engineered features
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass
class RawMeasurement:
    """
    Raw measurement from IoT sensors.
    Contains unprocessed telemetry data.
    """

    machine_id: str
    timestamp: datetime
    metrics: Dict[str, float]

    def __post_init__(self) -> None:
        """Validate measurement data"""
        if not self.machine_id or not self.machine_id.strip():
            raise ValueError("machine_id cannot be empty")
        if not isinstance(self.metrics, dict):
            raise TypeError("metrics must be a dictionary")
        if not self.metrics:
            raise ValueError("metrics cannot be empty")


@dataclass
class FeatureVector:
    """
    Engineered features from edge processing.
    Contains aggregated/transformed metrics ready for ML.
    """

    machine_id: str
    timestamp: datetime
    features: Dict[str, float]

    def __post_init__(self) -> None:
        """Validate feature vector data"""
        if not self.machine_id or not self.machine_id.strip():
            raise ValueError("machine_id cannot be empty")
        if not isinstance(self.features, dict):
            raise TypeError("features must be a dictionary")
        if not self.features:
            raise ValueError("features cannot be empty")
