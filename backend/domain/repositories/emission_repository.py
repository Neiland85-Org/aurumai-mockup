"""
Emission Repository Interface
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID
from domain.entities import EmissionSource, EmissionFactor, EmissionRecord


class IEmissionRepository(ABC):
    """Repository interface for ESG/Emissions entities"""

    @abstractmethod
    async def save_source(self, source: EmissionSource) -> EmissionSource:
        """Save or update an emission source"""
        pass

    @abstractmethod
    async def find_source_by_id(self, source_id: UUID) -> Optional[EmissionSource]:
        """Find emission source by ID"""
        pass

    @abstractmethod
    async def find_sources_by_site(self, site_id: UUID) -> List[EmissionSource]:
        """Find emission sources by site"""
        pass

    @abstractmethod
    async def save_factor(self, factor: EmissionFactor) -> EmissionFactor:
        """Save or update an emission factor"""
        pass

    @abstractmethod
    async def find_factor_by_code(self, code: str) -> Optional[EmissionFactor]:
        """Find emission factor by code"""
        pass

    @abstractmethod
    async def find_active_factors(self) -> List[EmissionFactor]:
        """Find all active emission factors"""
        pass

    @abstractmethod
    async def save_record(self, record: EmissionRecord) -> EmissionRecord:
        """Save an emission record"""
        pass

    @abstractmethod
    async def save_records_batch(self, records: List[EmissionRecord]) -> int:
        """Save multiple emission records"""
        pass

    @abstractmethod
    async def get_emissions_by_site(
        self,
        site_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> List[EmissionRecord]:
        """Get emission records for a site in a time range"""
        pass

    @abstractmethod
    async def get_emissions_summary(
        self,
        tenant_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> Dict:
        """Get aggregated emissions summary"""
        pass
