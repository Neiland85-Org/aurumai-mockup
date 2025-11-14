import random
from typing import Dict, Any

# Emission factors (simplified for demo)
# In production, these would come from EmissionFactor entities with versioning

# Scope 1: Direct emissions
FACTOR_FUEL_DIESEL = 2.68  # kg CO2eq per liter (EPA/IPCC standard)
FACTOR_FUEL_COAL = 2.86  # kg CO2eq per kg of coal burned
FACTOR_NATURAL_GAS = 2.03  # kg CO2eq per m³

# Scope 2: Indirect emissions from electricity
FACTOR_ELECTRICITY_LATAM = 0.45  # kg CO2eq per kWh (regional average)
FACTOR_ELECTRICITY_US = 0.40  # kg CO2eq per kWh
FACTOR_ELECTRICITY_EU = 0.30  # kg CO2eq per kWh (greener grid)

# Scope 3: Other indirect (not implemented in mock)


def compute_esg_metrics(
    machine_id: str,
    measurements: Dict[str, float],
    previous_total: float = 0.0,
    region: str = "latam",
) -> Dict[str, Any]:
    """
    Calculate ESG/Carbon metrics based on machine measurements.

    Args:
        machine_id: Machine identifier
        measurements: Dict of sensor measurements (fuel_rate_lh, kwh, co2_ppm, etc.)
        previous_total: Previous cumulative CO2eq total
        region: Geographic region for electricity factor

    Returns:
        Dict with instant and cumulative CO2eq, scope, and source data
    """

    # Extract relevant measurements
    fuel_rate_lh = (
        measurements.get("fuel_rate_lh")
        or measurements.get("fuel_rate")
        or random.uniform(8.0, 15.0)
    )
    kwh = (
        measurements.get("kwh")
        or measurements.get("power_kw")
        or random.uniform(2.0, 10.0)
    )
    co2_ppm = measurements.get("co2_ppm") or random.uniform(420, 650)

    # Select electricity factor by region
    electricity_factor = {
        "latam": FACTOR_ELECTRICITY_LATAM,
        "us": FACTOR_ELECTRICITY_US,
        "eu": FACTOR_ELECTRICITY_EU,
    }.get(region, FACTOR_ELECTRICITY_LATAM)

    # Calculate instant emissions (per measurement period, e.g., per hour)
    # Scope 1: Fuel combustion
    co2eq_fuel = fuel_rate_lh * FACTOR_FUEL_DIESEL

    # Scope 2: Electricity consumption
    co2eq_electricity = kwh * electricity_factor

    # Total instant emissions
    co2eq_instant = co2eq_fuel + co2eq_electricity

    # Add some realistic variance
    co2eq_instant *= random.uniform(0.95, 1.05)

    # Cumulative total
    co2eq_total = previous_total + co2eq_instant

    # Determine dominant scope
    if co2eq_fuel > co2eq_electricity:
        scope = "scope1"
    else:
        scope = "scope2"

    return {
        "co2eq_instant": round(co2eq_instant, 2),
        "co2eq_total": round(co2eq_total, 2),
        "fuel_rate_lh": round(fuel_rate_lh, 2),
        "kwh": round(kwh, 2),
        "co2_ppm": round(co2_ppm, 1),
        "scope": scope,
        "breakdown": {
            "scope1_kg": round(co2eq_fuel, 2),
            "scope2_kg": round(co2eq_electricity, 2),
        },
        "factors_used": {
            "fuel_factor": FACTOR_FUEL_DIESEL,
            "electricity_factor": electricity_factor,
        },
    }


def calculate_carbon_intensity(
    total_co2eq_kg: float, production_units: float, unit_type: str = "tons"
) -> float:
    """
    Calculate carbon intensity: kg CO2eq per unit of production.

    Args:
        total_co2eq_kg: Total CO2eq emissions in kg
        production_units: Amount produced (tons, kWh, etc.)
        unit_type: Type of production unit

    Returns:
        Carbon intensity value
    """
    if production_units <= 0:
        return 0.0

    return round(total_co2eq_kg / production_units, 3)


def forecast_emissions(
    current_rate_kg_per_hour: float, forecast_hours: int
) -> Dict[str, float]:
    """
    Simple linear forecast of future emissions.
    In production, this would use time series forecasting models.

    Args:
        current_rate_kg_per_hour: Current emission rate
        forecast_hours: Hours to forecast

    Returns:
        Dict with forecasted values
    """
    # Add some realistic growth/degradation
    trend_factor = random.uniform(0.98, 1.03)

    forecast_total = 0.0
    hourly_forecast = []

    for hour in range(forecast_hours):
        hour_emission = current_rate_kg_per_hour * (trend_factor**hour)
        forecast_total += hour_emission
        hourly_forecast.append({"hour": hour + 1, "co2eq_kg": round(hour_emission, 2)})

    return {
        "forecast_hours": forecast_hours,
        "forecast_total_kg": round(forecast_total, 2),
        "forecast_total_tons": round(forecast_total / 1000, 3),
        "hourly": hourly_forecast[:24],  # Return first 24 hours detail
    }
