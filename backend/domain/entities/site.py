"""
Site Entity - Physical location

Represents a mine, plant, factory, or any physical location where assets operate.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


@dataclass
class SiteLocation:
    """Geographic location of a site"""

    latitude: float
    longitude: float
    altitude: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = ""


@dataclass
class Site:
    """
    Site entity

    Represents a physical location (mine, plant, facility) where assets operate.
    Belongs to a single tenant.
    """

    id: UUID
    tenant_id: UUID
    name: str
    code: str  # e.g., "MINE_CATAMARCA", "PLANT_ASTURIAS"
    site_type: str  # mine, plant, facility, office
    location: SiteLocation
    timezone: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        tenant_id: UUID,
        name: str,
        code: str,
        site_type: str,
        location: SiteLocation,
        timezone: str = "UTC",
    ) -> "Site":
        """Factory method to create a new site"""
        now = datetime.utcnow()
        return Site(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name,
            code=code,
            site_type=site_type,
            location=location,
            timezone=timezone,
            created_at=now,
            updated_at=now,
            is_active=True,
            metadata={},
        )

    def update_location(self, location: SiteLocation) -> None:
        """Update site location"""
        self.location = location
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate site"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
