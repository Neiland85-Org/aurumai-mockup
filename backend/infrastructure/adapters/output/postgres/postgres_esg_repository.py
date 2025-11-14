"""
Concrete PostgreSQL implementation of IESGRepository
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.esg_repository import IESGRepository
from domain.entities.esg import ESGRecord
from infrastructure.db.models import ESGRecordModel


class PostgresESGRepository(IESGRepository):
    """PostgreSQL implementation of ESG repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, record: ESGRecord) -> ESGRecord:
        """Save ESG record"""
        model = ESGRecordModel(
            machine_id=record.machine_id,
            timestamp=record.timestamp,
            instant_co2eq_kg=record.instant_co2eq_kg,
            cumulative_co2eq_kg=record.cumulative_co2eq_kg,
            fuel_rate_lh=record.fuel_rate_lh,
            power_consumption_kw=record.power_consumption_kw,
            efficiency_score=record.efficiency_score,
            metadata_json=record.metadata,
        )
        self.session.add(model)
        await self.session.flush()

        return self._model_to_entity(model)

    async def get_latest(self, machine_id: str) -> Optional[ESGRecord]:
        """Get latest ESG record for machine"""
        stmt = (
            select(ESGRecordModel)
            .where(ESGRecordModel.machine_id == machine_id)
            .order_by(desc(ESGRecordModel.timestamp))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return self._model_to_entity(model)
        return None

    async def get_history(self, machine_id: str, limit: int = 100) -> List[ESGRecord]:
        """Get ESG history for machine"""
        stmt = (
            select(ESGRecordModel)
            .where(ESGRecordModel.machine_id == machine_id)
            .order_by(desc(ESGRecordModel.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def get_range(
        self,
        machine_id: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[ESGRecord]:
        """Get ESG records within time range"""
        stmt = (
            select(ESGRecordModel)
            .where(
                ESGRecordModel.machine_id == machine_id,
                ESGRecordModel.timestamp >= start_time,
                ESGRecordModel.timestamp <= end_time,
            )
            .order_by(ESGRecordModel.timestamp)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def get_total_emissions(self, machine_id: Optional[str] = None) -> float:
        """Get total cumulative emissions (all machines or specific machine)"""
        if machine_id:
            # Get latest cumulative value for specific machine
            latest = await self.get_latest(machine_id)
            return latest.cumulative_co2eq_kg if latest else 0.0
        else:
            # Sum latest cumulative values across all machines
            # This is a simplified approach; in production you'd use a more sophisticated query
            stmt = select(
                ESGRecordModel.machine_id,
                func.max(ESGRecordModel.cumulative_co2eq_kg).label("max_cumulative"),
            ).group_by(ESGRecordModel.machine_id)
            result = await self.session.execute(stmt)
            rows = result.all()

            total = sum(row.max_cumulative for row in rows if row.max_cumulative)
            return total

    async def get_summary_stats(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> dict:
        """Get summary statistics for ESG metrics"""
        stmt = select(
            func.sum(ESGRecordModel.instant_co2eq_kg).label("total_instant"),
            func.avg(ESGRecordModel.instant_co2eq_kg).label("avg_instant"),
            func.max(ESGRecordModel.instant_co2eq_kg).label("max_instant"),
            func.sum(ESGRecordModel.fuel_rate_lh).label("total_fuel"),
            func.sum(ESGRecordModel.power_consumption_kw).label("total_power"),
        )

        if start_time:
            stmt = stmt.where(ESGRecordModel.timestamp >= start_time)
        if end_time:
            stmt = stmt.where(ESGRecordModel.timestamp <= end_time)

        result = await self.session.execute(stmt)
        row = result.one()

        return {
            "total_instant_co2eq_kg": row.total_instant or 0.0,
            "avg_instant_co2eq_kg": row.avg_instant or 0.0,
            "max_instant_co2eq_kg": row.max_instant or 0.0,
            "total_fuel_liters": row.total_fuel or 0.0,
            "total_power_kwh": row.total_power or 0.0,
        }

    def _model_to_entity(self, model: ESGRecordModel) -> ESGRecord:
        """Convert SQLAlchemy model to domain entity"""
        return ESGRecord(
            machine_id=model.machine_id,
            timestamp=model.timestamp,
            instant_co2eq_kg=model.instant_co2eq_kg,
            cumulative_co2eq_kg=model.cumulative_co2eq_kg,
            fuel_rate_lh=model.fuel_rate_lh,
            power_consumption_kw=model.power_consumption_kw,
            efficiency_score=model.efficiency_score,
            metadata=model.metadata_json or {},
        )
