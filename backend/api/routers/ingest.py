"""
Ingest Router - Hexagonal Architecture
Handles ingestion of raw telemetry and feature vectors
"""

from fastapi import APIRouter, HTTPException, Depends
from models import RawMeasurement, FeatureVector
from api.dependencies import get_ingest_telemetry_use_case
from application.use_cases import IngestTelemetryUseCase

router = APIRouter()


@router.post("/raw")
async def ingest_raw(
    meas: RawMeasurement,
    use_case: IngestTelemetryUseCase = Depends(get_ingest_telemetry_use_case),
):
    """
    Ingest raw telemetry data from IoT devices/Edge nodes.
    Uses hexagonal architecture with dependency injection.
    """
    try:
        result = await use_case.execute_raw(
            machine_id=meas.machine_id,
            timestamp=meas.timestamp,
            metrics=meas.metrics,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/features")
async def ingest_features(
    vec: FeatureVector,
    use_case: IngestTelemetryUseCase = Depends(get_ingest_telemetry_use_case),
):
    """
    Ingest feature-engineered data from Edge nodes.
    Uses hexagonal architecture with dependency injection.
    """
    try:
        result = await use_case.execute_features(
            machine_id=vec.machine_id,
            timestamp=vec.timestamp,
            features=vec.features,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
