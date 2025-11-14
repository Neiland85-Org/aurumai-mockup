"""
Concrete Implementation: ML Service
Fake but credible ML prediction engine for demo purposes
"""

import random
from typing import Dict, Any

from .ml_service import IMLService


class MLServiceImpl(IMLService):
    """
    Mock ML service implementation using heuristic-based predictions.
    In production, this would integrate with a real ML model (ONNX, TensorFlow, PyTorch, etc.)
    """

    def __init__(self, model_version: str = "mock_v1.0"):
        self.model_version = model_version

    async def predict(
        self,
        machine_id: str,
        machine_type: str,
        features: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Run ML prediction using heuristic rules.

        This is a fake ML engine that produces credible results for demo purposes.
        It analyzes features like vibration, temperature, and RPM to estimate risk.
        """
        # Base risk varies by machine type
        base_risk = {
            "haul_truck": random.uniform(0.10, 0.25),
            "grinding_mill": random.uniform(0.15, 0.30),
            "industrial_boiler": random.uniform(0.08, 0.20),
        }.get(machine_type, random.uniform(0.05, 0.20))

        # Extract key features if available
        vibration = features.get("vibration") or features.get("raw_vibration") or 3.0
        temperature = (
            features.get("temperature") or features.get("raw_temperature") or 85.0
        )
        rpm = features.get("rpm") or features.get("raw_rpm") or 1600.0

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
        risk_score = min(
            base_risk + risk_adjustment + random.uniform(-0.05, 0.05), 0.95
        )
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

        # Determine likely failure type based on which metric is most elevated
        failure_type = None
        if vibration > 4.5:
            failure_type = (
                "bearing_failure"
                if machine_type in ["haul_truck", "grinding_mill"]
                else "mechanical_wear"
            )
        elif temperature > 100:
            failure_type = (
                "overheating"
                if machine_type == "industrial_boiler"
                else "thermal_stress"
            )
        elif rpm > 1900 or rpm < 1300:
            failure_type = "motor_failure"

        return {
            "risk_score": round(risk_score, 3),
            "failure_probability": round(failure_probability, 3),
            "confidence": round(confidence, 2),
            "maintenance_hours": maintenance_hours,
            "failure_type": failure_type,
            "model_version": self.model_version,
        }
