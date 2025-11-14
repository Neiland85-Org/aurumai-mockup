"""
Domain Entity: Prediction
Represents ML prediction results for predictive maintenance
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict


@dataclass
class Prediction:
    """
    Prediction domain entity.
    Contains ML prediction results for a machine at a specific point in time.
    """

    machine_id: str
    timestamp: datetime
    risk_score: float
    failure_probability: float
    maintenance_hours: int
    failure_type: Optional[str] = None
    confidence: Optional[float] = None
    model_version: Optional[str] = None
    features_used: Optional[Dict[str, float]] = None

    def __post_init__(self):
        """Validate prediction data"""
        if not self.machine_id or not self.machine_id.strip():
            raise ValueError("machine_id cannot be empty")

        if not (0 <= self.risk_score <= 1):
            raise ValueError("risk_score must be between 0 and 1")

        if not (0 <= self.failure_probability <= 1):
            raise ValueError("failure_probability must be between 0 and 1")

        if self.maintenance_hours < 0:
            raise ValueError("maintenance_hours cannot be negative")

        if self.confidence is not None and not (0 <= self.confidence <= 1):
            raise ValueError("confidence must be between 0 and 1")

    def is_high_risk(self, threshold: float = 0.7) -> bool:
        """Check if prediction indicates high risk"""
        return self.risk_score >= threshold

    def is_critical(self, threshold: float = 0.9) -> bool:
        """Check if prediction indicates critical status"""
        return self.risk_score >= threshold

    def needs_immediate_action(self, hours_threshold: int = 24) -> bool:
        """Check if maintenance is needed within threshold hours"""
        return self.maintenance_hours <= hours_threshold
