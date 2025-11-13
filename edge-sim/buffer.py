from typing import List, Dict, Any
from threading import Lock

_buffer: List[Dict[str, Any]] = []
_buffer_lock = Lock()

def add_raw_payload(payload: Dict[str, Any]) -> None:
    """Add a raw telemetry payload to in-memory buffer."""
    with _buffer_lock:
        _buffer.append(payload)

def get_and_clear_buffer() -> List[Dict[str, Any]]:
    """Returns current buffer and clears it."""
    global _buffer
    with _buffer_lock:
        data = list(_buffer)
        _buffer = []
        return data

def get_buffer_size() -> int:
    """Get current buffer size."""
    with _buffer_lock:
        return len(_buffer)
