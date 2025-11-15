from __future__ import annotations

import random
from typing import Any, Mapping
from typing_extensions import TypedDict


class _PredictionResultRequired(TypedDict):
    """Required fields in prediction results (must always be present)"""
    risk_score: float
    failure_probability: float
    maintenance_hours: int


class PredictionResult(_PredictionResultRequired, total=False):
    """Complete prediction result with required + optional fields"""
    confidence: float
    failure_type: str | None
    model_version: str


class BatchPrediction(TypedDict):
    timestamp: Any
    prediction: PredictionResult


class FeaturesBatchItem(TypedDict, total=False):
    machine_type: str
    features: Mapping[str, float | int]
    timestamp: Any


def run_prediction(
    machine_id: str, machine_type: str, features: Mapping[str, float | int]
) -> PredictionResult:
    """
    Fake but credible ML prediction engine for predictive maintenance.

    Uses a combination of:
    - Random baseline risk
    - Feature-based risk adjustment
    - Machine type specific patterns

    In production, this would load a real ML model (ONNX, pickle, etc.)
    """

    # Base risk varies by machine type
    base_risk = {
        "haul_truck": random.uniform(0.10, 0.25),
        "grinding_mill": random.uniform(0.15, 0.30),
        "industrial_boiler": random.uniform(0.08, 0.20),
    }.get(machine_type, random.uniform(0.05, 0.20))

    # Extract key features if available
    vibration = float(features.get("vibration") or features.get("raw_vibration") or 3.0)
    temperature = float(features.get("temperature") or features.get("raw_temperature") or 85.0)
    rpm = float(features.get("rpm") or features.get("raw_rpm") or 1600.0)

    # Risk modifiers based on features
    risk_adjustment = 0.0

    # High vibration increases risk
    if vibration > 5.0:
        risk_adjustment += 0.25
    elif vibration > 4.5:
        risk_adjustment += 0.15
    elif vibration > 4.0:
        risk_adjustment += 0.08

    # High temperature increases risk
    if temperature > 100:
        risk_adjustment += 0.20
    elif temperature > 95:
        risk_adjustment += 0.10

    # Abnormal RPM
    if rpm > 1900 or rpm < 1300:
        risk_adjustment += 0.12

    # Check for drift patterns (mock moving average detection)
    if "avg_all_metrics" in features:
        avg_value = features["avg_all_metrics"]
        if avg_value > 50:  # Arbitrary threshold for demo
            risk_adjustment += 0.05

    # Calculate final risk score (0-1)
    risk_score = min(base_risk + risk_adjustment + random.uniform(-0.05, 0.05), 0.95)
    failure_probability = min(risk_score * 1.2, 0.99)

    # Estimate hours until maintenance needed
    if risk_score < 0.3:
        maintenance_hours = random.randint(300, 500)
    elif risk_score < 0.5:
        maintenance_hours = random.randint(150, 300)
    elif risk_score < 0.7:
        maintenance_hours = random.randint(50, 150)
    else:
        maintenance_hours = random.randint(10, 50)

    # Confidence tends to be lower for edge cases
    confidence = 0.85 if risk_score < 0.7 else random.uniform(0.70, 0.85)

    return {
        "risk_score": round(risk_score, 3),
        "failure_probability": round(failure_probability, 3),
        "confidence": round(confidence, 2),
        "maintenance_hours": maintenance_hours,
        "model_version": "mock_v1.0",
    }


def run_batch_prediction(
    machine_id: str, features_batch: list[FeaturesBatchItem]
) -> list[BatchPrediction]:
    """
    Run predictions on a batch of feature vectors.
    Used for historical analysis or batch jobs.
    """
    results: list[BatchPrediction] = []
    for feature_vec in features_batch:
        features_payload: Mapping[str, float | int] | None = feature_vec.get("features")
        if features_payload is None:
            features_payload = {}
        prediction = run_prediction(
            machine_id,
            feature_vec.get("machine_type", "unknown"),
            features_payload,
        )
        entry: BatchPrediction = {
            "timestamp": feature_vec.get("timestamp"),
            "prediction": prediction,
        }
        results.append(entry)
    return results
