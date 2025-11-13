"""
EmissionFactor Entity - Emission conversion factors

Represents emission factors used to calculate CO2 equivalent from activity data.
Supports versioning and multiple methodologies (IPCC, country-specific, custom).
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict
from uuid import UUID, uuid4
from enum import Enum


class EmissionFactorSource(str, Enum):
    """Source of emission factor"""
    IPCC_2006 = "ipcc_2006"
    IPCC_2019 = "ipcc_2019"
    EU_ETS = "eu_ets"
    EPA = "epa"
    DEFRA = "defra"
    IEA = "iea"
    COUNTRY_SPECIFIC = "country_specific"
    CUSTOM = "custom"


@dataclass
class EmissionFactor:
    """
    EmissionFactor entity

    Represents an emission factor for converting activity data to CO2eq.
    Factors are versioned and have validity periods.
    """
    id: UUID
    name: str
    code: str  # e.g., "DIESEL_MOBILE", "ELEC_GRID_ES", "COAL_COMBUSTION"
    activity_type: str  # fuel_consumption, electricity, process, etc.
    activity_unit: str  # liters, kWh, kg, tons, etc.
    co2_factor: float  # kg CO2 per activity unit
    ch4_factor: float = 0.0  # kg CH4 per activity unit
    n2o_factor: float = 0.0  # kg N2O per activity unit
    co2eq_factor: float = 0.0  # Total kg CO2eq per activity unit (calculated)
    source: EmissionFactorSource = EmissionFactorSource.IPCC_2019
    country: Optional[str] = None  # ISO country code
    region: Optional[str] = None
    valid_from: date = field(default_factory=lambda: date(2024, 1, 1))
    valid_to: Optional[date] = None
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate total CO2eq factor using GWP100"""
        # GWP100: CH4 = 25, N2O = 298 (IPCC AR4)
        # More recent IPCC AR5: CH4 = 28, N2O = 265
        # We use AR5 values
        if self.co2eq_factor == 0.0:
            self.co2eq_factor = self.co2_factor + (self.ch4_factor * 28) + (self.n2o_factor * 265)

    @staticmethod
    def create(
        name: str,
        code: str,
        activity_type: str,
        activity_unit: str,
        co2_factor: float,
        ch4_factor: float = 0.0,
        n2o_factor: float = 0.0,
        source: EmissionFactorSource = EmissionFactorSource.IPCC_2019,
        country: Optional[str] = None,
        region: Optional[str] = None,
        valid_from: Optional[date] = None,
        valid_to: Optional[date] = None,
        version: str = "1.0",
        metadata: Optional[Dict[str, any]] = None
    ) -> "EmissionFactor":
        """Factory method to create a new emission factor"""
        now = datetime.utcnow()
        factor = EmissionFactor(
            id=uuid4(),
            name=name,
            code=code,
            activity_type=activity_type,
            activity_unit=activity_unit,
            co2_factor=co2_factor,
            ch4_factor=ch4_factor,
            n2o_factor=n2o_factor,
            source=source,
            country=country,
            region=region,
            valid_from=valid_from or date(2024, 1, 1),
            valid_to=valid_to,
            version=version,
            created_at=now,
            updated_at=now,
            is_active=True,
            metadata=metadata or {}
        )
        factor.__post_init__()  # Calculate CO2eq
        return factor

    def is_valid_for_date(self, check_date: date) -> bool:
        """Check if factor is valid for a given date"""
        if check_date < self.valid_from:
            return False
        if self.valid_to and check_date > self.valid_to:
            return False
        return self.is_active

    def deactivate(self) -> None:
        """Deactivate emission factor"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
