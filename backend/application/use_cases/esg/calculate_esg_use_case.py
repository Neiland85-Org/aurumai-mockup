"""
Use Case: Calculate ESG Metrics
Calculates carbon emissions and ESG metrics for machines
"""
from datetime import datetime
from typing import Dict, Any, Optional

from domain.repositories.machine_repository import IMachineRepository
from domain.repositories.measurement_repository import IMeasurementRepository
from domain.repositories.esg_repository import IESGRepository
from domain.entities.esg import ESGRecord
from domain.services.esg_service import IESGService


class CalculateESGUseCase:
    """
    Application use case for calculating ESG/carbon metrics.
    Computes emissions based on latest measurements and stores results.
    """

    def __init__(
        self,
        machine_repo: IMachineRepository,
        measurement_repo: IMeasurementRepository,
        esg_repo: IESGRepository,
        esg_service: IESGService,
    ):
        self.machine_repo = machine_repo
        self.measurement_repo = measurement_repo
        self.esg_repo = esg_repo
        self.esg_service = esg_service

    async def execute(self, machine_id: str) -> ESGRecord:
        """
        Calculate ESG metrics for a machine.

        Args:
            machine_id: ID of the machine to calculate ESG for

        Returns:
            ESGRecord entity with calculated metrics

        Raises:
            ValueError: If machine doesn't exist or no measurements available
        """
        # Validate machine exists
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")

        # Get latest raw measurement
        measurement = await self.measurement_repo.get_latest_raw_measurement(machine_id)
        if not measurement:
            raise ValueError(f"No measurements available for machine {machine_id}")

        # Get previous ESG record for cumulative calculation
        previous_esg = await self.esg_repo.get_latest(machine_id)
        previous_cumulative = previous_esg.cumulative_co2eq_kg if previous_esg else 0.0

        # Calculate ESG metrics
        esg_result = await self.esg_service.calculate(
            machine_id=machine_id,
            machine_type=machine.machine_type,
            metrics=measurement.metrics,
            previous_cumulative=previous_cumulative,
        )

        # Create ESG record entity
        esg_record = ESGRecord(
            machine_id=machine_id,
            timestamp=datetime.utcnow(),
            instant_co2eq_kg=esg_result["instant_co2eq_kg"],
            cumulative_co2eq_kg=esg_result["cumulative_co2eq_kg"],
            fuel_rate_lh=esg_result.get("fuel_rate_lh"),
            power_consumption_kw=esg_result.get("power_consumption_kw"),
            efficiency_score=esg_result.get("efficiency_score"),
            metadata=esg_result.get("metadata", {}),
        )

        # Save ESG record
        saved_record = await self.esg_repo.save(esg_record)

        return saved_record

    async def get_current(self, machine_id: str) -> Optional[ESGRecord]:
        """
        Get current (latest) ESG metrics for a machine.

        Args:
            machine_id: ID of the machine

        Returns:
            Latest ESG record or None if no records exist
        """
        # Validate machine exists
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")

        return await self.esg_repo.get_latest(machine_id)

    async def get_history(
        self,
        machine_id: str,
        limit: int = 100,
    ) -> list[ESGRecord]:
        """
        Get ESG history for a machine.

        Args:
            machine_id: ID of the machine
            limit: Maximum number of records to return

        Returns:
            List of historical ESG records
        """
        # Validate machine exists
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")

        return await self.esg_repo.get_history(machine_id, limit)

    async def get_summary(self) -> Dict[str, Any]:
        """
        Get ESG summary across all machines.

        Returns:
            Dictionary with aggregated ESG metrics
        """
        # Get all machines
        machines = await self.machine_repo.get_all()

        # Get latest ESG for each machine
        machine_esg = []
        for machine in machines:
            latest = await self.esg_repo.get_latest(machine.machine_id)
            if latest:
                machine_esg.append({
                    "machine_id": machine.machine_id,
                    "machine_type": machine.machine_type,
                    "instant_co2eq_kg": latest.instant_co2eq_kg,
                    "cumulative_co2eq_kg": latest.cumulative_co2eq_kg,
                    "fuel_rate_lh": latest.fuel_rate_lh,
                    "power_consumption_kw": latest.power_consumption_kw,
                })

        # Calculate totals
        total_instant = sum(m["instant_co2eq_kg"] for m in machine_esg)
        total_cumulative = sum(m["cumulative_co2eq_kg"] for m in machine_esg)
        total_fuel = sum(m["fuel_rate_lh"] or 0.0 for m in machine_esg)
        total_power = sum(m["power_consumption_kw"] or 0.0 for m in machine_esg)

        return {
            "total_machines": len(machines),
            "monitored_machines": len(machine_esg),
            "total_instant_co2eq_kg": total_instant,
            "total_cumulative_co2eq_kg": total_cumulative,
            "total_fuel_rate_lh": total_fuel,
            "total_power_consumption_kw": total_power,
            "machines": machine_esg,
        }

    async def get_total_emissions(
        self,
        machine_id: Optional[str] = None,
    ) -> float:
        """
        Get total cumulative emissions.

        Args:
            machine_id: Optional machine ID. If None, returns total for all machines

        Returns:
            Total cumulative CO2eq in kg
        """
        if machine_id:
            # Validate machine exists
            machine = await self.machine_repo.get_by_id(machine_id)
            if not machine:
                raise ValueError(f"Machine {machine_id} not found")

        return await self.esg_repo.get_total_emissions(machine_id)
