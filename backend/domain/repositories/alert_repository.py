"""
Alert Repository Interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities import Alert, AlertStatus, AlertLevel


class IAlertRepository(ABC):
    """Repository interface for Alert entity"""

    @abstractmethod
    async def save(self, alert: Alert) -> Alert:
        """Save or update an alert"""
        pass

    @abstractmethod
    async def find_by_id(self, alert_id: UUID) -> Optional[Alert]:
        """Find alert by ID"""
        pass

    @abstractmethod
    async def find_by_machine(
        self,
        machine_id: UUID,
        status: Optional[AlertStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Alert]:
        """Find alerts by machine, optionally filtered by status"""
        pass

    @abstractmethod
    async def find_by_site(
        self,
        site_id: UUID,
        level: Optional[AlertLevel] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Alert]:
        """Find alerts by site, optionally filtered by level"""
        pass

    @abstractmethod
    async def find_open_alerts(self, tenant_id: UUID) -> List[Alert]:
        """Find all open alerts for a tenant"""
        pass

    @abstractmethod
    async def delete(self, alert_id: UUID) -> bool:
        """Delete an alert"""
        pass
