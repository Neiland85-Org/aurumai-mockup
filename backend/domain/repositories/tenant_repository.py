"""
Tenant Repository Interface
"""

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.entities import Tenant


class ITenantRepository(ABC):
    """Repository interface for Tenant aggregate"""

    @abstractmethod
    async def save(self, tenant: Tenant) -> Tenant:
        """Save or update a tenant"""
        pass

    @abstractmethod
    async def find_by_id(self, tenant_id: UUID) -> Tenant | None:
        """Find tenant by ID"""
        pass

    @abstractmethod
    async def find_by_code(self, code: str) -> Tenant | None:
        """Find tenant by code"""
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        """Find all tenants"""
        pass

    @abstractmethod
    async def delete(self, tenant_id: UUID) -> bool:
        """Delete a tenant"""
        pass
