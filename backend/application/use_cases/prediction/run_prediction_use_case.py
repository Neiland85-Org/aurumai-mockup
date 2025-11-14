"""
Use Case: Run Predictive Maintenance Prediction
Executes ML prediction for a machine and stores the result
"""
from datetime import datetime
from typing import Dict, Any, Optional

from domain.repositories.machine_repository import IMachineRepository
from domain.repositories.measurement_repository import IMeasurementRepository
from domain.repositories.prediction_repository import IPredictionRepository
from domain.entities.prediction import Prediction
from domain.services.ml_service import IMLService


class RunPredictionUseCase:
    """
    Application use case for running predictive maintenance predictions.
    Fetches latest features, runs ML model, and stores prediction.
    """

    def __init__(
        self,
        machine_repo: IMachineRepository,
        measurement_repo: IMeasurementRepository,
        prediction_repo: IPredictionRepository,
        ml_service: IMLService,
    ):
        self.machine_repo = machine_repo
        self.measurement_repo = measurement_repo
        self.prediction_repo = prediction_repo
        self.ml_service = ml_service

    async def execute(self, machine_id: str) -> Prediction:
        """
        Run prediction for a machine.

        Args:
            machine_id: ID of the machine to predict for

        Returns:
            Prediction entity with results

        Raises:
            ValueError: If machine doesn't exist or no features available
        """
        # Validate machine exists
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")

        # Get latest features
        features = await self.measurement_repo.get_latest_features(machine_id)
        if not features:
            raise ValueError(f"No features available for machine {machine_id}")

        # Run ML prediction
        prediction_result = await self.ml_service.predict(
            machine_id=machine_id,
            machine_type=machine.machine_type,
            features=features.features,
        )

        # Create prediction entity
        prediction = Prediction(
            machine_id=machine_id,
            timestamp=datetime.utcnow(),
            risk_score=prediction_result["risk_score"],
            failure_probability=prediction_result["failure_probability"],
            maintenance_hours=prediction_result["maintenance_hours"],
            failure_type=prediction_result.get("failure_type"),
            confidence=prediction_result.get("confidence"),
            model_version=prediction_result.get("model_version", "v1.0"),
            features_used=features.features,
        )

        # Save prediction
        saved_prediction = await self.prediction_repo.save(prediction)

        return saved_prediction

    async def get_history(
        self,
        machine_id: str,
        limit: int = 50,
    ) -> list[Prediction]:
        """
        Get prediction history for a machine.

        Args:
            machine_id: ID of the machine
            limit: Maximum number of predictions to return

        Returns:
            List of historical predictions
        """
        # Validate machine exists
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")

        return await self.prediction_repo.get_history(machine_id, limit)

    async def get_latest(self, machine_id: str) -> Optional[Prediction]:
        """
        Get latest prediction for a machine.

        Args:
            machine_id: ID of the machine

        Returns:
            Latest prediction or None if no predictions exist
        """
        # Validate machine exists
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")

        return await self.prediction_repo.get_latest(machine_id)

    async def get_high_risk_machines(
        self,
        risk_threshold: float = 0.7,
        limit: int = 100,
    ) -> list[Prediction]:
        """
        Get machines with high risk predictions.

        Args:
            risk_threshold: Minimum risk score to include
            limit: Maximum number of predictions to return

        Returns:
            List of high-risk predictions
        """
        return await self.prediction_repo.get_high_risk_predictions(
            risk_threshold=risk_threshold,
            limit=limit,
        )
