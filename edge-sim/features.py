from typing import Dict, Any
from statistics import mean

def compute_features_from_metrics(metrics: Dict[str, float]) -> Dict[str, float]:
    """
    Simple feature engineering:
    - copy raw metrics as-is
    - add aggregated features
    """
    features: Dict[str, float] = {}

    # Copy raw metrics with prefix
    for k, v in metrics.items():
        features[f"raw_{k}"] = float(v)

    # Aggregate features
    values = list(metrics.values())
    if values:
        features["sum_all_metrics"] = float(sum(values))
        features["avg_all_metrics"] = float(mean(values))
        features["max_metric"] = float(max(values))
        features["min_metric"] = float(min(values))

    # Domain-specific features
    if "vibration" in metrics and "temperature" in metrics:
        features["vib_temp_product"] = metrics["vibration"] * metrics["temperature"]

    if "rpm" in metrics and metrics["rpm"] > 0:
        features["rpm_normalized"] = metrics["rpm"] / 2000.0

    return features

def enrich_payload_with_features(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a feature payload from a raw telemetry payload."""
    return {
        "machine_id": payload["machine_id"],
        "timestamp": payload["timestamp"],
        "features": compute_features_from_metrics(payload["metrics"])
    }
