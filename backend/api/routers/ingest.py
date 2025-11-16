"""
Ingest Router - Hexagonal Architecture
Handles ingestion of raw telemetry and feature vectors with comprehensive error handling.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.dependencies import get_ingest_telemetry_use_case

# Get the global limiter from the infrastructure module
from infrastructure.rate_limiting import limiter
from application.use_cases import IngestTelemetryUseCase
from application.use_cases.ingest.ingest_telemetry_use_case import (
    FeatureIngestResult,
    RawIngestResult,
)
from models import FeatureVector, RawMeasurement
from models_errors import (
    ComputationException,
    ErrorCode,
    ResourceNotFoundException,
    ValidationException,
)

logger = logging.getLogger("aurumai")

router = APIRouter()

# Rate limiter for ingest endpoints


def _validate_raw_measurement(meas: RawMeasurement) -> None:
    """
    Validate raw measurement data.
    Raises ValidationException if invalid.
    """
    if not meas.machine_id or len(meas.machine_id.strip()) == 0:
        raise ValidationException(
            message="machine_id cannot be empty",
            field="machine_id",
            constraint="required",
            expected_format="Non-empty string",
        )

    if len(meas.metrics) == 0:
        raise ValidationException(
            message="metrics cannot be empty",
            field="metrics",
            constraint="required",
            expected_format="Non-empty dictionary",
        )

    # Validate that all metric values are numeric
    for key, value in meas.metrics.items():
        try:
            float(value)
        except (ValueError, TypeError) as exc:
            raise ValidationException(
                message=f"Metric '{key}' value must be numeric",
                field=f"metrics.{key}",
                constraint="type",
                provided_value=str(value),
                expected_format="Numeric value",
            ) from exc


def _validate_feature_vector(vec: FeatureVector) -> None:
    """
    Validate feature vector data.
    Raises ValidationException if invalid.
    """
    if not vec.machine_id or len(vec.machine_id.strip()) == 0:
        raise ValidationException(
            message="machine_id cannot be empty",
            field="machine_id",
            constraint="required",
            expected_format="Non-empty string",
        )

    if len(vec.features) == 0:
        raise ValidationException(
            message="features cannot be empty",
            field="features",
            constraint="required",
            expected_format="Non-empty dictionary",
        )

    # Validate that all feature values are numeric
    for key, value in vec.features.items():
        try:
            float(value)
        except (ValueError, TypeError) as exc:
            raise ValidationException(
                message=f"Feature '{key}' value must be numeric",
                field=f"features.{key}",
                constraint="type",
                provided_value=str(value),
                expected_format="Numeric value",
            ) from exc


@router.post("/raw")
async def ingest_raw(
    request: Request,
    meas: RawMeasurement,
    use_case: Annotated[IngestTelemetryUseCase, Depends(get_ingest_telemetry_use_case)],
) -> RawIngestResult:
    """
    Ingest raw telemetry data from IoT devices/Edge nodes.
    Uses hexagonal architecture with dependency injection.

    Args:
        meas: Raw measurement with machine_id, timestamp, and metrics dict.

    Returns:
        Result of ingestion including status and any warnings.

    Raises:
        ValidationException: If measurement data is invalid.
        ResourceNotFoundException: If machine not found.
        ComputationException: If ingestion fails.
    """
    # Rate limiting: 100 requests per minute for raw telemetry
    limiter.limit("100/minute")(request)

    # Validate input
    _validate_raw_measurement(meas)

    try:
        result = await use_case.execute_raw(
            machine_id=meas.machine_id,
            timestamp=meas.timestamp,
            metrics=meas.metrics,
        )
        logger.info(
            f"Raw telemetry ingested for machine {meas.machine_id}: {result['message']}"
        )
    except (ResourceNotFoundException, ValidationException):
        raise
    except ValueError as exc:
        logger.warning(f"Not found for {meas.machine_id}: {exc}")
        raise ResourceNotFoundException(
            message=f"Machine '{meas.machine_id}' not found or invalid",
            resource_type="machine",
            resource_id=meas.machine_id,
        ) from exc
    except ComputationException:
        raise
    except Exception as exc:
        logger.error(
            f"Unexpected error ingesting raw telemetry for {meas.machine_id}: "
            f"{type(exc).__name__}: {exc}"
        )
        raise ComputationException(
            message=f"Failed to ingest telemetry for machine '{meas.machine_id}'",
            error_code=ErrorCode.INGEST_ERROR,
        ) from exc
    else:
        return result


@router.post("/features")
async def ingest_features(
    request: Request,
    vec: FeatureVector,
    use_case: Annotated[IngestTelemetryUseCase, Depends(get_ingest_telemetry_use_case)],
) -> FeatureIngestResult:
    """
    Ingest feature-engineered data from Edge nodes.
    Uses hexagonal architecture with dependency injection.

    Args:
        vec: Feature vector with machine_id, timestamp, and features dict.

    Returns:
        Result of ingestion including status and any warnings.

    Raises:
        ValidationException: If feature data is invalid.
        ResourceNotFoundException: If machine not found.
        ComputationException: If ingestion fails.
    """
    # Rate limiting: 50 requests per minute for feature vectors
    limiter.limit("50/minute")(request)

    # Validate input
    _validate_feature_vector(vec)

    try:
        result = await use_case.execute_features(
            machine_id=vec.machine_id,
            timestamp=vec.timestamp,
            features=vec.features,
        )
        logger.info(
            f"Feature vector ingested for machine {vec.machine_id}: {result['message']}"
        )
    except (ResourceNotFoundException, ValidationException):
        raise
    except ValueError as exc:
        logger.warning(f"Not found for {vec.machine_id}: {exc}")
        raise ResourceNotFoundException(
            message=f"Machine '{vec.machine_id}' not found or invalid",
            resource_type="machine",
            resource_id=vec.machine_id,
        ) from exc
    except ComputationException:
        raise
    except Exception as exc:
        logger.error(
            f"Unexpected error ingesting features for {vec.machine_id}: {type(exc).__name__}: {exc}"
        )
        raise ComputationException(
            message=f"Failed to ingest features for machine '{vec.machine_id}'",
            error_code=ErrorCode.INVALID_FEATURES,
        ) from exc
    else:
        return result
