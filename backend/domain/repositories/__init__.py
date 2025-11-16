"""
Repository Interfaces (Ports) for Domain Layer

These are abstract interfaces that define how the domain accesses persistence.
Implementations are provided by the infrastructure layer (adapters).
"""

from .alert_repository import IAlertRepository
from .emission_repository import IEmissionRepository
from .esg_repository import IESGRepository
from .machine_repository import IMachineRepository
from .measurement_repository import IMeasurementRepository
from .prediction_repository import IPredictionRepository
from .sensor_repository import ISensorRepository
from .tenant_repository import ITenantRepository

__all__ = [
    "IAlertRepository",
    "IESGRepository",
    "IEmissionRepository",
    "IMachineRepository",
    "IMeasurementRepository",
    "IPredictionRepository",
    "ISensorRepository",
    "ITenantRepository",
]
