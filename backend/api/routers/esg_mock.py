"""
ESG Mock Router - For demo/development without database
Provides simulated ESG/Carbon emission data.
"""

import logging
import random
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Query

from models import ESGResponse

logger = logging.getLogger("aurumai")

router = APIRouter()

# Mock machine IDs (should match machines_mock.py)
VALID_MACHINE_IDS = {"CNC-001", "CNC-002", "PRESS-001", "WELD-001", "PACK-001"}


def _generate_mock_esg(machine_id: str) -> dict[str, Any]:
    """Generate realistic mock ESG data for a machine."""
    # Base values depend on machine type
    if "CNC" in machine_id:
        base_power = 15.0  # kW
        base_co2 = 8.5  # kg/h
    elif "PRESS" in machine_id:
        base_power = 45.0
        base_co2 = 25.0
    elif "WELD" in machine_id:
        base_power = 12.0
        base_co2 = 6.8
    else:  # PACK
        base_power = 8.0
        base_co2 = 4.5

    # Add some realistic variation
    variation = random.uniform(0.85, 1.15)
    instant_co2 = base_co2 * variation
    power_kw = base_power * variation
    
    # Cumulative is instant * random runtime hours
    runtime_hours = random.uniform(100, 500)
    cumulative_co2 = instant_co2 * runtime_hours

    # Fuel rate (liters per hour) - only for some machines
    fuel_rate = base_co2 * 0.35 if random.random() > 0.3 else None

    return {
        "instant_co2eq_kg": round(instant_co2, 2),
        "cumulative_co2eq_kg": round(cumulative_co2, 2),
        "fuel_rate_lh": round(fuel_rate, 2) if fuel_rate else None,
        "kwh": round(power_kw, 2),
        "scope": "scope1" if fuel_rate else "scope2",
    }


@router.get("/current", response_model=ESGResponse)
async def get_current_esg_mock(
    machine_id: str = Query(..., description="Machine ID", min_length=1),
) -> ESGResponse:
    """
    Get current mock ESG/Carbon metrics for a machine.
    Returns simulated data - no database required.
    
    Args:
        machine_id: The machine to get ESG data for.
        
    Returns:
        Mock ESG metrics including CO2 emissions and fuel consumption.
    """
    logger.info(f"🔧 Using MOCK ESG endpoint for '{machine_id}' (database not available)")

    # Validate machine exists
    if machine_id not in VALID_MACHINE_IDS:
        from models_errors import ResourceNotFoundException
        raise ResourceNotFoundException(
            message=f"Machine '{machine_id}' not found in mock data",
            resource_type="machine",
            resource_id=machine_id,
        )

    # Generate mock data
    esg_data = _generate_mock_esg(machine_id)

    return ESGResponse(
        machine_id=machine_id,
        timestamp=datetime.now(timezone.utc),
        instant_co2eq_kg=esg_data["instant_co2eq_kg"],
        cumulative_co2eq_kg=esg_data["cumulative_co2eq_kg"],
        fuel_rate_lh=esg_data["fuel_rate_lh"],
        kwh=esg_data["kwh"],
        scope=esg_data["scope"],
    )


@router.get("/summary")
async def get_esg_summary_mock() -> dict[str, Any]:
    """
    Get aggregated mock ESG summary across all machines.
    Returns simulated data - no database required.
    
    Returns:
        Dictionary with total emissions and per-machine breakdown.
    """
    logger.info("🔧 Using MOCK ESG summary endpoint (database not available)")

    machines_data = []
    total_co2 = 0.0

    for machine_id in VALID_MACHINE_IDS:
        esg_data = _generate_mock_esg(machine_id)
        total_co2 += esg_data["cumulative_co2eq_kg"]
        machines_data.append({
            "machine_id": machine_id,
            "co2eq_total": esg_data["cumulative_co2eq_kg"],
            "scope": esg_data["scope"],
        })

    return {
        "total_co2eq_kg": round(total_co2, 2),
        "total_co2eq_tons": round(total_co2 / 1000, 3),
        "machines_count": len(VALID_MACHINE_IDS),
        "monitored_machines": len(VALID_MACHINE_IDS),
        "machines": machines_data,
    }
