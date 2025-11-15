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

With Observability:
- JSON structured logging
- Retry policies with exponential backoff
- Circuit breaker for backend connection
- Configurable timeouts
"""

import random
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import httpx

from observability import (
    setup_logging,
    set_sample_context,
    clear_sample_context,
    create_retry_decorator,
    create_circuit_breaker,
    create_timeout_config,
)
from pybreaker import CircuitBreakerError


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
    """
    Resilient HTTP publisher to backend/edge
    
    Features:
    - Structured JSON logging
    - Automatic retries with exponential backoff
    - Circuit breaker for backend protection
    - Configurable timeouts
    """

    def __init__(
        self,
        backend_url: str = "http://localhost:8000",
        logger: Optional[logging.Logger] = None,
        max_retries: int = 3,
        circuit_breaker_enabled: bool = True
    ):
        self.backend_url = backend_url
        self.endpoint = f"{backend_url}/ingest/raw"
        self.logger = logger or logging.getLogger(__name__)
        
        # Configure timeout
        self.timeout = create_timeout_config(
            connect=5.0,
            read=30.0,
            write=30.0,
            pool=5.0
        )
        
        # Configure circuit breaker
        self.circuit_breaker = None
        if circuit_breaker_enabled:
            self.circuit_breaker = create_circuit_breaker(
                name="iot-backend-connection",
                fail_max=5,
                timeout_duration=60.0,
                logger=self.logger
            )
        
        # Configure retry decorator
        self.retry_publish = create_retry_decorator(
            max_attempts=max_retries,
            base_delay=1.0,
            max_delay=30.0,
            multiplier=2.0,
            logger=self.logger
        )
        
        self.logger.info(
            "HTTP Publisher initialized",
            extra={
                "backend_url": backend_url,
                "max_retries": max_retries,
                "circuit_breaker_enabled": circuit_breaker_enabled
            }
        )

    def _publish_with_retry(self, data: Dict[str, Any]) -> httpx.Response:
        """Internal method with retry logic"""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                self.endpoint,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response

    def publish(self, data: Dict[str, Any]) -> bool:
        """
        Publish data to backend via HTTP POST with resilience
        
        Args:
            data: Telemetry data to publish
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Apply retry decorator
            publish_fn = self.retry_publish(self._publish_with_retry)
            
            # Apply circuit breaker if enabled
            if self.circuit_breaker:
                response = self.circuit_breaker.call(publish_fn, data)
            else:
                response = publish_fn(data)
            
            self.logger.debug(
                "Data published successfully",
                extra={
                    "status_code": response.status_code,
                    "machine_id": data.get("machine_id"),
                    "sample_number": data.get("sample_number")
                }
            )
            return True
            
        except CircuitBreakerError:
            self.logger.warning(
                "Circuit breaker open - backend unavailable",
                extra={
                    "machine_id": data.get("machine_id"),
                    "sample_number": data.get("sample_number")
                }
            )
            return False
            
        except httpx.HTTPError as e:
            self.logger.error(
                "HTTP error publishing data",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "machine_id": data.get("machine_id"),
                    "sample_number": data.get("sample_number")
                }
            )
            return False
            
        except Exception as e:
            self.logger.error(
                "Unexpected error publishing data",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "machine_id": data.get("machine_id"),
                    "sample_number": data.get("sample_number")
                },
                exc_info=True
            )
            return False


def run_simulator(
    backend_url: str = "http://localhost:8000",
    samples: int = 1000,
    interval_seconds: float = 1.0,
    log_level: str = "INFO",
    environment: str = "development"
):
    """
    Run simplified IoT simulator with observability
    
    Args:
        backend_url: Backend API URL
        samples: Total samples to generate
        interval_seconds: Time between samples
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        environment: Environment name (development, staging, production)
    """
    # Setup structured logging
    logger = setup_logging(
        level=log_level,
        environment=environment,
        component="iot-simulator"
    )
    
    logger.info(
        "Starting IoT Simulator",
        extra={
            "backend_url": backend_url,
            "samples": samples,
            "interval_seconds": interval_seconds,
            "environment": environment
        }
    )
    
    print("🚛 TRUCK-21 IoT Simulator - With Observability")
    print("=" * 60)
    print(f"📡 Backend: {backend_url}")
    print(f"📊 Samples: {samples}")
    print(f"⏱️  Interval: {interval_seconds}s")
    print(f"📝 Log Level: {log_level}")
    print(f"🌍 Environment: {environment}")
    print()
    
    simulator = TruckSimulator()
    publisher = HTTPPublisher(
        backend_url,
        logger=logger,
        max_retries=3,
        circuit_breaker_enabled=True
    )
    
    success_count = 0
    fail_count = 0
    circuit_breaker_blocks = 0
    
    try:
        for i in range(samples):
            # Generate sample
            data = simulator.generate_sample()
            
            # Set context for structured logging
            set_sample_context(
                machine_id=data["machine_id"],
                sample_number=data["sample_number"]
            )
            
            # Publish to backend
            success = publisher.publish(data)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
                # Check if circuit breaker is open
                if publisher.circuit_breaker and publisher.circuit_breaker.current_state == "open":
                    circuit_breaker_blocks += 1
            
            # Log every 50 samples
            if (i + 1) % 50 == 0:
                status = data['status']
                logger.info(
                    f"Sample {i+1}/{samples} [{status}]",
                    extra={
                        "sample_number": i + 1,
                        "total_samples": samples,
                        "status": status,
                        "success_count": success_count,
                        "fail_count": fail_count,
                        "circuit_breaker_blocks": circuit_breaker_blocks
                    }
                )
                print(f"✅ Sample {i+1}/{samples} [{status}] | "
                      f"Success: {success_count} | Failed: {fail_count} | "
                      f"CB Blocks: {circuit_breaker_blocks}")
            
            # Clear context
            clear_sample_context()
            
            # Wait before next sample
            time.sleep(interval_seconds)
    
    except KeyboardInterrupt:
        logger.warning("Simulator stopped by user (KeyboardInterrupt)")
        print("\n🛑 Simulator stopped by user")
    
    # Final statistics
    success_rate = (success_count / simulator.sample_count * 100) if simulator.sample_count > 0 else 0
    
    logger.info(
        "Simulator finished",
        extra={
            "total_samples": simulator.sample_count,
            "successful": success_count,
            "failed": fail_count,
            "circuit_breaker_blocks": circuit_breaker_blocks,
            "success_rate": success_rate
        }
    )
    
    print()
    print("📊 Final Stats:")
    print(f"  Total samples: {simulator.sample_count}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Circuit Breaker Blocks: {circuit_breaker_blocks}")
    print(f"  Success rate: {success_rate:.1f}%")


if __name__ == "__main__":
    import os
    
    # Configuration from environment variables
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    samples = int(os.getenv("SAMPLES", "1000"))
    interval_seconds = float(os.getenv("INTERVAL_SECONDS", "1.0"))
    log_level = os.getenv("LOG_LEVEL", "INFO")
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Run simulator with observability
    run_simulator(
        backend_url=backend_url,
        samples=samples,
        interval_seconds=interval_seconds,
        log_level=log_level,
        environment=environment
    )
