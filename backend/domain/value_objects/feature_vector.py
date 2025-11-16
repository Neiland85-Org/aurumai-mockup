"""
FeatureVector Value Object - Engineered features for ML
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
from uuid import UUID


@dataclass(frozen=True)
class FeatureVector:
    """
    Feature vector value object

    Represents engineered features ready for ML model inference.
    Immutable after creation.
    """

    machine_id: UUID
    timestamp: datetime
    window_size_seconds: int
    features: Dict[str, float]  # feature_name -> value
    feature_names: List[str] | None = None

    def __post_init__(self) -> None:
        """Initialize feature names list"""
        if self.feature_names is None:
            object.__setattr__(self, "feature_names", sorted(self.features.keys()))

    def get_feature(self, name: str) -> float:
        """Get feature value by name"""
        return self.features.get(name, 0.0)

    def to_array(self) -> List[float]:
        """Convert to ordered array for ML model"""
        return [self.features.get(name, 0.0) for name in (self.feature_names or [])]

    def feature_count(self) -> int:
        """Get number of features"""
        return len(self.features)
