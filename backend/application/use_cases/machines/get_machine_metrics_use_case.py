"""
Use Case: Get Machine Metrics
Retrieves comprehensive metrics and status for machines
"""

from typing import Any, Dict, List, Optional

from domain.entities.machine import Machine
from domain.repositories.esg_repository import IESGRepository
from domain.repositories.machine_repository import IMachineRepository
from domain.repositories.measurement_repository import IMeasurementRepository
from domain.repositories.prediction_repository import IPredictionRepository


class GetMachineMetricsUseCase:
    """
    Application use case for retrieving machine metrics.
    Aggregates data from multiple sources to provide complete machine status.
    """

    def __init__(
        self,
        machine_repo: IMachineRepository,
        measurement_repo: IMeasurementRepository,
        prediction_repo: IPredictionRepository,
        esg_repo: IESGRepository,
    ) -> None:
        self.machine_repo = machine_repo
        self.measurement_repo = measurement_repo
        self.prediction_repo = prediction_repo
        self.esg_repo = esg_repo

    async def execute(self, machine_id: str) -> Dict[str, Any]:
        """
        Get comprehensive metrics for a machine.

        Args:
            machine_id: ID of the machine

        Returns:
            Dictionary with complete machine status including:
            - Basic machine info
            - Latest raw measurements
            - Latest features
            - Latest prediction
            - Latest ESG metrics

        Raises:
            ValueError: If machine doesn't exist
        """
        # Get machine
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")

        # Get latest measurements
        raw_measurement = await self.measurement_repo.get_latest_raw_measurement(
            machine_id
        )
        features = await self.measurement_repo.get_latest_features(machine_id)

        # Get latest prediction
        prediction = await self.prediction_repo.get_latest(machine_id)

        # Get latest ESG
        esg = await self.esg_repo.get_latest(machine_id)

        # Build response
        return {
            "machine": {
                "machine_id": machine.machine_id,
                "machine_type": machine.machine_type,
                "location": machine.location,
                "operational": machine.operational,
            },
            "latest_measurement": (
                {
                    "timestamp": (
                        raw_measurement.timestamp.isoformat()
                        if raw_measurement
                        else None
                    ),
                    "metrics": raw_measurement.metrics if raw_measurement else {},
                }
                if raw_measurement
                else None
            ),
            "latest_features": (
                {
                    "timestamp": features.timestamp.isoformat() if features else None,
                    "features": features.features if features else {},
                }
                if features
                else None
            ),
            "latest_prediction": (
                {
                    "timestamp": (
                        prediction.timestamp.isoformat() if prediction else None
                    ),
                    "risk_score": prediction.risk_score if prediction else None,
                    "failure_probability": (
                        prediction.failure_probability if prediction else None
                    ),
                    "maintenance_hours": (
                        prediction.maintenance_hours if prediction else None
                    ),
                    "failure_type": prediction.failure_type if prediction else None,
                }
                if prediction
                else None
            ),
            "latest_esg": (
                {
                    "timestamp": esg.timestamp.isoformat() if esg else None,
                    "instant_co2eq_kg": esg.instant_co2eq_kg if esg else None,
                    "cumulative_co2eq_kg": esg.cumulative_co2eq_kg if esg else None,
                    "fuel_rate_lh": esg.fuel_rate_lh if esg else None,
                    "power_consumption_kw": esg.power_consumption_kw if esg else None,
                }
                if esg
                else None
            ),
        }

    async def get_all_machines(self) -> List[Dict[str, Any]]:
        """
        Get list of all machines with basic info.

        Returns:
            List of machine dictionaries
        """
        machines = await self.machine_repo.get_all()

        return [
            {
                "machine_id": machine.machine_id,
                "machine_type": machine.machine_type,
                "location": machine.location,
                "operational": machine.operational,
            }
            for machine in machines
        ]

    async def get_all_machines_with_status(self) -> List[Dict[str, Any]]:
        """
        Get list of all machines with latest status.

        Returns:
            List of machine dictionaries with latest metrics
        """
        machines = await self.machine_repo.get_all()

        result = []
        for machine in machines:
            # Get latest prediction for status
            prediction = await self.prediction_repo.get_latest(machine.machine_id)

            # Get latest ESG
            esg = await self.esg_repo.get_latest(machine.machine_id)

            result.append(
                {
                    "machine_id": machine.machine_id,
                    "machine_type": machine.machine_type,
                    "location": machine.location,
                    "operational": machine.operational,
                    "risk_score": prediction.risk_score if prediction else None,
                    "instant_co2eq_kg": esg.instant_co2eq_kg if esg else None,
                    "cumulative_co2eq_kg": esg.cumulative_co2eq_kg if esg else None,
                }
            )

        return result

    async def create_machine(
        self,
        machine_id: str,
        machine_type: str,
        location: str,
        operational: bool = True,
    ) -> Machine:
        """
        Create a new machine.

        Args:
            machine_id: Unique machine identifier
            machine_type: Type of machine
            location: Physical location
            operational: Whether machine is operational

        Returns:
            Created machine entity

        Raises:
            ValueError: If machine_id already exists
        """
        # Check if machine already exists
        existing = await self.machine_repo.get_by_id(machine_id)
        if existing:
            raise ValueError(f"Machine {machine_id} already exists")

        # Create machine entity
        machine = Machine(
            machine_id=machine_id,
            machine_type=machine_type,
            location=location,
            operational=operational,
        )

        # Save machine
        return await self.machine_repo.save(machine)

    async def update_machine(
        self,
        machine_id: str,
        machine_type: Optional[str] = None,
        location: Optional[str] = None,
        operational: Optional[bool] = None,
    ) -> Machine:
        """
        Update machine information.

        Args:
            machine_id: ID of machine to update
            machine_type: New machine type (optional)
            location: New location (optional)
            operational: New operational status (optional)

        Returns:
            Updated machine entity

        Raises:
            ValueError: If machine doesn't exist
        """
        # Get existing machine
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")

        # Update fields if provided
        if machine_type is not None:
            machine.machine_type = machine_type
        if location is not None:
            machine.location = location
        if operational is not None:
            machine.operational = operational

        # Save updated machine
        return await self.machine_repo.save(machine)

    async def delete_machine(self, machine_id: str) -> bool:
        """
        Delete a machine.

        Args:
            machine_id: ID of machine to delete

        Returns:
            True if deleted, False if not found
        """
        return await self.machine_repo.delete(machine_id)
