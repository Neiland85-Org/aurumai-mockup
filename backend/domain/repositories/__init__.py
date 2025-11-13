"""
Repository Interfaces (Ports) for Domain Layer

These are abstract interfaces that define how the domain accesses persistence.
Implementations are provided by the infrastructure layer (adapters).
"""

from .tenant_repository import ITenantRepository
from .machine_repository import IMachineRepository
from .sensor_repository import ISensorRepository
from .measurement_repository import IMeasurementRepository
from .alert_repository import IAlertRepository
from .emission_repository import IEmissionRepository

__all__ = [
    "ITenantRepository",
    "IMachineRepository",
    "ISensorRepository",
    "IMeasurementRepository",
    "IAlertRepository",
    "IEmissionRepository",
]
