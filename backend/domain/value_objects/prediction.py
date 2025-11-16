"""
Prediction Value Object - ML model predictions
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID


@dataclass(frozen=True)
class Prediction:
    """
    Prediction value object

    Represents the output of an ML model prediction.
    Immutable after creation.
    """

    machine_id: UUID
    timestamp: datetime
    model_name: str
    model_version: str
    prediction_type: str  # failure, anomaly, emissions, energy
    risk_score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    predicted_value: Optional[float] = None
    predicted_class: Optional[str] = None
    time_to_event_hours: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def is_high_risk(self, threshold: float = 0.7) -> bool:
        """Check if prediction indicates high risk"""
        return self.risk_score >= threshold

    def is_confident(self, threshold: float = 0.8) -> bool:
        """Check if prediction is confident"""
        return self.confidence >= threshold
