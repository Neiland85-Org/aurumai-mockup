"""Domain Entities for AurumAI Platform

Expose all core entity classes and selected enums for convenient imports.

NOTE: Added AlertStatus, AlertLevel, AlertCategory to fix ImportError in
repository layer expecting these symbols from ``domain.entities``.
"""

from .tenant import Tenant
from .site import Site
from .asset import Asset
from .machine import Machine
from .sensor import Sensor
from .alert import Alert, AlertLevel, AlertStatus, AlertCategory
from .event import Event
from .emission_source import EmissionSource
from .emission_factor import EmissionFactor
from .emission_record import EmissionRecord

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
