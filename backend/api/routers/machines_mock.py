"""
Machines Router - MOCK VERSION (Temporary)
Returns mock data when database is not available.
This file provides sample data for development without requiring PostgreSQL.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Request

# Get the global limiter from the infrastructure module
from infrastructure.rate_limiting import limiter
from models import MachineInfo, MachineMetrics, PredictionResponse

logger = logging.getLogger("aurumai")

router = APIRouter()

# Rate limiter for machines endpoints


# Mock data
MOCK_MACHINES = [
    {
        "machine_id": "CNC-001",
        "machine_type": "CNC_MILL",
        "site": "Factory-A",
        "status": "operational",
        "commissioned_date": datetime(2022, 1, 15, tzinfo=timezone.utc),
    },
    {
        "machine_id": "CNC-002",
        "machine_type": "CNC_LATHE",
        "site": "Factory-A",
        "status": "operational",
        "commissioned_date": datetime(2022, 3, 20, tzinfo=timezone.utc),
    },
    {
        "machine_id": "PRESS-001",
        "machine_type": "HYDRAULIC_PRESS",
        "site": "Factory-B",
        "status": "operational",
        "commissioned_date": datetime(2021, 11, 10, tzinfo=timezone.utc),
    },
    {
        "machine_id": "WELD-001",
        "machine_type": "WELDING_ROBOT",
        "site": "Factory-A",
        "status": "offline",
        "commissioned_date": datetime(2023, 2, 5, tzinfo=timezone.utc),
    },
    {
        "machine_id": "PACK-001",
        "machine_type": "PACKAGING_LINE",
        "site": "Factory-C",
        "status": "operational",
        "commissioned_date": datetime(2022, 8, 12, tzinfo=timezone.utc),
    },
]


@router.get("/", response_model=list[MachineInfo])
@limiter.limit("200/minute")
async def list_machines(request: Request) -> list[MachineInfo]:
    """
    List all available machines (MOCK VERSION).
    Returns sample data without database connection.

    Returns:
        List of mock machines with basic info.
    """
    logger.info("🔧 Using MOCK machines endpoint (database not available)")

    return [
        MachineInfo(
            machine_id=m["machine_id"],
            machine_type=m["machine_type"],
            site=m["site"],
            status=m["status"],
            commissioned_date=m["commissioned_date"],
        )
        for m in MOCK_MACHINES
    ]


@router.get("/{machine_id}/metrics", response_model=MachineMetrics)
@limiter.limit("100/minute")
async def get_machine_metrics(request: Request, machine_id: str) -> MachineMetrics:
    """
    Get current metrics and status for a specific machine (MOCK VERSION).
    Returns sample metrics without database connection.

    Args:
        machine_id: The ID of the machine to retrieve metrics for.

    Returns:
        Mock machine metrics including status, measurements, and predictions.
    """
    logger.info(f"🔧 Using MOCK metrics endpoint for machine: {machine_id}")

    # Find machine in mock data
    machine = next((m for m in MOCK_MACHINES if m["machine_id"] == machine_id), None)

    if not machine:
        # Return default mock machine if not found
        machine = MOCK_MACHINES[0]
        machine_id = machine["machine_id"]

    # Generate mock metrics based on machine ID
    now = datetime.utcnow()

    # Mock metrics vary by machine type
    mock_metrics: dict[str, Any] = {
        "temperature": 45.2 + hash(machine_id) % 20,
        "vibration": 0.5 + (hash(machine_id) % 10) / 10,
        "power_consumption": 12.5 + (hash(machine_id) % 50) / 10,
        "rpm": 1500 + hash(machine_id) % 500,
        "pressure": 80 + hash(machine_id) % 40,
    }

    # Mock prediction
    risk_score = 0.2 + (hash(machine_id) % 30) / 100
    prediction = PredictionResponse(
        machine_id=machine_id,
        timestamp=now,
        risk_score=risk_score,
        failure_probability=risk_score * 1.2,
        confidence=0.85 + (hash(machine_id) % 10) / 100,
        maintenance_hours=240 - int(risk_score * 100),
    )

    # Alerts based on risk
    alerts_count = 1 if risk_score > 0.4 else 0

    return MachineMetrics(
        machine_id=machine_id,
        current_status=machine["status"],
        last_measurement=now - timedelta(seconds=30),
        metrics=mock_metrics,
        alerts_count=alerts_count,
        predictions=prediction,
    )
