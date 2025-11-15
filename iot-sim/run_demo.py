"""
Integrated IoT + Edge Simulator - SIMPLIFIED VERSION

This script combines IoT data generation and Edge processing
in a single integrated flow for easy testing.

Usage:
    python run_demo.py

Components:
- IoT Simulator: Generates TRUCK-21 telemetry
- Edge Simulator: Processes features and syncs to backend

With Observability:
- JSON structured logging
- Resilient HTTP connections
- Circuit breakers
"""

import threading
import time
import sys
import os
import logging
from queue import Queue
from typing import Dict, Any, Optional

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'edge-sim'))

from generator_simplified import TruckSimulator
from main_simplified import EdgeSimulator
from observability import setup_logging, set_sample_context, clear_sample_context


def iot_thread_function(
    simulator: TruckSimulator,
    edge_queue: Queue,
    samples: int = 1000,
    interval_seconds: float = 1.0,
    logger: Optional[logging.Logger] = None
):
    """
    IoT thread: Generate data and push to edge queue
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    logger.info("Starting IoT thread", extra={"machine_id": simulator.machine_id})
    print("🚛 IoT Thread: Starting TRUCK-21 simulator")
    
    for i in range(samples):
        # Generate sample
        data = simulator.generate_sample()
        
        # Set context
        set_sample_context(
            machine_id=data["machine_id"],
            sample_number=data["sample_number"]
        )
        
        # Push to edge queue (simulating IoT → Edge communication)
        try:
            edge_queue.put(data, block=False)
        except:
            logger.warning("Queue full", extra={"sample_number": i})
            print(f"⚠️  Queue full at sample {i}")
        
        # Log progress
        if (i + 1) % 100 == 0:
            status = data['status']
            logger.info(
                f"Generated {i+1} samples",
                extra={
                    "samples_generated": i + 1,
                    "total_samples": samples,
                    "status": status
                }
            )
            print(f"🚛 IoT: Generated {i+1}/{samples} samples [{status}]")
        
        # Clear context
        clear_sample_context()
        
        time.sleep(interval_seconds)
    
    logger.info("IoT thread completed", extra={"total_samples": simulator.sample_count})
    print("🚛 IoT Thread: Completed")


def edge_thread_function(
    edge_sim: EdgeSimulator,
    max_iterations: int = 1000,
    logger: Optional[logging.Logger] = None
):
    """
    Edge thread: Process data from queue and sync to backend
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    logger.info("Starting edge thread", extra={"max_iterations": max_iterations})
    print("🔄 Edge Thread: Starting processing loop")
    
    edge_sim.process_loop(max_iterations=max_iterations)
    
    logger.info(
        "Edge thread completed",
        extra={
            "processed_count": edge_sim.processed_count,
            "synced_count": edge_sim.synced_count,
            "failed_count": edge_sim.failed_count
        }
    )
    print("🔄 Edge Thread: Completed")


def run_integrated_demo(
    backend_url: str = "http://localhost:8000",
    samples: int = 1000,
    interval_seconds: float = 1.0,
    log_level: str = "INFO",
    environment: str = "development"
):
    """
    Run integrated IoT + Edge demo with observability
    
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
        component="iot-edge-demo"
    )
    
    logger.info(
        "Starting integrated demo",
        extra={
            "backend_url": backend_url,
            "samples": samples,
            "interval_seconds": interval_seconds,
            "environment": environment
        }
    )
    
    print("=" * 70)
    print("🏭 AurumAI Mockup - IoT + Edge Integrated Simulator")
    print("=" * 70)
    print()
    print("Configuration:")
    print(f"  📡 Backend URL: {backend_url}")
    print(f"  📊 Total samples: {samples}")
    print(f"  ⏱️  Interval: {interval_seconds}s")
    print(f"  🚛 Machine: TRUCK-21 (mining truck)")
    print(f"  📝 Log Level: {log_level}")
    print(f"  🌍 Environment: {environment}")
    print()
    print("Workflow:")
    print("  1. IoT generates telemetry → Queue")
    print("  2. Edge computes features")
    print("  3. Edge syncs to backend (raw + features)")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    # Create shared queue for IoT → Edge communication
    shared_queue = Queue(maxsize=200)
    
    # Initialize simulators
    iot_simulator = TruckSimulator(machine_id="TRUCK-21")
    edge_simulator = EdgeSimulator(
        backend_url=backend_url,
        queue_size=200,
        window_size=10
    )
    
    # Override edge simulator's queue with shared queue
    edge_simulator.data_queue = shared_queue
    
    # Create threads
    iot_thread = threading.Thread(
        target=iot_thread_function,
        args=(iot_simulator, shared_queue, samples, interval_seconds, logger),
        daemon=True
    )
    
    edge_thread = threading.Thread(
        target=edge_thread_function,
        args=(edge_simulator, samples, logger),
        daemon=True
    )
    
    # Start threads
    logger.info("Starting threads")
    iot_thread.start()
    time.sleep(2)  # Let IoT start first
    edge_thread.start()
    
    # Wait for completion
    try:
        iot_thread.join()
        edge_thread.join()
    except KeyboardInterrupt:
        logger.warning("Demo stopped by user (KeyboardInterrupt)")
        print("\n🛑 Demo stopped by user")
    
    # Final summary
    success_rate = 0.0
    if edge_simulator.processed_count > 0:
        success_rate = edge_simulator.synced_count / edge_simulator.processed_count * 100
    
    logger.info(
        "Demo completed",
        extra={
            "iot_samples_generated": iot_simulator.sample_count,
            "edge_samples_processed": edge_simulator.processed_count,
            "backend_syncs_success": edge_simulator.synced_count,
            "backend_syncs_failed": edge_simulator.failed_count,
            "success_rate": success_rate
        }
    )
    
    print()
    print("=" * 70)
    print("📊 Demo Summary")
    print("=" * 70)
    print(f"IoT Samples Generated: {iot_simulator.sample_count}")
    print(f"Edge Samples Processed: {edge_simulator.processed_count}")
    print(f"Backend Syncs Success: {edge_simulator.synced_count}")
    print(f"Backend Syncs Failed: {edge_simulator.failed_count}")
    print(f"Success Rate: {success_rate:.1f}%")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    # Parse command line args or use environment variables
    backend_url = os.getenv("BACKEND_URL", sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000")
    samples = int(os.getenv("SAMPLES", sys.argv[2] if len(sys.argv) > 2 else "1000"))
    interval = float(os.getenv("INTERVAL_SECONDS", sys.argv[3] if len(sys.argv) > 3 else "1.0"))
    log_level = os.getenv("LOG_LEVEL", "INFO")
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Run demo with observability
    run_integrated_demo(
        backend_url=backend_url,
        samples=samples,
        interval_seconds=interval,
        log_level=log_level,
        environment=environment
    )
