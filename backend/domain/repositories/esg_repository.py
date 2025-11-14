"""
ESG Repository Interface
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict

from domain.entities.esg import ESGRecord


class IESGRepository(ABC):
    """Repository interface for ESG/Carbon emission records"""

    @abstractmethod
    async def save(self, record: ESGRecord) -> ESGRecord:
        """Persist an ESG record and return the stored entity"""
        raise NotImplementedError

    @abstractmethod
    async def get_latest(self, machine_id: str) -> Optional[ESGRecord]:
        """Fetch latest ESG record for a machine"""
        raise NotImplementedError

    @abstractmethod
    async def get_history(self, machine_id: str, limit: int = 100) -> List[ESGRecord]:
        """Fetch last N ESG records for a machine"""
        raise NotImplementedError

    @abstractmethod
    async def get_range(
        self,
        machine_id: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[ESGRecord]:
        """Fetch ESG records within a time range"""
        raise NotImplementedError

    @abstractmethod
    async def get_total_emissions(self, machine_id: Optional[str] = None) -> float:
        """Sum of cumulative emissions; all machines if machine_id is None"""
        raise NotImplementedError

    @abstractmethod
    async def get_summary_stats(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict:
        """Aggregate metrics (sum/avg/max) over ESG measurements"""
        raise NotImplementedError
