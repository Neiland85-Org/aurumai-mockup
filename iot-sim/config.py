import os
from typing import Dict, Any, List, Tuple

# Edge node endpoint
EDGE_HOST: str = os.getenv("EDGE_HOST", "localhost")
EDGE_PORT: int = int(os.getenv("EDGE_PORT", "9000"))
EDGE_BASE_URL: str = f"http://{EDGE_HOST}:{EDGE_PORT}"

# Machines to simulate
MACHINES: List[str] = os.getenv("MACHINES", "TRUCK-21,MILL-3,BOILER-7").split(",")

# Simulation timing
INTERVAL_SECONDS: int = int(os.getenv("SIM_INTERVAL_SECONDS", "3"))

# Phase durations (in cycles)
NORMAL_PHASE_CYCLES: int = int(os.getenv("NORMAL_PHASE_CYCLES", "50"))
DRIFT_PHASE_CYCLES: int = int(os.getenv("DRIFT_PHASE_CYCLES", "50"))

# Machine-specific configurations
MACHINE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "TRUCK-21": {
        "type": "haul_truck",
        "site": "Copper Mine - North Pit",
        "metrics": {
            "rpm": (1400, 1900),
            "temperature": (80, 100),
            "vibration": (2.0, 4.5),
            "fuel_rate_lh": (9.0, 15.0),
            "co2_ppm": (420, 550),
            "pressure": (85, 110),
            "speed_kmh": (15, 45),
        }
    },
    "MILL-3": {
        "type": "grinding_mill",
        "site": "Coal Plant - Processing",
        "metrics": {
            "rpm": (1200, 1600),
            "temperature": (90, 115),
            "vibration": (3.0, 5.5),
            "fuel_rate_lh": (0, 2),
            "co2_ppm": (400, 500),
            "pressure": (95, 125),
            "load_tons": (50, 150),
            "kwh": (150, 250),
        }
    },
    "BOILER-7": {
        "type": "industrial_boiler",
        "site": "Power Generation - Unit 2",
        "metrics": {
            "rpm": (0, 0),
            "temperature": (150, 220),
            "vibration": (1.5, 3.0),
            "fuel_rate_lh": (20, 40),
            "co2_ppm": (500, 800),
            "pressure": (120, 180),
            "steam_pressure_bar": (80, 120),
            "kwh": (50, 100),
        }
    },
}

# Export all public symbols
__all__ = [
    "EDGE_HOST",
    "EDGE_PORT",
    "EDGE_BASE_URL",
    "MACHINES",
    "INTERVAL_SECONDS",
    "NORMAL_PHASE_CYCLES",
    "DRIFT_PHASE_CYCLES",
    "MACHINE_CONFIGS",
]
