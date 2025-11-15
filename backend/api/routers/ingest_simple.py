"""
Simple Ingest Router for Development
Stores telemetry in memory without database dependencies
"""

from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import List, Dict, Any, Union, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for development
# WARNING: The following lists are NOT thread-safe and are shared across all requests.
# In a production ASGI environment with multiple workers or async handlers, this can lead to race conditions.
# Do NOT use this code in production. Use a thread-safe collection or a proper database instead.
telemetry_store: List[Dict[str, Any]] = []
features_store: List[Dict[str, Any]] = []


class RawMeasurement(BaseModel):
    """Raw measurement from IoT device"""
    machine_id: str
    timestamp: datetime
    sample_number: Optional[int] = None
    status: Optional[str] = None
    
    # Support both flat format and nested metrics
    metrics: Optional[Dict[str, float]] = None
    
    # Individual metrics (optional, for flat format)
    rpm: Optional[float] = None
    temperature: Optional[float] = None
    vibration: Optional[float] = None
    fuel_rate_lh: Optional[float] = None
    fuel_consumption: Optional[float] = None
    co2_ppm: Optional[float] = None
    pressure: Optional[float] = None
    speed_kmh: Optional[float] = None
    load_tons: Optional[float] = None
    steam_pressure_bar: Optional[float] = None
    kwh: Optional[float] = None


class FeatureBatch(BaseModel):
    """Batch of computed features"""
    machine_id: str
    timestamp: datetime
    window_size: Optional[int] = None
    features: Dict[str, float]


class TelemetryBatch(BaseModel):
    """Batch of raw measurements and features"""
    raw: List[RawMeasurement]
    features: Optional[List[FeatureBatch]] = None


@router.post("/raw", status_code=status.HTTP_200_OK)
async def ingest_raw(measurements: Union[List[RawMeasurement], RawMeasurement]):
    """
    Ingest batch of raw measurements or single measurement
    """
    # Handle both single object and list
    if not isinstance(measurements, list):
        measurements = [measurements]
    
    for measurement in measurements:
        telemetry_store.append(measurement.model_dump())
    
    logger.info(f"Ingested {len(measurements)} raw measurements")
    
    return {
        "status": "success",
        "stored": len(measurements),
        "total": len(telemetry_store),
    }


@router.post("/features", status_code=status.HTTP_200_OK)
async def ingest_features(features: Union[List[FeatureBatch], FeatureBatch]):
    """
    Ingest batch of computed features or single feature batch
    """
    # Handle both single object and list
    if not isinstance(features, list):
        features = [features]
    
    for feature in features:
        features_store.append(feature.model_dump())
    
    logger.info(f"Ingested {len(features)} feature batches")
    
    return {
        "status": "success",
        "stored": len(features),
        "total": len(features_store),
    }


@router.post("/telemetry/batch", status_code=status.HTTP_201_CREATED)
async def ingest_batch(batch: TelemetryBatch):
    """
    Ingest batch of telemetry data (raw + features)
    """
    raw_count = len(batch.raw)
    feature_count = len(batch.features) if batch.features else 0
    
    # Store in memory
    for measurement in batch.raw:
        telemetry_store.append(measurement.model_dump())
    
    if batch.features:
        for feature in batch.features:
            features_store.append(feature.model_dump())
    
    logger.info(f"Ingested batch: {raw_count} raw, {feature_count} features")
    
    return {
        "status": "success",
        "raw_stored": raw_count,
        "features_stored": feature_count,
        "total_raw": len(telemetry_store),
        "total_features": len(features_store),
    }


@router.get("/telemetry/stats")
async def get_stats():
    """Get storage statistics"""
    return {
        "total_raw": len(telemetry_store),
        "total_features": len(features_store),
        "last_raw": telemetry_store[-1] if telemetry_store else None,
        "last_features": features_store[-1] if features_store else None,
    }


@router.delete("/telemetry/clear")
async def clear_storage():
    """Clear all stored data"""
    telemetry_store.clear()
    features_store.clear()
    return {"status": "cleared"}
