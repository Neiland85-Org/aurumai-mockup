from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class RawMeasurement(BaseModel):
    machine_id: str
    timestamp: datetime
    metrics: Dict[str, float]


class FeatureVector(BaseModel):
    machine_id: str
    timestamp: datetime
    features: Dict[str, float]


class PredictionRequest(BaseModel):
    machine_id: str


class PredictionResponse(BaseModel):
    machine_id: str
    timestamp: datetime
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Failure risk score 0-1")
    failure_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of failure")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    maintenance_hours: Optional[int] = None


class ESGRequest(BaseModel):
    machine_id: str


class ESGResponse(BaseModel):
    machine_id: str
    timestamp: datetime
    instant_co2eq_kg: float = Field(..., description="Instant CO2eq in kg")
    cumulative_co2eq_kg: float = Field(..., description="Total accumulated CO2eq in kg")
    fuel_rate_lh: Optional[float] = Field(None, description="Current fuel rate in l/h")
    kwh: Optional[float] = Field(None, description="Current power consumption in kWh")
    scope: str = Field(default="scope1", description="Emission scope")


class MachineMetrics(BaseModel):
    machine_id: str
    current_status: str
    last_measurement: Optional[datetime] = None
    metrics: Dict[str, float]
    alerts_count: int = 0
    predictions: Optional[PredictionResponse] = None


class MachineInfo(BaseModel):
    machine_id: str
    machine_type: str
    site: str
    status: str
    commissioned_date: Optional[datetime] = None
