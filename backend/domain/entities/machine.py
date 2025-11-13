"""
Machine Entity - Industrial asset/equipment

Represents physical machinery (trucks, mills, boilers, pumps, turbines, etc.)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from uuid import UUID, uuid4


@dataclass
class MachineSpec:
    """Technical specifications of a machine"""
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    year: Optional[int] = None
    capacity: Optional[float] = None
    capacity_unit: Optional[str] = None
    power_rating: Optional[float] = None  # kW
    fuel_type: Optional[str] = None  # diesel, electric, hybrid, gas


@dataclass
class Machine:
    """
    Machine entity

    Represents an industrial asset/machine that can have sensors attached.
    Central entity for predictive maintenance and ESG metrics.
    """
    id: UUID
    tenant_id: UUID
    site_id: UUID
    name: str
    code: str  # e.g., "TRUCK-21", "MILL-3", "BOILER-7"
    machine_type: str  # truck, mill, crusher, boiler, pump, turbine, conveyor, etc.
    category: str  # mobile, fixed, process
    spec: MachineSpec
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    is_operational: bool = True
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    metadata: Dict[str, any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    @staticmethod
    def create(
        tenant_id: UUID,
        site_id: UUID,
        name: str,
        code: str,
        machine_type: str,
        category: str = "fixed",
        spec: Optional[MachineSpec] = None
    ) -> "Machine":
        """Factory method to create a new machine"""
        now = datetime.utcnow()
        return Machine(
            id=uuid4(),
            tenant_id=tenant_id,
            site_id=site_id,
            name=name,
            code=code,
            machine_type=machine_type,
            category=category,
            spec=spec or MachineSpec(),
            created_at=now,
            updated_at=now,
            is_active=True,
            is_operational=True,
            metadata={},
            tags=[]
        )

    def update_operational_status(self, is_operational: bool) -> None:
        """Update machine operational status"""
        self.is_operational = is_operational
        self.updated_at = datetime.utcnow()

    def record_maintenance(self, next_maintenance: Optional[datetime] = None) -> None:
        """Record maintenance performed"""
        self.last_maintenance = datetime.utcnow()
        self.next_maintenance = next_maintenance
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate machine"""
        self.is_active = False
        self.is_operational = False
        self.updated_at = datetime.utcnow()
