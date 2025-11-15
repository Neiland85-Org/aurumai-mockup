"""
Machines Router - Hexagonal Architecture
Handles machine information and metrics retrieval
"""


from fastapi import APIRouter, HTTPException, Depends


from typing import List
from models import MachineInfo, MachineMetrics, PredictionResponse
from api.dependencies import get_machine_metrics_use_case
from application.use_cases import GetMachineMetricsUseCase
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=List[MachineInfo])
async def list_machines(
    use_case: GetMachineMetricsUseCase = Depends(get_machine_metrics_use_case),
):
    """
    List all available machines.
    Uses hexagonal architecture with dependency injection.
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{machine_id}/metrics", response_model=MachineMetrics)
async def get_machine_metrics(
    machine_id: str,
    use_case: GetMachineMetricsUseCase = Depends(get_machine_metrics_use_case),
):
    """
    Get current metrics and status for a specific machine.
    Uses hexagonal architecture with dependency injection.
    """
    try:
        metrics = await use_case.execute(machine_id)

        # Extract latest measurement
        last_timestamp = None
        latest_metrics = {}
        if metrics.get("latest_measurement"):
            last_timestamp = datetime.fromisoformat(
                metrics["latest_measurement"]["timestamp"]
            )
            latest_metrics = metrics["latest_measurement"]["metrics"]

        # Extract prediction
        prediction = None
        if (
            metrics.get("latest_prediction")
            and metrics["latest_prediction"]["risk_score"] is not None
        ):
            pred_data = metrics["latest_prediction"]
            prediction = PredictionResponse(
                machine_id=machine_id,
                timestamp=datetime.fromisoformat(pred_data["timestamp"]),
                risk_score=pred_data["risk_score"],
                failure_probability=pred_data["failure_probability"],
                confidence=pred_data.get("confidence", 0.0),
                next_maintenance_hours=pred_data["maintenance_hours"],
            )

        # Count alerts based on risk score
        alerts_count = 0
        if prediction and prediction.risk_score > 0.6:
            alerts_count = 1
        elif prediction and prediction.risk_score > 0.4:
            alerts_count = 1

        return MachineMetrics(
            machine_id=machine_id,
            current_status=(
                "operational" if metrics["machine"]["operational"] else "down"
            ),
            last_measurement=last_timestamp,
            metrics=latest_metrics,
            alerts_count=alerts_count,
            predictions=prediction,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
