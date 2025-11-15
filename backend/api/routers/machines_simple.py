"""
Simple Machines Router for Development
Returns mock data for frontend demo without database dependencies
"""

from fastapi import APIRouter
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter()


# Mock machine data
MACHINES = [
    {
        "machine_id": "TRUCK-21",
        "type": "haul_truck",
        "site": "Copper Mine - North Pit",
        "status": "operational",
        "last_reading": datetime.utcnow().isoformat(),
    }
]


@router.get("/")
async def get_machines() -> List[Dict[str, Any]]:
    """Get list of all machines"""
    return MACHINES


@router.get("/{machine_id}")
async def get_machine(machine_id: str) -> Dict[str, Any]:
    """Get specific machine details"""
    machine = next((m for m in MACHINES if m["machine_id"] == machine_id), None)
    if not machine:
        return {"error": "Machine not found"}
    return machine


@router.get("/{machine_id}/metrics")
async def get_machine_metrics(machine_id: str) -> Dict[str, Any]:
    """Get machine metrics (time series data)"""
    
    # Generate mock time series data for the last hour
    now = datetime.utcnow()
    data_points = []
    
    for i in range(60):  # 60 data points (1 per minute)
        timestamp = now - timedelta(minutes=60-i)
        data_points.append({
            "timestamp": timestamp.isoformat(),
            "vibration": round(random.uniform(2.5, 4.5), 2),
            "temperature": round(random.uniform(75, 85), 2),
            "rpm": round(random.uniform(1200, 1800), 2),
            "co2_ppm": round(random.uniform(400, 800), 2),
            "fuel_consumption": round(random.uniform(25, 35), 2),
        })
    
    return {
        "machine_id": machine_id,
        "data": data_points,
        "summary": {
            "avg_vibration": 3.5,
            "avg_temperature": 80.0,
            "avg_rpm": 1500.0,
            "total_readings": len(data_points),
        }
    }
