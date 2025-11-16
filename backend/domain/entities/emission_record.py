"""
EmissionRecord Entity - Calculated emissions

Represents calculated emissions for a given activity and time period.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from uuid import UUID, uuid4


@dataclass
class EmissionRecord:
    """
    EmissionRecord entity

    Represents a calculated emission record.
    Links activity data with emission factors to produce CO2eq values.
    """

    id: UUID
    tenant_id: UUID
    site_id: UUID
    emission_source_id: UUID
    emission_factor_id: UUID
    machine_id: Optional[UUID]
    timestamp: datetime
    period_start: datetime
    period_end: datetime
    activity_value: float  # Amount of activity (liters, kWh, kg, etc.)
    activity_unit: str
    co2_kg: float
    ch4_kg: float
    n2o_kg: float
    co2eq_kg: float  # Total CO2 equivalent
    calculation_method: str = "direct"  # direct, estimated, modeled
    confidence_level: float = 1.0  # 0.0 to 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        tenant_id: UUID,
        site_id: UUID,
        emission_source_id: UUID,
        emission_factor_id: UUID,
        timestamp: datetime,
        period_start: datetime,
        period_end: datetime,
        activity_value: float,
        activity_unit: str,
        co2_kg: float,
        ch4_kg: float,
        n2o_kg: float,
        co2eq_kg: float,
        machine_id: Optional[UUID] = None,
        calculation_method: str = "direct",
        confidence_level: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "EmissionRecord":
        """Factory method to create a new emission record"""
        return EmissionRecord(
            id=uuid4(),
            tenant_id=tenant_id,
            site_id=site_id,
            emission_source_id=emission_source_id,
            emission_factor_id=emission_factor_id,
            machine_id=machine_id,
            timestamp=timestamp,
            period_start=period_start,
            period_end=period_end,
            activity_value=activity_value,
            activity_unit=activity_unit,
            co2_kg=co2_kg,
            ch4_kg=ch4_kg,
            n2o_kg=n2o_kg,
            co2eq_kg=co2eq_kg,
            calculation_method=calculation_method,
            confidence_level=confidence_level,
            created_at=datetime.now(timezone.utc),
            metadata=metadata or {},
        )

    @property
    def co2eq_tons(self) -> float:
        """Convert CO2eq to tons"""
        return self.co2eq_kg / 1000.0

    @property
    def duration_hours(self) -> float:
        """Calculate period duration in hours"""
        delta = self.period_end - self.period_start
        return delta.total_seconds() / 3600.0
