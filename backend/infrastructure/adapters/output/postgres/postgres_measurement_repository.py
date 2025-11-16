"""
Concrete PostgreSQL implementation of IMeasurementRepository
"""

from datetime import datetime, timezone
from typing import Dict, List, Mapping, Optional, Sequence
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.measurement import FeatureVector, RawMeasurement
from domain.repositories.measurement_repository import IMeasurementRepository
from domain.value_objects import Measurement, TimeSeriesPoint
from infrastructure.db.models import FeatureModel, RawMeasurementModel


class PostgresMeasurementRepository(IMeasurementRepository):
    """PostgreSQL implementation of measurement repository"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_raw_measurement(self, measurement: RawMeasurement) -> RawMeasurement:
        """Save raw telemetry measurement"""
        model = RawMeasurementModel(
            machine_id=measurement.machine_id,
            timestamp=measurement.timestamp,
            metrics=measurement.metrics,
        )
        self.session.add(model)
        await self.session.flush()

        return self._raw_model_to_entity(model)

    async def save_feature_vector(self, features: FeatureVector) -> FeatureVector:
        """Save engineered features"""
        model = FeatureModel(
            machine_id=features.machine_id,
            timestamp=features.timestamp,
            features=features.features,
        )
        self.session.add(model)
        await self.session.flush()

        return self._feature_model_to_entity(model)

    async def get_latest_raw_measurement(self, machine_id: str) -> Optional[RawMeasurement]:
        """Get latest raw measurement for machine"""
        stmt = (
            select(RawMeasurementModel)
            .where(RawMeasurementModel.machine_id == machine_id)
            .order_by(desc(RawMeasurementModel.timestamp))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return self._raw_model_to_entity(model)
        return None

    async def get_latest_features(self, machine_id: str) -> Optional[FeatureVector]:
        """Get latest feature vector for machine"""
        stmt = (
            select(FeatureModel)
            .where(FeatureModel.machine_id == machine_id)
            .order_by(desc(FeatureModel.timestamp))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return self._feature_model_to_entity(model)
        return None

    async def get_raw_measurements_range(
        self,
        machine_id: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[RawMeasurement]:
        """Get raw measurements within time range"""
        stmt = (
            select(RawMeasurementModel)
            .where(
                RawMeasurementModel.machine_id == machine_id,
                RawMeasurementModel.timestamp >= start_time,
                RawMeasurementModel.timestamp <= end_time,
            )
            .order_by(RawMeasurementModel.timestamp)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._raw_model_to_entity(model) for model in models]

    async def get_features_range(
        self,
        machine_id: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[FeatureVector]:
        """Get feature vectors within time range"""
        stmt = (
            select(FeatureModel)
            .where(
                FeatureModel.machine_id == machine_id,
                FeatureModel.timestamp >= start_time,
                FeatureModel.timestamp <= end_time,
            )
            .order_by(FeatureModel.timestamp)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._feature_model_to_entity(model) for model in models]

    def _raw_model_to_entity(self, model: RawMeasurementModel) -> RawMeasurement:
        """Convert SQLAlchemy model to domain entity"""
        # Conversión segura de machine_id, timestamp y metrics
        machine_id = str(getattr(model, "machine_id", ""))
        ts = getattr(model, "timestamp", None)
        if ts is not None and hasattr(ts, "value"):
            ts = ts.value
        if ts is None:
            ts = datetime.now(timezone.utc)
        metrics = getattr(model, "metrics", {})
        metrics_dict: Dict[str, float] = {}
        if isinstance(metrics, dict):
            for k, v in metrics.items():
                key = k.decode() if isinstance(k, bytes) else str(k)
                try:
                    value = float(v.decode() if isinstance(v, bytes) else v)
                except Exception:
                    value = None
                if value is not None:
                    metrics_dict[key] = value
        return RawMeasurement(
            machine_id=machine_id,
            timestamp=ts,
            metrics=metrics_dict,
        )

    def _feature_model_to_entity(self, model: FeatureModel) -> FeatureVector:
        """Convert SQLAlchemy model to domain entity"""
        # Conversión segura de machine_id, timestamp y features
        machine_id = str(getattr(model, "machine_id", ""))
        ts = getattr(model, "timestamp", None)
        if ts is not None and hasattr(ts, "value"):
            ts = ts.value
        if ts is None:
            ts = datetime.now(timezone.utc)
        features = getattr(model, "features", {})
        features_dict: Dict[str, float] = {}
        if isinstance(features, dict):
            for k, v in features.items():
                key = k.decode() if isinstance(k, bytes) else str(k)
                try:
                    value = float(v.decode() if isinstance(v, bytes) else v)
                except Exception:
                    value = None
                if value is not None:
                    features_dict[key] = value
        return FeatureVector(
            machine_id=machine_id,
            timestamp=ts,
            features=features_dict,
        )

    async def save_measurement(self, measurement: Measurement) -> bool:
        raise NotImplementedError

    async def save_batch(self, measurements: Sequence[Measurement]) -> int:
        raise NotImplementedError

    async def save_timeseries_point(self, point: TimeSeriesPoint) -> bool:
        raise NotImplementedError

    async def get_latest(
        self, machine_id: UUID, metric_names: Sequence[str], limit: int = 100
    ) -> Sequence[Mapping[str, float]]:
        raise NotImplementedError

    async def get_range(
        self,
        machine_id: UUID,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
    ) -> Sequence[Mapping[str, float]]:
        raise NotImplementedError

    async def get_aggregated(
        self,
        machine_id: UUID,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        interval_seconds: int,
    ) -> Sequence[Mapping[str, float]]:
        raise NotImplementedError
