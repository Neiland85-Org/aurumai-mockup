import os

EDGE_PORT = int(os.getenv("EDGE_PORT", "9000"))

# Backend AurumAI API
BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
BACKEND_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# Sync interval (seconds)
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "5"))

# Buffer settings
MAX_BUFFER_SIZE = int(os.getenv("MAX_BUFFER_SIZE", "1000"))
