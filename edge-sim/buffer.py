import asyncio
from typing import List, Dict, Any

_buffer: List[Dict[str, Any]] = []
_buffer_lock = asyncio.Lock()

async def add_raw_payload(payload: Dict[str, Any]) -> None:
    """Add a raw telemetry payload to in-memory buffer."""
    async with _buffer_lock:
        _buffer.append(payload)

async def get_and_clear_buffer() -> List[Dict[str, Any]]:
    """Returns current buffer and clears it."""
    global _buffer
    async with _buffer_lock:
        data = list(_buffer)
        _buffer = []
        return data

async def get_buffer_size() -> int:
    """Get current buffer size."""
    async with _buffer_lock:
        return len(_buffer)
