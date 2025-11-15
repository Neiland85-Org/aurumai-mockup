"""
Simple Predict Router for Development
Returns mock predictions without ML dependencies
"""

from fastapi import APIRouter, Query
from typing import Dict, Any
from datetime import datetime
import random

router = APIRouter()


@router.get("/")
async def predict(machine_id: str = Query(...)) -> Dict[str, Any]:
    """Get prediction for a machine"""
    
    # Generate mock prediction
    failure_probability = round(random.uniform(0.05, 0.25), 3)
    
    return {
        "machine_id": machine_id,
        "timestamp": datetime.utcnow().isoformat(),
        "prediction": {
            "failure_probability": failure_probability,
            "risk_level": "low" if failure_probability < 0.15 else "medium",
            "time_to_failure_hours": round(random.uniform(100, 500), 1),
            "confidence": round(random.uniform(0.75, 0.95), 2),
        },
        "recommendations": [
            "Schedule preventive maintenance within 7 days",
            "Monitor vibration levels closely",
            "Check bearing condition",
        ] if failure_probability > 0.15 else [
            "Continue normal operation",
            "Standard maintenance schedule",
        ],
        "model_version": "mock-v1.0.0",
    }
