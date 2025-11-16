"""
Prediction Mock Router - For demo/development without database
Provides simulated predictive maintenance data.
"""

import logging
import random
from typing import Any

from fastapi import APIRouter, Query

logger = logging.getLogger("aurumai")

router = APIRouter()

# Mock machine IDs (should match machines_mock.py)
VALID_MACHINE_IDS = {"CNC-001", "CNC-002", "PRESS-001", "WELD-001", "PACK-001"}


def _generate_mock_prediction(machine_id: str) -> dict[str, Any]:
    """Generate realistic mock prediction data for a machine."""
    # Base risk depends on machine type
    if "CNC" in machine_id:
        base_risk = 0.15  # Low risk
    elif "PRESS" in machine_id:
        base_risk = 0.45  # Medium risk
    elif "WELD" in machine_id:
        base_risk = 0.75  # High risk (matches offline status)
    else:  # PACK
        base_risk = 0.25  # Low-medium risk

    # Add variation
    risk_score = max(0.0, min(1.0, base_risk + random.uniform(-0.1, 0.1)))

    # Failure probability is usually lower than risk score
    failure_prob = risk_score * random.uniform(0.6, 0.9)

    # Maintenance hours based on risk
    if risk_score > 0.6:
        maintenance_hours = random.randint(24, 72)  # Soon
    elif risk_score > 0.3:
        maintenance_hours = random.randint(100, 300)  # Medium term
    else:
        maintenance_hours = random.randint(400, 800)  # Long term

    return {
        "risk_score": round(risk_score, 3),
        "failure_probability": round(failure_prob, 3),
        "maintenance_hours": maintenance_hours,
        "confidence": round(random.uniform(0.75, 0.95), 2),
    }


@router.get("")
async def predict_mock(
    machine_id: str = Query(..., description="Machine ID"),
) -> dict[str, Any]:
    """
    Get mock predictive maintenance analysis for a machine.
    Returns simulated data - no database required.

    Args:
        machine_id: The machine to get predictions for.

    Returns:
        Mock prediction with risk score, failure probability, and maintenance schedule.
    """
    logger.info(
        f"🔧 Using MOCK predict endpoint for '{machine_id}' (database not available)"
    )

    # Validate machine exists
    if machine_id not in VALID_MACHINE_IDS:
        from models_errors import ResourceNotFoundException

        raise ResourceNotFoundException(
            message=f"Machine '{machine_id}' not found in mock data",
            resource_type="machine",
            resource_id=machine_id,
        )

    # Generate mock prediction
    prediction = _generate_mock_prediction(machine_id)

    return {
        "machine_id": machine_id,
        "risk_score": prediction["risk_score"],
        "failure_probability": prediction["failure_probability"],
        "maintenance_hours": prediction["maintenance_hours"],
        "confidence": prediction["confidence"],
        "recommendations": [
            (
                f"Monitor {machine_id} for unusual vibrations"
                if prediction["risk_score"] > 0.5
                else f"{machine_id} operating normally"
            ),
            (
                "Schedule maintenance"
                if prediction["maintenance_hours"] < 100
                else "Continue regular monitoring"
            ),
        ],
    }
