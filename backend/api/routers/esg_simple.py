"""
Simple ESG Router for Development
Returns mock ESG metrics without database dependencies
"""

from fastapi import APIRouter, Query
from typing import Dict, Any
from datetime import datetime
import random

router = APIRouter()


@router.get("/current")
async def get_current_esg(machine_id: str = Query(...)) -> Dict[str, Any]:
    """Get current ESG metrics for a machine"""
    
    return {
        "machine_id": machine_id,
        "timestamp": datetime.utcnow().isoformat(),
        "carbon": {
            "co2_kg_per_hour": round(random.uniform(15, 25), 2),
            "co2_total_kg": round(random.uniform(500, 1000), 2),
            "carbon_intensity": round(random.uniform(0.5, 0.8), 3),
        },
        "energy": {
            "kwh_consumed": round(random.uniform(50, 100), 2),
            "efficiency_score": round(random.uniform(0.7, 0.9), 2),
        },
        "esg_score": round(random.uniform(65, 85), 1),
        "rating": "B",
        "trend": "improving",
    }


@router.get("/summary")
async def get_esg_summary() -> Dict[str, Any]:
    """Get ESG summary across all machines"""
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_machines": 1,
        "summary": {
            "total_co2_kg": round(random.uniform(500, 1000), 2),
            "total_kwh": round(random.uniform(50, 100), 2),
            "avg_esg_score": round(random.uniform(70, 80), 1),
            "overall_rating": "B",
        },
        "by_machine": [
            {
                "machine_id": "TRUCK-21",
                "esg_score": round(random.uniform(70, 80), 1),
                "co2_kg": round(random.uniform(500, 1000), 2),
                "rating": "B",
            }
        ],
        "recommendations": [
            "Consider reducing idle time to improve carbon footprint",
            "Optimize fuel consumption during peak operations",
            "Schedule energy efficiency audit",
        ],
    }
