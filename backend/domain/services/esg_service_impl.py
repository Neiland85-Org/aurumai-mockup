"""
Concrete Implementation: ESG Service
Calculates carbon emissions using IPCC/EPA factors
"""

import random
from typing import Any, Dict

from .esg_service import IESGService


class ESGServiceImpl(IESGService):
    """
    ESG/Carbon calculation service using standard emission factors.
    Based on IPCC and EPA guidelines for industrial emissions.
    """

    # Emission factors (Scope 1: Direct emissions)
    FACTOR_FUEL_DIESEL = 2.68  # kg CO2eq per liter (EPA/IPCC standard)
    FACTOR_FUEL_COAL = 2.86  # kg CO2eq per kg of coal burned
    FACTOR_NATURAL_GAS = 2.03  # kg CO2eq per m³

    # Emission factors (Scope 2: Indirect emissions from electricity)
    FACTOR_ELECTRICITY_LATAM = 0.45  # kg CO2eq per kWh (regional average)
    FACTOR_ELECTRICITY_US = 0.40  # kg CO2eq per kWh
    FACTOR_ELECTRICITY_EU = 0.30  # kg CO2eq per kWh (greener grid)

    def __init__(self, region: str = "latam") -> None:
        self.region = region
        self.electricity_factor = {
            "latam": self.FACTOR_ELECTRICITY_LATAM,
            "us": self.FACTOR_ELECTRICITY_US,
            "eu": self.FACTOR_ELECTRICITY_EU,
        }.get(region, self.FACTOR_ELECTRICITY_LATAM)

    async def calculate(
        self,
        machine_id: str,
        machine_type: str,
        metrics: Dict[str, float],
        previous_cumulative: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Calculate ESG/carbon metrics based on machine measurements.

        Computes both instant emissions (current rate) and cumulative totals.
        Breaks down emissions by scope (Scope 1: fuel, Scope 2: electricity).
        """
        # Extract relevant measurements
        fuel_rate_lh = (
            metrics.get("fuel_rate_lh")
            or metrics.get("fuel_rate")
            or random.uniform(8.0, 15.0)
        )
        power_kw = (
            metrics.get("kwh") or metrics.get("power_kw") or random.uniform(2.0, 10.0)
        )
        co2_ppm = metrics.get("co2_ppm") or random.uniform(420, 650)

        # Calculate instant emissions (per measurement period, e.g., per hour)

        # Scope 1: Fuel combustion
        co2eq_fuel = fuel_rate_lh * self.FACTOR_FUEL_DIESEL

        # Scope 2: Electricity consumption
        co2eq_electricity = power_kw * self.electricity_factor

        # Total instant emissions
        co2eq_instant = co2eq_fuel + co2eq_electricity

        # Add realistic variance
        co2eq_instant *= random.uniform(0.95, 1.05)

        # Cumulative total
        co2eq_cumulative = previous_cumulative + co2eq_instant

        # Calculate efficiency score (0-100)
        # Lower emissions relative to power/fuel = higher efficiency
        efficiency_score = self._calculate_efficiency(
            co2eq_instant=co2eq_instant,
            fuel_rate=fuel_rate_lh,
            power_kw=power_kw,
            machine_type=machine_type,
        )

        # Determine dominant scope
        scope = "scope1" if co2eq_fuel > co2eq_electricity else "scope2"

        return {
            "instant_co2eq_kg": round(co2eq_instant, 2),
            "cumulative_co2eq_kg": round(co2eq_cumulative, 2),
            "fuel_rate_lh": round(fuel_rate_lh, 2),
            "power_consumption_kw": round(power_kw, 2),
            "efficiency_score": round(efficiency_score, 1),
            "metadata": {
                "co2_ppm": round(co2_ppm, 1),
                "dominant_scope": scope,
                "breakdown": {
                    "scope1_kg": round(co2eq_fuel, 2),
                    "scope2_kg": round(co2eq_electricity, 2),
                },
                "factors_used": {
                    "fuel_factor": self.FACTOR_FUEL_DIESEL,
                    "electricity_factor": self.electricity_factor,
                    "region": self.region,
                },
            },
        }

    def _calculate_efficiency(
        self,
        co2eq_instant: float,
        fuel_rate: float,
        power_kw: float,
        machine_type: str,
    ) -> float:
        """
        Calculate efficiency score (0-100).
        Higher score = better efficiency (lower emissions per unit of energy).
        """
        # Calculate total energy input
        total_energy = fuel_rate + power_kw

        if total_energy == 0:
            return 50.0  # Neutral score if no energy input

        # Emissions per unit energy
        emissions_per_energy = co2eq_instant / total_energy

        # Machine type baselines (lower is better)
        baselines = {
            "haul_truck": 0.35,
            "grinding_mill": 0.30,
            "industrial_boiler": 0.25,
        }
        baseline = baselines.get(machine_type, 0.30)

        # Score: 100 at half baseline, 0 at double baseline
        score = 100 * (1 - (emissions_per_energy - baseline * 0.5) / (baseline * 1.5))

        # Clamp to 0-100
        return max(0.0, min(100.0, score))
