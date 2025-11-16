"""
Machines Router - Hexagonal Architecture
Handles machine information and metrics retrieval with comprehensive error handling.
"""

import logging
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends

from api.dependencies import get_machine_metrics_use_case
from application.use_cases import GetMachineMetricsUseCase
from models import MachineInfo, MachineMetrics, PredictionResponse
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

    # Only alphanumeric, dash, underscore allowed
    if not all(c.isalnum() or c in "-_" for c in machine_id):
        raise ValidationException(
            message="machine_id contains invalid characters",
            field="machine_id",
            constraint="pattern",
            provided_value=machine_id,
            expected_format="Only alphanumeric, dash, underscore allowed",
        )


@router.get("/", response_model=list[MachineInfo])
async def list_machines(
    use_case: Annotated[GetMachineMetricsUseCase, Depends(get_machine_metrics_use_case)],
) -> list[MachineInfo]:
    """
    List all available machines.
    Uses hexagonal architecture with dependency injection.

    Returns:
        List of all registered machines with basic info.

    Raises:
        ComputationException: If retrieving machines fails.
    """
    try:
        machines = await use_case.get_all_machines()

        return [
            MachineInfo(
                machine_id=m["machine_id"],
                machine_type=m["machine_type"],
                site=m["location"],
                status="operational" if m["operational"] else "down",
                commissioned_date=None,
            )
            for m in machines
        ]

    except ComputationException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error retrieving machines: {type(exc).__name__}: {exc}")
        raise ComputationException(
            message="Failed to retrieve machines list. Please try again.",
            error_code=ErrorCode.DATABASE_ERROR,
        ) from exc


@router.get("/{machine_id}/metrics", response_model=MachineMetrics)
async def get_machine_metrics(
    machine_id: str,
    use_case: Annotated[GetMachineMetricsUseCase, Depends(get_machine_metrics_use_case)],
) -> MachineMetrics:
    """
    Get current metrics and status for a specific machine.
    Uses hexagonal architecture with dependency injection.

    Args:
        machine_id: The ID of the machine to retrieve metrics for.

    Returns:
        Current machine metrics including status, measurements, and predictions.

    Raises:
        ValidationException: If machine_id is invalid.
        ResourceNotFoundException: If machine is not found.
        ComputationException: If retrieving metrics fails.
    """
    # Validate input
    _validate_machine_id(machine_id)

    try:
        metrics = await use_case.execute(machine_id)

        # Extract latest measurement
        last_timestamp = None
        latest_metrics: dict[str, Any] = {}
        if metrics.get("latest_measurement"):
            try:
                last_timestamp = datetime.fromisoformat(metrics["latest_measurement"]["timestamp"])
                latest_metrics = metrics["latest_measurement"]["metrics"]
            except (ValueError, KeyError) as exc:
                logger.warning(f"Invalid measurement data for {machine_id}: {exc}")
                last_timestamp = None

        # Extract prediction
        prediction: PredictionResponse | None = None
        if (
            metrics.get("latest_prediction")
            and metrics["latest_prediction"].get("risk_score") is not None
        ):
            try:
                pred_data = metrics["latest_prediction"]
                prediction = PredictionResponse(
                    machine_id=machine_id,
                    timestamp=datetime.fromisoformat(pred_data["timestamp"]),
                    risk_score=pred_data["risk_score"],
                    failure_probability=pred_data["failure_probability"],
                    confidence=pred_data.get("confidence", 0.0),
                    next_maintenance_hours=pred_data.get("maintenance_hours"),
                )
            except (ValueError, KeyError) as exc:
                logger.warning(f"Invalid prediction data for {machine_id}: {exc}")
                prediction = None

        # Count alerts based on risk score
        alerts_count = 0
        if prediction and prediction.risk_score > 0.6:
            alerts_count = 1
        elif prediction and prediction.risk_score > 0.4:
            alerts_count = 1

        return MachineMetrics(
            machine_id=machine_id,
            current_status=("operational" if metrics["machine"]["operational"] else "down"),
            last_measurement=last_timestamp,
            metrics=latest_metrics,
            alerts_count=alerts_count,
            predictions=prediction,
        )

    except (ResourceNotFoundException, ValidationException):
        raise
    except ValueError as exc:
        logger.warning(f"Not found or validation error for {machine_id}: {exc}")
        raise ResourceNotFoundException(
            message=f"Machine '{machine_id}' not found",
            resource_type="machine",
            resource_id=machine_id,
        ) from exc
    except ComputationException:
        raise
    except Exception as exc:
        logger.error(
            f"Unexpected error retrieving metrics for {machine_id}: {type(exc).__name__}: {exc}"
        )
        raise ComputationException(
            message=f"Failed to retrieve metrics for machine '{machine_id}'",
            error_code=ErrorCode.DATABASE_ERROR,
        ) from exc
