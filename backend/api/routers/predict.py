"""
Prediction Router - Hexagonal Architecture
Handles ML predictions for predictive maintenance with comprehensive error handling.
"""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_run_prediction_use_case
from application.use_cases import RunPredictionUseCase
from models import PredictionResponse
from models_errors import (
    ComputationException,
    ErrorCode,
    ResourceNotFoundException,
    ValidationException,
)

logger = logging.getLogger("aurumai")

router = APIRouter()


def _validate_machine_id(machine_id: str) -> None:
    """
    Validate machine_id format.
    Raises ValidationException if invalid.
    """
    if not machine_id or len(machine_id.strip()) == 0:
        raise ValidationException(
            message="machine_id cannot be empty",
            field="machine_id",
            constraint="required",
            expected_format="Non-empty string",
        )

    if len(machine_id) > 255:
        raise ValidationException(
            message="machine_id is too long (max 255 characters)",
            field="machine_id",
            constraint="max_length",
            provided_value=machine_id[:50] + "...",
            expected_format="Max 255 characters",
        )


def _validate_limit(limit: int) -> None:
    """
    Validate limit parameter.
    Raises ValidationException if invalid.
    """
    if limit < 1:
        raise ValidationException(
            message="limit must be at least 1",
            field="limit",
            constraint="minimum",
            provided_value=str(limit),
            expected_format="Integer >= 1",
        )

    if limit > 200:
        raise ValidationException(
            message="limit must not exceed 200",
            field="limit",
            constraint="maximum",
            provided_value=str(limit),
            expected_format="Integer <= 200",
        )


@router.post("/", response_model=PredictionResponse)
async def predict(
    use_case: Annotated[RunPredictionUseCase, Depends(get_run_prediction_use_case)],
    machine_id: str = Query(..., description="Machine ID to predict", min_length=1),
) -> PredictionResponse:
    """
    Run predictive maintenance model for a specific machine.
    Uses hexagonal architecture with dependency injection.

    Args:
        machine_id: The ID of the machine to predict.

    Returns:
        Prediction result with risk score and maintenance recommendations.

    Raises:
        ValidationException: If machine_id is invalid.
        ResourceNotFoundException: If machine or prediction data not found.
        ComputationException: If prediction model fails.
    """
    # Validate input
    _validate_machine_id(machine_id)

    try:
        prediction = await use_case.execute(machine_id)

        return PredictionResponse(
            machine_id=prediction.machine_id,
            timestamp=prediction.timestamp,
            risk_score=prediction.risk_score,
            failure_probability=prediction.failure_probability,
            confidence=(prediction.confidence if prediction.confidence is not None else 0.85),
            next_maintenance_hours=prediction.maintenance_hours,
        )

    except (ResourceNotFoundException, ValidationException):
        raise
    except ValueError as exc:
        logger.warning(f"Not found for {machine_id}: {exc}")
        raise ResourceNotFoundException(
            message=f"No prediction available for machine '{machine_id}'",
            resource_type="prediction",
            resource_id=machine_id,
        ) from exc
    except ComputationException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error predicting {machine_id}: {type(exc).__name__}: {exc}")
        raise ComputationException(
            message=f"Failed to generate prediction for machine '{machine_id}'",
            error_code=ErrorCode.PREDICTION_FAILED,
        ) from exc


@router.get("/history/{machine_id}")
async def get_prediction_history(
    machine_id: str,
    use_case: Annotated[RunPredictionUseCase, Depends(get_run_prediction_use_case)],
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
) -> dict[str, Any]:
    """
    Get prediction history for a machine.
    Uses hexagonal architecture with dependency injection.

    Args:
        machine_id: The machine to get history for.
        limit: Maximum number of records (1-200, default 50).

    Returns:
        Dictionary with machine_id and list of historical predictions.

    Raises:
        ValidationException: If parameters are invalid.
        ResourceNotFoundException: If machine or history not found.
        ComputationException: If retrieval fails.
    """
    # Validate inputs
    _validate_machine_id(machine_id)
    _validate_limit(limit)

    try:
        predictions = await use_case.get_history(machine_id, limit)

        return {
            "machine_id": machine_id,
            "predictions": [
                {
                    "timestamp": p.timestamp.isoformat(),
                    "risk_score": p.risk_score,
                    "failure_probability": p.failure_probability,
                    "confidence": p.confidence,
                    "maintenance_hours": p.maintenance_hours,
                    "failure_type": p.failure_type,
                }
                for p in predictions
            ],
        }

    except (ResourceNotFoundException, ValidationException):
        raise
    except ValueError as exc:
        logger.warning(f"Not found for {machine_id}: {exc}")
        raise ResourceNotFoundException(
            message=f"No prediction history found for machine '{machine_id}'",
            resource_type="machine",
            resource_id=machine_id,
        ) from exc
    except ComputationException:
        raise
    except Exception as exc:
        logger.error(
            f"Unexpected error retrieving history for {machine_id}: {type(exc).__name__}: {exc}"
        )
        raise ComputationException(
            message=f"Failed to retrieve prediction history for '{machine_id}'",
            error_code=ErrorCode.DATABASE_ERROR,
        ) from exc
