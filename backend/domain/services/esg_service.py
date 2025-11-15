"""
Domain Service Interface: ESG/Carbon Calculation Service
Defines contract for ESG metrics calculation
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IESGService(ABC):
    """Interface for ESG calculation service"""

    @abstractmethod
    async def calculate(
        self,
        machine_id: str,
        machine_type: str,
        metrics: Dict[str, float],
        previous_cumulative: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Calculate ESG/carbon metrics for a machine.

        Args:
            machine_id: ID of the machine
            machine_type: Type of machine
            metrics: Dictionary of raw metrics from telemetry
            previous_cumulative: Previous cumulative CO2eq value

        Returns:
            Dictionary with ESG results containing:
            - instant_co2eq_kg: float
            - cumulative_co2eq_kg: float
            - fuel_rate_lh: float (optional)
            - power_consumption_kw: float (optional)
            - efficiency_score: float (optional)
            - metadata: dict (optional)
        """
        pass
