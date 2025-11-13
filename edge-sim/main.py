from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
from datetime import datetime
import asyncio
import uvicorn
from buffer import add_raw_payload, get_buffer_size
from sync import sync_loop
from config import EDGE_PORT, BACKEND_BASE_URL, SYNC_INTERVAL

class RawFromIoT(BaseModel):
    machine_id: str
    timestamp: str
    metrics: Dict[str, float]

app = FastAPI(
    title="AurumAI Edge Simulator",
    description="Edge node mock for AurumAI demo",
    version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
    print("🚀 Edge Simulator starting...")
    print(f"📡 Backend: {BACKEND_BASE_URL}")
    print(f"🔄 Sync interval: {SYNC_INTERVAL}s")
    asyncio.create_task(sync_loop(interval_seconds=SYNC_INTERVAL))

@app.get("/", tags=["health"])
def health():
    return {
        "status": "ok",
        "component": "edge-sim",
        "buffer_size": get_buffer_size()
    }

@app.post("/iot/raw", tags=["ingest"])
def ingest_from_iot(raw: RawFromIoT):
    """Receives telemetry from IoT simulator and buffers it."""
    payload = {
        "machine_id": raw.machine_id,
        "timestamp": raw.timestamp,
        "metrics": raw.metrics
    }
    add_raw_payload(payload)
    return {"status": "ok", "message": "buffered at edge"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=EDGE_PORT)
