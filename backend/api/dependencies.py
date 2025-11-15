"""
FastAPI Dependency Injection Configuration
Provides factory functions for use cases with their dependencies
"""

from typing import TYPE_CHECKING, Annotated, Any

from fastapi import Depends

from application.use_cases import (
    CalculateESGUseCase,
    GetMachineMetricsUseCase,
    IngestTelemetryUseCase,
    RunPredictionUseCase,
)
from domain.services.esg_service_impl import ESGServiceImpl
from domain.services.ml_service_impl import MLServiceImpl
from infrastructure.adapters.output.postgres import (
    PostgresESGRepository,
    PostgresMachineRepository,
    PostgresMeasurementRepository,
    PostgresPredictionRepository,
)
from infrastructure.db.sqlite_config import get_db

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
else:
    AsyncSession = Any


DbSession = Annotated[AsyncSession, Depends(get_db)]


# Service instances (stateless, can be reused)
ml_service = MLServiceImpl()
esg_service = ESGServiceImpl()


async def get_ingest_telemetry_use_case(
    db: DbSession,
) -> IngestTelemetryUseCase:
    """
    Provides IngestTelemetryUseCase with dependencies.
    """
    machine_repo = PostgresMachineRepository(db)
    measurement_repo = PostgresMeasurementRepository(db)

    return IngestTelemetryUseCase(
        machine_repo=machine_repo,
        measurement_repo=measurement_repo,
    )


async def get_run_prediction_use_case(
    db: DbSession,
) -> RunPredictionUseCase:
    """
    Provides RunPredictionUseCase with dependencies.
    """
    machine_repo = PostgresMachineRepository(db)
    measurement_repo = PostgresMeasurementRepository(db)
    prediction_repo = PostgresPredictionRepository(db)

    return RunPredictionUseCase(
        machine_repo=machine_repo,
        measurement_repo=measurement_repo,
        prediction_repo=prediction_repo,
        ml_service=ml_service,
    )


async def get_calculate_esg_use_case(
    db: DbSession,
) -> CalculateESGUseCase:
    """
    Provides CalculateESGUseCase with dependencies.
    """
    machine_repo = PostgresMachineRepository(db)
    measurement_repo = PostgresMeasurementRepository(db)
    esg_repo = PostgresESGRepository(db)

    return CalculateESGUseCase(
        machine_repo=machine_repo,
        measurement_repo=measurement_repo,
        esg_repo=esg_repo,
        esg_service=esg_service,
    )


async def get_machine_metrics_use_case(
    db: DbSession,
) -> GetMachineMetricsUseCase:
    """
    Provides GetMachineMetricsUseCase with dependencies.
    """
    machine_repo = PostgresMachineRepository(db)
    measurement_repo = PostgresMeasurementRepository(db)
    prediction_repo = PostgresPredictionRepository(db)
    esg_repo = PostgresESGRepository(db)

    return GetMachineMetricsUseCase(
        machine_repo=machine_repo,
        measurement_repo=measurement_repo,
        prediction_repo=prediction_repo,
        esg_repo=esg_repo,
    )


# Individual repository providers (for cases where direct access is needed)


async def get_machine_repository(
    db: DbSession,
) -> PostgresMachineRepository:
    """Provides MachineRepository instance"""
    return PostgresMachineRepository(db)


async def get_measurement_repository(
    db: DbSession,
) -> PostgresMeasurementRepository:
    """Provides MeasurementRepository instance"""
    return PostgresMeasurementRepository(db)


async def get_prediction_repository(
    db: DbSession,
) -> PostgresPredictionRepository:
    """Provides PredictionRepository instance"""
    return PostgresPredictionRepository(db)


async def get_esg_repository(
    db: DbSession,
) -> PostgresESGRepository:
    """Provides ESGRepository instance"""
    return PostgresESGRepository(db)
