"""
Prediction Router - Hexagonal Architecture
Handles ML predictions for predictive maintenance
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from models import PredictionResponse
from api.dependencies import get_run_prediction_use_case
from application.use_cases import RunPredictionUseCase

router = APIRouter()


@router.post("/", response_model=PredictionResponse)
async def predict(
    machine_id: str = Query(..., description="Machine ID to predict"),
    use_case: RunPredictionUseCase = Depends(get_run_prediction_use_case),
):
    """
    Run predictive maintenance model for a specific machine.
    Uses hexagonal architecture with dependency injection.
    """
    try:
        prediction = await use_case.execute(machine_id)

        return PredictionResponse(
            machine_id=prediction.machine_id,
            timestamp=prediction.timestamp,
            risk_score=prediction.risk_score,
            failure_probability=prediction.failure_probability,
            confidence=prediction.confidence,
            next_maintenance_hours=prediction.maintenance_hours,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{machine_id}")
async def get_prediction_history(
    machine_id: str,
    limit: int = Query(default=50, le=200),
    use_case: RunPredictionUseCase = Depends(get_run_prediction_use_case),
):
    """
    Get prediction history for a machine.
    Uses hexagonal architecture with dependency injection.
    """
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

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
