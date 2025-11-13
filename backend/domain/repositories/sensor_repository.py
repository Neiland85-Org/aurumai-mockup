"""
Sensor Repository Interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities import Sensor


class ISensorRepository(ABC):
    """Repository interface for Sensor entity"""

    @abstractmethod
    async def save(self, sensor: Sensor) -> Sensor:
        """Save or update a sensor"""
        pass

    @abstractmethod
    async def find_by_id(self, sensor_id: UUID) -> Optional[Sensor]:
        """Find sensor by ID"""
        pass

    @abstractmethod
    async def find_by_machine(self, machine_id: UUID) -> List[Sensor]:
        """Find sensors by machine"""
        pass

    @abstractmethod
    async def delete(self, sensor_id: UUID) -> bool:
        """Delete a sensor"""
        pass
