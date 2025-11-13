"""
FastAPI Dependency Injection Configuration
Provides factory functions for use cases with their dependencies
"""
from typing import AsyncGenerator, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
    from fastapi import Depends
else:
    AsyncSession = Any

    # Fallback stub for editors/linters that don't have FastAPI installed.
    # At runtime with FastAPI installed, the real Depends will be used (imported under TYPE_CHECKING only for type checkers).
    def Depends(dependency=None):
        return dependency
from infrastructure.db.postgres_config import get_db
from infrastructure.adapters.output.postgres import (
    PostgresMachineRepository,
    PostgresMeasurementRepository,
    PostgresPredictionRepository,
    PostgresESGRepository,
)
from application.use_cases import (
    IngestTelemetryUseCase,
    RunPredictionUseCase,
    CalculateESGUseCase,
    GetMachineMetricsUseCase,
)
from domain.services.ml_service_impl import MLServiceImpl
from domain.services.esg_service_impl import ESGServiceImpl


# Service instances (stateless, can be reused)
ml_service = MLServiceImpl()
esg_service = ESGServiceImpl()


# Dependency providers for use cases

async def get_ingest_telemetry_use_case(
    db: AsyncSession = Depends(get_db),
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
    db: AsyncSession = Depends(get_db),
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
    db: AsyncSession = Depends(get_db),
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
    db: AsyncSession = Depends(get_db),
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
    db: AsyncSession = Depends(get_db),
) -> PostgresMachineRepository:
    """Provides MachineRepository instance"""
    return PostgresMachineRepository(db)


async def get_measurement_repository(
    db: AsyncSession = Depends(get_db),
) -> PostgresMeasurementRepository:
    """Provides MeasurementRepository instance"""
    return PostgresMeasurementRepository(db)


async def get_prediction_repository(
    db: AsyncSession = Depends(get_db),
) -> PostgresPredictionRepository:
    """Provides PredictionRepository instance"""
    return PostgresPredictionRepository(db)


async def get_esg_repository(
    db: AsyncSession = Depends(get_db),
) -> PostgresESGRepository:
    """Provides ESGRepository instance"""
    return PostgresESGRepository(db)
