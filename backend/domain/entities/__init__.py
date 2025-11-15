"""Domain Entities for AurumAI Platform

Expose all core entity classes and selected enums for convenient imports.

NOTE: Added AlertStatus, AlertLevel, AlertCategory to fix ImportError in
repository layer expecting these symbols from ``domain.entities``.
"""

from .alert import Alert, AlertCategory, AlertLevel, AlertStatus
from .asset import Asset
from .emission_factor import EmissionFactor
from .emission_record import EmissionRecord
from .emission_source import EmissionSource
from .event import Event
from .machine import Machine
from .sensor import Sensor
from .site import Site
from .tenant import Tenant

__all__ = [
    "Tenant",
    "Site",
    "Asset",
    "Machine",
    "Sensor",
    "Alert",
    "AlertLevel",
    "AlertStatus",
    "AlertCategory",
    "Event",
    "EmissionSource",
    "EmissionFactor",
    "EmissionRecord",
]
