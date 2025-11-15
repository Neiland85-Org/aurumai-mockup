"""
Concrete PostgreSQL implementation of IPredictionRepository
"""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.prediction import Prediction
from domain.repositories.prediction_repository import IPredictionRepository
from infrastructure.db.models import PredictionModel


class PostgresPredictionRepository(IPredictionRepository):
    """PostgreSQL implementation of prediction repository"""

    def __init__(self, session: AsyncSession) -> None:
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
        raw_features = getattr(model, "features_used", {}) or {}
        if not isinstance(raw_features, dict):
            raw_features = dict(raw_features)
        features_used: Dict[str, float] = {}
        for key, value in raw_features.items():
            if isinstance(key, bytes):
                key = key.decode()
            try:
                features_used[str(key)] = float(value)
            except (TypeError, ValueError):
                continue
        return Prediction(
            machine_id=str(getattr(model, "machine_id", "")),
            timestamp=getattr(model, "timestamp", datetime.utcnow()),
            risk_score=float(getattr(model, "risk_score", 0.0)),
            failure_probability=float(getattr(model, "failure_probability", 0.0)),
            maintenance_hours=int(getattr(model, "maintenance_hours", 0)),
            failure_type=getattr(model, "failure_type", None),
            confidence=float(getattr(model, "confidence", 0.0))
            if getattr(model, "confidence", None) is not None
            else None,
            model_version=str(getattr(model, "model_version", "")),
            features_used=features_used,
        )
