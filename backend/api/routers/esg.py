"""
ESG Router - Hexagonal Architecture
Handles ESG/Carbon emission calculations and reporting
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from models import ESGResponse
from api.dependencies import get_calculate_esg_use_case
from application.use_cases import CalculateESGUseCase

router = APIRouter()


@router.get("/current", response_model=ESGResponse)
async def get_current_esg(
    machine_id: str = Query(..., description="Machine ID"),
    use_case: CalculateESGUseCase = Depends(get_calculate_esg_use_case),
):
    """
    Calculate current ESG/Carbon metrics for a machine.
    Uses hexagonal architecture with dependency injection.
    """
    try:
        esg_record = await use_case.execute(machine_id)

        return ESGResponse(
            machine_id=esg_record.machine_id,
            timestamp=esg_record.timestamp,
            co2eq_instant=esg_record.instant_co2eq_kg,
            co2eq_total=esg_record.cumulative_co2eq_kg,
            fuel_rate_lh=esg_record.fuel_rate_lh,
            kwh=esg_record.power_consumption_kw,
            scope=esg_record.metadata.get("dominant_scope", "scope1"),
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{machine_id}")
async def get_esg_history(
    machine_id: str,
    limit: int = Query(default=100, le=500),
    use_case: CalculateESGUseCase = Depends(get_calculate_esg_use_case),
):
    """
    Get ESG history for a machine.
    Uses hexagonal architecture with dependency injection.
    """
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

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_esg_summary(
    use_case: CalculateESGUseCase = Depends(get_calculate_esg_use_case),
):
    """
    Get aggregated ESG summary across all machines.
    Uses hexagonal architecture with dependency injection.
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
