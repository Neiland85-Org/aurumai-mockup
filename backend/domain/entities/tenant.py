"""
Tenant Entity - Multi-tenant support

Each tenant represents a customer/organization using the platform.
Tenants are isolated from each other and have their own configuration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Any
from uuid import UUID, uuid4


@dataclass
class TenantConfig:
    """Configuration specific to a tenant"""

    gdpr_enabled: bool = False
    data_residency: str = "EU"  # EU, LATAM, US, Other
    esg_frameworks: List[str] = field(default_factory=lambda: ["GHG_PROTOCOL", "IPCC"])
    timezone: str = "UTC"
    language: str = "en"


@dataclass
class Tenant:
    """
    Tenant aggregate root

    Represents a customer organization using AurumAI Platform.
    Each tenant has isolated data and configuration.
    """

    id: UUID
    name: str
    code: str  # Short identifier (e.g., "AR_001", "ES_MINING_01")
    industry: str  # mining, coal, cement, energy, heavy_industry
    region: str  # LATAM, EU, NA, APAC, AFRICA
    config: TenantConfig
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        name: str,
        code: str,
        industry: str,
        region: str,
        config: Optional[TenantConfig] = None,
    ) -> "Tenant":
        """Factory method to create a new tenant"""
        now = datetime.utcnow()
        return Tenant(
            id=uuid4(),
            name=name,
            code=code,
            industry=industry,
            region=region,
            config=config or TenantConfig(),
            created_at=now,
            updated_at=now,
            is_active=True,
            metadata={},
        )

    def update_config(self, config: TenantConfig) -> None:
        """Update tenant configuration"""
        self.config = config
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate tenant"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate tenant"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
