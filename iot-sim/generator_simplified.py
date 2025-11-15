"""
IoT Data Generator - SIMPLIFIED VERSION for Mockup Demo

Changes from original:
- Single machine: TRUCK-21 only (vs 3 machines)
- Hardcoded anomalies (vs complex injection system)
- Synchronous HTTP (vs async)
- No MQTT support
- Simpler phase progression

Time saved: 1-2 days
Impact: None on core demo functionality
"""

import random
import time
from datetime import datetime
from typing import Dict, Any
import httpx  # Using httpx instead of requests (already installed)


class TruckSimulator:
    """
    Simplified Mining Truck Simulator (TRUCK-21)
    
    Sensors:
    - vibration (mm/s RMS)
    - temperature (°C)
    - rpm (revolutions per minute)
    - co2_ppm (parts per million)
    - fuel_consumption (L/h)
    """

    def __init__(self, machine_id: str = "TRUCK-21"):
        self.machine_id = machine_id
        self.sample_count = 0
        
        # Normal operating ranges
        self.normal_ranges = {
            "vibration": (2.0, 5.0),
            "temperature": (70.0, 85.0),
            "rpm": (1200, 1800),
            "co2_ppm": (400, 800),
            "fuel_consumption": (25.0, 35.0)
        }
        
        # Failure ranges (triggered after threshold)
        self.failure_ranges = {
            "vibration": (15.0, 25.0),      # HIGH - bearing issue
            "temperature": (95.0, 105.0),   # HIGH - overheating
            "rpm": (1200, 1800),            # Normal
            "co2_ppm": (1200, 1800),        # HIGH - incomplete combustion
            "fuel_consumption": (45.0, 60.0) # HIGH - inefficiency
        }

    def generate_normal_data(self) -> Dict[str, Any]:
        """Generate normal operational data"""
        self.sample_count += 1
        
        readings = {}
        for sensor, (low, high) in self.normal_ranges.items():
            value = random.uniform(low, high)
            readings[sensor] = round(value, 2)
        
        return {
            "machine_id": self.machine_id,
            "timestamp": datetime.utcnow().isoformat(),
            "sample_number": self.sample_count,
            "status": "normal",
            "metrics": readings
        }

    def generate_degradation_data(self) -> Dict[str, Any]:
        """Generate data showing gradual degradation (drift)"""
        self.sample_count += 1
        
        readings = {}
        for sensor, (low, high) in self.normal_ranges.items():
            # Shift towards upper bound (degradation)
            mid = (low + high) / 2
            drift_value = random.uniform(mid, high * 1.15)
            readings[sensor] = round(drift_value, 2)
        
        return {
            "machine_id": self.machine_id,
            "timestamp": datetime.utcnow().isoformat(),
            "sample_number": self.sample_count,
            "status": "degrading",
            "metrics": readings
        }

    def generate_failure_data(self) -> Dict[str, Any]:
        """Generate data indicating imminent failure"""
        self.sample_count += 1
        
        readings = {}
        for sensor, (low, high) in self.failure_ranges.items():
            value = random.uniform(low, high)
            readings[sensor] = round(value, 2)
        
        return {
            "machine_id": self.machine_id,
            "timestamp": datetime.utcnow().isoformat(),
            "sample_number": self.sample_count,
            "status": "critical",
            "metrics": readings
        }

    def generate_sample(self) -> Dict[str, Any]:
        """
        Generate next sample with progressive failure pattern
        
        Timeline:
        - Samples 0-600: Normal operation
        - Samples 601-800: Gradual degradation
        - Samples 801+: Critical/failure state
        """
        if self.sample_count < 600:
            return self.generate_normal_data()
        elif self.sample_count < 800:
            return self.generate_degradation_data()
        else:
            return self.generate_failure_data()


class HTTPPublisher:
    """Simple HTTP publisher to backend/edge"""

    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.endpoint = f"{backend_url}/ingest/raw"

    def publish(self, data: Dict[str, Any]) -> bool:
        """Publish data to backend via HTTP POST"""
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.endpoint,
                    json=data,
                    timeout=5.0
                )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Publish failed: {e}")
            return False


def run_simulator(
    backend_url: str = "http://localhost:8000",
    samples: int = 1000,
    interval_seconds: float = 1.0
):
    """
    Run simplified IoT simulator
    
    Args:
        backend_url: Backend API URL
        samples: Total samples to generate
        interval_seconds: Time between samples
    """
    print("🚛 TRUCK-21 IoT Simulator - Simplified Version")
    print("=" * 60)
    print(f"📡 Backend: {backend_url}")
    print(f"📊 Samples: {samples}")
    print(f"⏱️  Interval: {interval_seconds}s")
    print()
    
    simulator = TruckSimulator()
    publisher = HTTPPublisher(backend_url)
    
    success_count = 0
    fail_count = 0
    
    try:
        for i in range(samples):
            # Generate sample
            data = simulator.generate_sample()
            
            # Publish to backend
            success = publisher.publish(data)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
            
            # Log every 50 samples
            if (i + 1) % 50 == 0:
                status = data['status']
                print(f"✅ Sample {i+1}/{samples} [{status}] | "
                      f"Success: {success_count} | Failed: {fail_count}")
            
            # Wait before next sample
            time.sleep(interval_seconds)
    
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped by user")
    
    print()
    print("📊 Final Stats:")
    print(f"  Total samples: {simulator.sample_count}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Success rate: {success_count / simulator.sample_count * 100:.1f}%")


if __name__ == "__main__":
    # Run with defaults
    run_simulator(
        backend_url="http://localhost:8000",
        samples=1000,
        interval_seconds=1.0
    )
