import asyncio
from datetime import datetime
import random
from typing import Dict, Any
import httpx
from config import EDGE_BASE_URL, MACHINES, INTERVAL_SECONDS, MACHINE_CONFIGS, NORMAL_PHASE_CYCLES, DRIFT_PHASE_CYCLES
from anomalies import generate_normal_metrics, apply_drift, apply_failure_spike, get_failure_types_for_machine, should_trigger_anomaly

async def send_payload(payload: Dict[str, Any]) -> bool:
    url = f"{EDGE_BASE_URL}/iot/raw"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            return response.status_code == 200
    except:
        return False

def build_payload(machine_id: str, phase: str, cycle: int) -> Dict[str, Any]:
    config = MACHINE_CONFIGS.get(machine_id, MACHINE_CONFIGS["TRUCK-21"])
    machine_type = config["type"]
    metrics = generate_normal_metrics(machine_id, config)
    if phase == "drift":
        drift_intensity = min(cycle / DRIFT_PHASE_CYCLES, 1.0) * 0.1
        metrics = apply_drift(metrics, drift_factor=drift_intensity)
    elif phase == "failure":
        if should_trigger_anomaly(cycle, phase, anomaly_probability=0.2):
            failure_types = get_failure_types_for_machine(machine_type)
            failure_type = random.choice(failure_types)
            metrics = apply_failure_spike(metrics, failure_type=failure_type)
            print(f"🔥 {machine_id}: {failure_type} anomaly")
    return {"machine_id": machine_id, "timestamp": datetime.utcnow().isoformat() + "Z", "metrics": metrics}

async def simulate_machine(machine_id: str):
    cycle = 0
    print(f"🚀 Starting {machine_id}")
    while True:
        if cycle < NORMAL_PHASE_CYCLES:
            phase = "normal"
        elif cycle < NORMAL_PHASE_CYCLES + DRIFT_PHASE_CYCLES:
            phase = "drift"
        else:
            phase = "failure" if random.random() < 0.25 else "drift"
        payload = build_payload(machine_id, phase, cycle)
        await send_payload(payload)
        if cycle % 10 == 0:
            print(f"✅ {machine_id} [{phase}]: Cycle {cycle}")
        cycle += 1
        await asyncio.sleep(INTERVAL_SECONDS)

async def main():
    print("🏭 AurumAI IoT Simulator Starting")
    print(f"📡 Edge: {EDGE_BASE_URL}")
    print(f"⚙️  Machines: {', '.join(MACHINES)}")
    tasks = [simulate_machine(m.strip()) for m in MACHINES if m.strip()]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped")
