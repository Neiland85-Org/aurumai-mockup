"""
ESG Router - Hexagonal Architecture
Handles ESG/Carbon emission calculations and reporting with comprehensive error handling.
"""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_calculate_esg_use_case
from application.use_cases import CalculateESGUseCase
from models import ESGResponse
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

    if limit > 500:
        raise ValidationException(
            message="limit must not exceed 500",
            field="limit",
            constraint="maximum",
            provided_value=str(limit),
            expected_format="Integer <= 500",
        )


@router.get("/current", response_model=ESGResponse)
async def get_current_esg(
    use_case: Annotated[CalculateESGUseCase, Depends(get_calculate_esg_use_case)],
    machine_id: str = Query(..., description="Machine ID", min_length=1),
) -> ESGResponse:
    """
    Calculate current ESG/Carbon metrics for a machine.
    Uses hexagonal architecture with dependency injection.
    
    Args:
        machine_id: The machine to calculate ESG for.
        
    Returns:
        Current ESG metrics including CO2 emissions and fuel consumption.
        
    Raises:
        ValidationException: If machine_id is invalid.
        ResourceNotFoundException: If machine or ESG data not found.
        ComputationException: If calculation fails.
    """
    # Validate input
    _validate_machine_id(machine_id)

    try:
        esg_record = await use_case.execute(machine_id)

        return ESGResponse(
            machine_id=esg_record.machine_id,
            timestamp=esg_record.timestamp,
            instant_co2eq_kg=esg_record.instant_co2eq_kg,
            cumulative_co2eq_kg=esg_record.cumulative_co2eq_kg,
            fuel_rate_lh=esg_record.fuel_rate_lh,
            kwh=esg_record.power_consumption_kw,
            scope=esg_record.metadata.get("dominant_scope", "scope1"),
        )

    except (ResourceNotFoundException, ValidationException):
        raise
    except ValueError as exc:
        logger.warning(f"Not found or validation error for {machine_id}: {exc}")
        raise ResourceNotFoundException(
            message=f"No ESG data available for machine '{machine_id}'",
            resource_type="esg",
            resource_id=machine_id,
        ) from exc
    except ComputationException:
        raise
    except Exception as exc:
        logger.error(
            f"Unexpected error calculating ESG for {machine_id}: {type(exc).__name__}: {exc}"
        )
        raise ComputationException(
            message=f"Failed to calculate ESG metrics for '{machine_id}'",
            error_code=ErrorCode.ESG_CALCULATION_ERROR,
        ) from exc


@router.get("/history/{machine_id}")
async def get_esg_history(
    machine_id: str,
    use_case: Annotated[CalculateESGUseCase, Depends(get_calculate_esg_use_case)],
    limit: int = Query(default=100, ge=1, le=500, description="Max records to return"),
) -> dict[str, Any]:
    """
    Get ESG history for a machine.
    Uses hexagonal architecture with dependency injection.
    
    Args:
        machine_id: The machine to get ESG history for.
        limit: Maximum number of records (1-500, default 100).
        
    Returns:
        Dictionary with machine_id and list of historical ESG records.
        
    Raises:
        ValidationException: If parameters are invalid.
        ResourceNotFoundException: If machine or history not found.
        ComputationException: If retrieval fails.
    """
    # Validate inputs
    _validate_machine_id(machine_id)
    _validate_limit(limit)

    try:
        records = await use_case.get_history(machine_id, limit)

        return {
            "machine_id": machine_id,
            "records": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "co2eq_instant": r.instant_co2eq_kg,
                    "co2eq_total": r.cumulative_co2eq_kg,
                    "fuel_rate_lh": r.fuel_rate_lh,
                    "kwh": r.power_consumption_kw,
                    "scope": r.metadata.get("dominant_scope"),
                }
                for r in records
            ],
        }

    except (ResourceNotFoundException, ValidationException):
        raise
    except ValueError as exc:
        logger.warning(f"Not found for {machine_id}: {exc}")
        raise ResourceNotFoundException(
            message=f"No ESG history found for machine '{machine_id}'",
            resource_type="machine",
            resource_id=machine_id,
        ) from exc
    except ComputationException:
        raise
    except Exception as exc:
        logger.error(
            f"Unexpected error retrieving ESG history for {machine_id}: {type(exc).__name__}: {exc}"
        )
        raise ComputationException(
            message=f"Failed to retrieve ESG history for '{machine_id}'",
            error_code=ErrorCode.DATABASE_ERROR,
        ) from exc


@router.get("/summary")
async def get_esg_summary(
    use_case: Annotated[CalculateESGUseCase, Depends(get_calculate_esg_use_case)],
) -> dict[str, Any]:
    """
    Get aggregated ESG summary across all machines.
    Uses hexagonal architecture with dependency injection.
    
    Returns:
        Dictionary with total emissions and per-machine breakdown.
        
    Raises:
        ComputationException: If summary calculation fails.
    """
    try:
        summary = await use_case.get_summary()

        return {
            "total_co2eq_kg": summary["total_cumulative_co2eq_kg"],
            "total_co2eq_tons": summary["total_cumulative_co2eq_kg"] / 1000,
            "machines_count": summary["total_machines"],
            "monitored_machines": summary["monitored_machines"],
            "machines": summary["machines"],
        }

    except ComputationException:
        raise
    except Exception as exc:
        logger.error(
            f"Unexpected error calculating ESG summary: {type(exc).__name__}: {exc}"
        )
        raise ComputationException(
            message="Failed to calculate ESG summary",
            error_code=ErrorCode.ESG_CALCULATION_ERROR,
        ) from exc
