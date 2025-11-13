import asyncio
from typing import Dict, Any, List
import httpx
from buffer import get_and_clear_buffer
from features import enrich_payload_with_features
from config import BACKEND_BASE_URL

async def send_to_backend(path: str, json_payload: Dict[str, Any]) -> bool:
    url = f"{BACKEND_BASE_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(url, json=json_payload)
            return True
    except:
        return False

async def process_and_forward(payloads: List[Dict[str, Any]]) -> None:
    """
    Process buffered raw payloads:
    - send raw to backend /ingest/raw
    - compute features and send to /ingest/features
    """
    for p in payloads:
        await send_to_backend("/ingest/raw", p)
        features_payload = enrich_payload_with_features(p)
        await send_to_backend("/ingest/features", features_payload)

async def sync_loop(interval_seconds: int = 5) -> None:
    """Periodic loop: takes buffered payloads, processes & forwards to backend"""
    while True:
        buffered = get_and_clear_buffer()
        if buffered:
            await process_and_forward(buffered)
            print(f"📤 Synced {len(buffered)} payloads to backend")
        await asyncio.sleep(interval_seconds)
