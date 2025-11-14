"""
Use Case: Ingest Telemetry Data
Handles ingestion of raw measurements and feature vectors from IoT/Edge devices
"""

from datetime import datetime
from typing import Dict, Any

from domain.repositories.machine_repository import IMachineRepository
from domain.repositories.measurement_repository import IMeasurementRepository
from domain.entities.measurement import RawMeasurement, FeatureVector


class IngestTelemetryUseCase:
    """
    Application use case for ingesting telemetry data.
    Validates machine existence before storing measurements.
    """

    def __init__(
        self,
        machine_repo: IMachineRepository,
        measurement_repo: IMeasurementRepository,
    ):
        self.machine_repo = machine_repo
        self.measurement_repo = measurement_repo

    async def execute_raw(
        self,
        machine_id: str,
        timestamp: datetime,
        metrics: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Ingest raw measurement from IoT device.

        Args:
            machine_id: ID of the machine sending data
            timestamp: Timestamp of measurement
            metrics: Dictionary of metric_name -> value

        Returns:
            Status dictionary with ingestion result

        Raises:
            ValueError: If machine doesn't exist
        """
        # Validate machine exists
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")

        # Create and save measurement
        measurement = RawMeasurement(
            machine_id=machine_id,
            timestamp=timestamp,
            metrics=metrics,
        )

        saved = await self.measurement_repo.save_raw_measurement(measurement)

        return {
            "status": "success",
            "message": f"Raw measurement ingested for machine {machine_id}",
            "machine_id": machine_id,
            "timestamp": timestamp.isoformat(),
            "metrics_count": len(metrics),
        }

    async def execute_features(
        self,
        machine_id: str,
        timestamp: datetime,
        features: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Ingest engineered features from edge device.

        Args:
            machine_id: ID of the machine
            timestamp: Timestamp of feature computation
            features: Dictionary of feature_name -> value

        Returns:
            Status dictionary with ingestion result

        Raises:
            ValueError: If machine doesn't exist
        """
        # Validate machine exists
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")

        # Create and save feature vector
        feature_vector = FeatureVector(
            machine_id=machine_id,
            timestamp=timestamp,
            features=features,
        )

        saved = await self.measurement_repo.save_feature_vector(feature_vector)

        return {
            "status": "success",
            "message": f"Features ingested for machine {machine_id}",
            "machine_id": machine_id,
            "timestamp": timestamp.isoformat(),
            "features_count": len(features),
        }

    async def execute_batch_raw(
        self,
        measurements: list[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Ingest batch of raw measurements.

        Args:
            measurements: List of measurement dicts with machine_id, timestamp, metrics

        Returns:
            Summary of batch ingestion
        """
        successful = 0
        failed = 0
        errors = []

        for measurement_data in measurements:
            try:
                await self.execute_raw(
                    machine_id=measurement_data["machine_id"],
                    timestamp=measurement_data["timestamp"],
                    metrics=measurement_data["metrics"],
                )
                successful += 1
            except Exception as e:
                failed += 1
                errors.append(
                    {
                        "machine_id": measurement_data.get("machine_id"),
                        "error": str(e),
                    }
                )

        return {
            "status": "completed",
            "total": len(measurements),
            "successful": successful,
            "failed": failed,
            "errors": errors if errors else None,
        }
