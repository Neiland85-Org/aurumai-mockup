"""
EmissionSource Entity - Sources of emissions

Represents sources of greenhouse gas emissions (mobile, fixed, electricity, process).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID, uuid4
from enum import Enum


class EmissionScope(str, Enum):
    """GHG Protocol scopes"""
    SCOPE_1 = "scope_1"  # Direct emissions
    SCOPE_2 = "scope_2"  # Indirect emissions from purchased energy
    SCOPE_3 = "scope_3"  # Other indirect emissions


class EmissionSourceType(str, Enum):
    """Types of emission sources"""
    MOBILE_COMBUSTION = "mobile_combustion"  # Trucks, excavators, loaders
    STATIONARY_COMBUSTION = "stationary_combustion"  # Boilers, furnaces, generators
    ELECTRICITY = "electricity"  # Purchased electricity
    PROCESS = "process"  # Industrial processes (cement, steel, mining)
    FUGITIVE = "fugitive"  # Leaks, venting
    WASTE = "waste"  # Waste treatment


@dataclass
class EmissionSource:
    """
    EmissionSource entity

    Represents a source of GHG emissions.
    Can be associated with a machine or a site-level process.
    """
    id: UUID
    tenant_id: UUID
    site_id: UUID
    machine_id: Optional[UUID]  # None for site-level sources
    name: str
    code: str
    source_type: EmissionSourceType
    scope: EmissionScope
    fuel_type: Optional[str] = None  # diesel, gasoline, natural_gas, coal, electric, etc.
    capacity: Optional[float] = None
    capacity_unit: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, any] = field(default_factory=dict)

    @staticmethod
    def create(
        tenant_id: UUID,
        site_id: UUID,
        name: str,
        code: str,
        source_type: EmissionSourceType,
        scope: EmissionScope,
        machine_id: Optional[UUID] = None,
        fuel_type: Optional[str] = None,
        capacity: Optional[float] = None,
        capacity_unit: Optional[str] = None,
        metadata: Optional[Dict[str, any]] = None
    ) -> "EmissionSource":
        """Factory method to create a new emission source"""
        now = datetime.utcnow()
        return EmissionSource(
            id=uuid4(),
            tenant_id=tenant_id,
            site_id=site_id,
            machine_id=machine_id,
            name=name,
            code=code,
            source_type=source_type,
            scope=scope,
            fuel_type=fuel_type,
            capacity=capacity,
            capacity_unit=capacity_unit,
            created_at=now,
            updated_at=now,
            is_active=True,
            metadata=metadata or {}
        )

    def deactivate(self) -> None:
        """Deactivate emission source"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
