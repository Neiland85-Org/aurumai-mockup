"""
Domain Service Interface: Machine Learning Service
Defines contract for ML prediction operations
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class IMLService(ABC):
    """Interface for ML prediction service"""

    @abstractmethod
    async def predict(
        self,
        machine_id: str,
        machine_type: str,
        features: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Run ML prediction for a machine.

        Args:
            machine_id: ID of the machine
            machine_type: Type of machine (haul_truck, grinding_mill, etc.)
            features: Dictionary of engineered features

        Returns:
            Dictionary with prediction results containing:
            - risk_score: float (0-1)
            - failure_probability: float (0-1)
            - maintenance_hours: int
            - failure_type: str (optional)
            - confidence: float (optional)
            - model_version: str (optional)
        """
        pass
