"""
Edge Simulator - SIMPLIFIED VERSION for Mockup Demo

Changes from original:
- In-memory queue (vs SQLite buffer)
- Synchronous processing (vs async)
- Direct HTTP sync (vs store-and-forward)
- No local ONNX inference
- Basic feature engineering only

Time saved: 1-2 days
Impact: None on core demo functionality
"""

import time
from queue import Queue, Empty
from datetime import datetime
from typing import Dict, Any, List
import httpx  # Using httpx instead of requests (already installed)
from collections import deque


class FeatureEngine:
    """
    Simple feature engineering for time-series data
    
    Features computed:
    - Simple Moving Average (SMA)
    - Derivatives (rate of change)
    - Min/Max over window
    """

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.buffers = {}  # sensor -> deque of values

    def add_reading(self, sensor: str, value: float):
        """Add new reading to sensor buffer"""
        if sensor not in self.buffers:
            self.buffers[sensor] = deque(maxlen=self.window_size)
        
        self.buffers[sensor].append(value)

    def compute_sma(self, sensor: str) -> float:
        """Compute Simple Moving Average"""
        if sensor not in self.buffers or len(self.buffers[sensor]) == 0:
            return 0.0
        
        values = list(self.buffers[sensor])
        return sum(values) / len(values)

    def compute_derivative(self, sensor: str) -> float:
        """Compute derivative (change rate)"""
        if sensor not in self.buffers or len(self.buffers[sensor]) < 2:
            return 0.0
        
        values = list(self.buffers[sensor])
        return values[-1] - values[-2]

    def compute_min(self, sensor: str) -> float:
        """Compute minimum over window"""
        if sensor not in self.buffers or len(self.buffers[sensor]) == 0:
            return 0.0
        
        return min(self.buffers[sensor])

    def compute_max(self, sensor: str) -> float:
        """Compute maximum over window"""
        if sensor not in self.buffers or len(self.buffers[sensor]) == 0:
            return 0.0
        
        return max(self.buffers[sensor])

    def compute_features(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute all features from raw sensor data
        
        Input format:
        {
            "machine_id": "TRUCK-21",
            "timestamp": "2025-11-14T...",
            "metrics": {
                "vibration": 3.5,
                "temperature": 75.2,
                ...
            }
        }
        
        Output format:
        {
            "machine_id": "TRUCK-21",
            "timestamp": "2025-11-14T...",
            "features": {
                "vibration_sma": 3.2,
                "vibration_derivative": 0.1,
                "vibration_min": 2.8,
                "vibration_max": 4.1,
                ...
            }
        }
        """
        features = {}
        
        # Add readings to buffers
        for sensor, value in raw_data.get("metrics", {}).items():
            self.add_reading(sensor, value)
            
            # Compute features for this sensor
            features[f"{sensor}_sma"] = round(self.compute_sma(sensor), 2)
            features[f"{sensor}_derivative"] = round(self.compute_derivative(sensor), 2)
            features[f"{sensor}_min"] = round(self.compute_min(sensor), 2)
            features[f"{sensor}_max"] = round(self.compute_max(sensor), 2)
        
        return {
            "machine_id": raw_data.get("machine_id"),
            "timestamp": raw_data.get("timestamp"),
            "features": features
        }


class BackendSyncClient:
    """Simple HTTP client to sync data to backend"""

    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.raw_endpoint = f"{backend_url}/ingest/raw"
        self.features_endpoint = f"{backend_url}/ingest/features"

    def send_raw(self, data: Dict[str, Any]) -> bool:
        """Send raw telemetry to backend"""
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.raw_endpoint,
                    json=data,
                    timeout=5.0
                )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Raw sync failed: {e}")
            return False

    def send_features(self, data: Dict[str, Any]) -> bool:
        """Send computed features to backend"""
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.features_endpoint,
                    json=data,
                    timeout=5.0
                )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Features sync failed: {e}")
            return False


class EdgeSimulator:
    """
    Simplified Edge Device Simulator
    
    Workflow:
    1. Receive raw data from IoT (via queue)
    2. Compute features
    3. Sync both raw and features to backend
    """

    def __init__(
        self,
        backend_url: str = "http://localhost:8000",
        queue_size: int = 100,
        window_size: int = 10
    ):
        self.data_queue = Queue(maxsize=queue_size)
        self.feature_engine = FeatureEngine(window_size=window_size)
        self.backend_client = BackendSyncClient(backend_url)
        
        self.processed_count = 0
        self.synced_count = 0
        self.failed_count = 0

    def receive_iot_data(self, raw_data: Dict[str, Any]):
        """Receive data from IoT device (simulated)"""
        try:
            self.data_queue.put(raw_data, block=False)
            return True
        except:
            print("⚠️  Queue full, dropping sample")
            return False

    def process_loop(self, max_iterations: int = 1000):
        """
        Main processing loop
        
        Continuously:
        1. Get data from queue
        2. Compute features
        3. Sync to backend
        """
        print("🔄 Edge Simulator - Processing Loop Started")
        print("=" * 60)
        print(f"📡 Backend: {self.backend_client.backend_url}")
        print(f"📊 Queue size: {self.data_queue.maxsize}")
        print(f"🪟 Feature window: {self.feature_engine.window_size}")
        print()
        
        iteration = 0
        
        try:
            while iteration < max_iterations:
                try:
                    # Get raw data from queue (timeout 1 sec)
                    raw_data = self.data_queue.get(timeout=1.0)
                    
                    # Compute features
                    feature_data = self.feature_engine.compute_features(raw_data)
                    self.processed_count += 1
                    
                    # Sync to backend (both raw and features)
                    raw_success = self.backend_client.send_raw(raw_data)
                    features_success = self.backend_client.send_features(feature_data)
                    
                    if raw_success and features_success:
                        self.synced_count += 1
                    else:
                        self.failed_count += 1
                    
                    # Log every 50 samples
                    if self.processed_count % 50 == 0:
                        print(f"✅ Processed: {self.processed_count} | "
                              f"Synced: {self.synced_count} | "
                              f"Failed: {self.failed_count}")
                    
                    iteration += 1
                
                except Empty:
                    # Queue is empty, wait a bit
                    time.sleep(0.1)
                    continue
        
        except KeyboardInterrupt:
            print("\n🛑 Edge simulator stopped by user")
        
        print()
        print("📊 Final Stats:")
        print(f"  Total processed: {self.processed_count}")
        print(f"  Successfully synced: {self.synced_count}")
        print(f"  Failed: {self.failed_count}")
        if self.processed_count > 0:
            print(f"  Success rate: {self.synced_count / self.processed_count * 100:.1f}%")


def run_edge_simulator(backend_url: str = "http://localhost:8000"):
    """
    Run simplified edge simulator
    
    In real scenario, this would receive data from IoT devices.
    For testing, you can manually push data to the queue.
    """
    edge = EdgeSimulator(backend_url=backend_url)
    
    # Start processing
    edge.process_loop(max_iterations=1000)


if __name__ == "__main__":
    run_edge_simulator()
