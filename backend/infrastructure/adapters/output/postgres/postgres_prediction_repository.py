"""
Concrete PostgreSQL implementation of IPredictionRepository
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.prediction_repository import IPredictionRepository
from domain.entities.prediction import Prediction
from infrastructure.db.models import PredictionModel


class PostgresPredictionRepository(IPredictionRepository):
    """PostgreSQL implementation of prediction repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, prediction: Prediction) -> Prediction:
        """Save prediction"""
        model = PredictionModel(
            machine_id=prediction.machine_id,
            timestamp=prediction.timestamp,
            risk_score=prediction.risk_score,
            failure_probability=prediction.failure_probability,
            maintenance_hours=prediction.maintenance_hours,
            failure_type=prediction.failure_type,
            confidence=prediction.confidence,
            model_version=prediction.model_version,
            features_used=prediction.features_used,
        )
        self.session.add(model)
        await self.session.flush()

        return self._model_to_entity(model)

    async def get_latest(self, machine_id: str) -> Optional[Prediction]:
        """Get latest prediction for machine"""
        stmt = (
            select(PredictionModel)
            .where(PredictionModel.machine_id == machine_id)
            .order_by(desc(PredictionModel.timestamp))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return self._model_to_entity(model)
        return None

    async def get_history(self, machine_id: str, limit: int = 50) -> List[Prediction]:
        """Get prediction history for machine"""
        stmt = (
            select(PredictionModel)
            .where(PredictionModel.machine_id == machine_id)
            .order_by(desc(PredictionModel.timestamp))
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
    ) -> List[Prediction]:
        """Get predictions within time range"""
        stmt = (
            select(PredictionModel)
            .where(
                PredictionModel.machine_id == machine_id,
                PredictionModel.timestamp >= start_time,
                PredictionModel.timestamp <= end_time,
            )
            .order_by(PredictionModel.timestamp)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def get_high_risk_predictions(
        self, risk_threshold: float = 0.7, limit: int = 100
    ) -> List[Prediction]:
        """Get predictions with high risk scores"""
        stmt = (
            select(PredictionModel)
            .where(PredictionModel.risk_score >= risk_threshold)
            .order_by(desc(PredictionModel.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    def _model_to_entity(self, model: PredictionModel) -> Prediction:
        """Convert SQLAlchemy model to domain entity"""
        # SQLAlchemy models use descriptors, so type checkers see Column types
        # but at runtime these are the actual values
        return Prediction(
            machine_id=model.machine_id,  # type: ignore
            timestamp=model.timestamp,  # type: ignore
            risk_score=model.risk_score,  # type: ignore
            failure_probability=model.failure_probability,  # type: ignore
            maintenance_hours=model.maintenance_hours,  # type: ignore
            failure_type=model.failure_type,  # type: ignore
            confidence=model.confidence,  # type: ignore
            model_version=model.model_version,  # type: ignore
            features_used=model.features_used,  # type: ignore
        )
