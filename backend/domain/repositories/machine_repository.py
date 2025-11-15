"""
Machine Repository Interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities import Machine


class IMachineRepository(ABC):
    """Repository interface for Machine entity"""

    @abstractmethod
    async def save(self, machine: Machine) -> Machine:
        """Save or update a machine"""
        pass

    @abstractmethod
    async def find_by_id(self, machine_id: UUID) -> Optional[Machine]:
        """Find machine by ID"""
        pass

    @abstractmethod
    async def find_by_code(self, tenant_id: UUID, code: str) -> Optional[Machine]:
        """Find machine by code within a tenant"""
        pass

    @abstractmethod
    async def find_by_site(
        self, site_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Machine]:
        """Find machines by site"""
        pass

    @abstractmethod
    async def find_by_tenant(
        self, tenant_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Machine]:
        """Find machines by tenant"""
        pass

    @abstractmethod
    async def delete(self, machine_id: UUID) -> bool:
        """Delete a machine"""
        pass

    # Aliases for compatibility with use cases
    async def get_by_id(self, machine_id: str) -> Optional[Machine]:
        """Alias for find_by_id (accepts string)"""
        try:
            uuid_id = UUID(machine_id) if isinstance(machine_id, str) else machine_id
            return await self.find_by_id(uuid_id)
        except (ValueError, AttributeError):
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Machine]:
        """Get all machines (default implementation)"""
        # This should be implemented by concrete repositories
        # For now, return empty list - subclasses should override
        return []
