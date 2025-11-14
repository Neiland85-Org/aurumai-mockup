"""
Domain Entity: ESG Record
Represents ESG/Carbon emissions data
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class ESGRecord:
    """
    ESG Record domain entity.
    Contains carbon emissions and environmental metrics.
    """

    machine_id: str
    timestamp: datetime
    instant_co2eq_kg: float
    cumulative_co2eq_kg: float
    fuel_rate_lh: Optional[float] = None
    power_consumption_kw: Optional[float] = None
    efficiency_score: Optional[float] = None
    metadata: Dict[str, any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate ESG data"""
        if not self.machine_id or not self.machine_id.strip():
            raise ValueError("machine_id cannot be empty")

        if self.instant_co2eq_kg < 0:
            raise ValueError("instant_co2eq_kg cannot be negative")

        if self.cumulative_co2eq_kg < 0:
            raise ValueError("cumulative_co2eq_kg cannot be negative")

        if self.efficiency_score is not None and not (
            0 <= self.efficiency_score <= 100
        ):
            raise ValueError("efficiency_score must be between 0 and 100")

    def get_scope(self) -> str:
        """Get dominant emission scope from metadata"""
        return self.metadata.get("dominant_scope", "unknown")

    def get_breakdown(self) -> Dict[str, float]:
        """Get emissions breakdown by scope"""
        return self.metadata.get("breakdown", {})
