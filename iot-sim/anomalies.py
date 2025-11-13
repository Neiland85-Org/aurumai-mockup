import random
from typing import Dict

def generate_normal_metrics(machine_id: str, config: Dict) -> Dict[str, float]:
    metrics = {}
    metric_ranges = config.get("metrics", {})
    for metric_name, (min_val, max_val) in metric_ranges.items():
        if min_val == max_val:
            metrics[metric_name] = min_val
        else:
            mean = (min_val + max_val) / 2
            std_dev = (max_val - min_val) / 6
            value = random.gauss(mean, std_dev)
            value = max(min_val, min(max_val, value))
            metrics[metric_name] = round(value, 2)
    return metrics

def apply_drift(metrics: Dict[str, float], drift_factor: float = 0.05) -> Dict[str, float]:
    drifted = metrics.copy()
    degradation_metrics = ["vibration", "temperature", "co2_ppm"]
    improvement_metrics = ["rpm"]
    for key in drifted:
        if key in degradation_metrics:
            drifted[key] *= 1.0 + random.uniform(0, drift_factor)
        elif key in improvement_metrics:
            drifted[key] *= 1.0 - random.uniform(0, drift_factor * 0.5)
        else:
            drifted[key] *= random.uniform(0.98, 1.02)
        drifted[key] = round(drifted[key], 2)
    return drifted

def apply_failure_spike(metrics: Dict[str, float], failure_type: str = "vibration") -> Dict[str, float]:
    spiked = metrics.copy()
    if failure_type == "vibration":
        if "vibration" in spiked:
            spiked["vibration"] *= random.uniform(1.8, 2.8)
        if "temperature" in spiked:
            spiked["temperature"] *= random.uniform(1.1, 1.3)
    elif failure_type == "temperature":
        if "temperature" in spiked:
            spiked["temperature"] *= random.uniform(1.3, 1.6)
        if "co2_ppm" in spiked:
            spiked["co2_ppm"] *= random.uniform(1.1, 1.2)
    elif failure_type == "emission":
        if "co2_ppm" in spiked:
            spiked["co2_ppm"] *= random.uniform(1.3, 1.7)
        if "fuel_rate_lh" in spiked:
            spiked["fuel_rate_lh"] *= random.uniform(1.2, 1.4)
    for key in spiked:
        spiked[key] = round(spiked[key], 2)
    return spiked

def get_failure_types_for_machine(machine_type: str) -> list:
    failure_map = {
        "haul_truck": ["vibration", "temperature"],
        "grinding_mill": ["vibration", "temperature"],
        "industrial_boiler": ["temperature", "emission"],
    }
    return failure_map.get(machine_type, ["vibration", "temperature"])

def should_trigger_anomaly(cycle: int, phase: str, anomaly_probability: float = 0.15) -> bool:
    if phase == "normal":
        return random.random() < (anomaly_probability * 0.2)
    elif phase == "drift":
        return random.random() < (anomaly_probability * 0.5)
    elif phase == "failure":
        return random.random() < (anomaly_probability * 1.5)
    return False
