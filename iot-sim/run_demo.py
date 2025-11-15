"""
Integrated IoT + Edge Simulator - SIMPLIFIED VERSION

This script combines IoT data generation and Edge processing
in a single integrated flow for easy testing.

Usage:
    python run_demo.py

Components:
- IoT Simulator: Generates TRUCK-21 telemetry
- Edge Simulator: Processes features and syncs to backend
"""

import threading
import time
import sys
import os
from queue import Queue
from typing import Dict, Any

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'edge-sim'))

from generator_simplified import TruckSimulator
# Edge simulator will be imported from ../edge-sim/main_simplified.py
# For now, we'll use a local implementation


def iot_thread_function(
    simulator: TruckSimulator,
    edge_queue: Queue,
    samples: int = 1000,
    interval_seconds: float = 1.0
):
    """
    IoT thread: Generate data and push to edge queue
    """
    print("🚛 IoT Thread: Starting TRUCK-21 simulator")
    
    for i in range(samples):
        # Generate sample
        data = simulator.generate_sample()
        
        # Push to edge queue (simulating IoT → Edge communication)
        try:
            edge_queue.put(data, block=False)
        except:
            print(f"⚠️  Queue full at sample {i}")
        
        # Log progress
        if (i + 1) % 100 == 0:
            status = data['status']
            print(f"🚛 IoT: Generated {i+1}/{samples} samples [{status}]")
        
        time.sleep(interval_seconds)
    
    print("🚛 IoT Thread: Completed")


def edge_thread_function(
    edge_sim: EdgeSimulator,
    max_iterations: int = 1000
):
    """
    Edge thread: Process data from queue and sync to backend
    """
    print("🔄 Edge Thread: Starting processing loop")
    
    edge_sim.process_loop(max_iterations=max_iterations)
    
    print("🔄 Edge Thread: Completed")


def run_integrated_demo(
    backend_url: str = "http://localhost:8000",
    samples: int = 1000,
    interval_seconds: float = 1.0
):
    """
    Run integrated IoT + Edge demo
    
    Args:
        backend_url: Backend API URL
        samples: Total samples to generate
        interval_seconds: Time between samples
    """
    print("=" * 70)
    print("🏭 AurumAI Mockup - IoT + Edge Integrated Simulator")
    print("=" * 70)
    print()
    print("Configuration:")
    print(f"  📡 Backend URL: {backend_url}")
    print(f"  📊 Total samples: {samples}")
    print(f"  ⏱️  Interval: {interval_seconds}s")
    print(f"  🚛 Machine: TRUCK-21 (mining truck)")
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
        args=(iot_simulator, shared_queue, samples, interval_seconds),
        daemon=True
    )
    
    edge_thread = threading.Thread(
        target=edge_thread_function,
        args=(edge_simulator, samples),
        daemon=True
    )
    
    # Start threads
    iot_thread.start()
    time.sleep(2)  # Let IoT start first
    edge_thread.start()
    
    # Wait for completion
    try:
        iot_thread.join()
        edge_thread.join()
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    
    # Final summary
    print()
    print("=" * 70)
    print("📊 Demo Summary")
    print("=" * 70)
    print(f"IoT Samples Generated: {iot_simulator.sample_count}")
    print(f"Edge Samples Processed: {edge_simulator.processed_count}")
    print(f"Backend Syncs Success: {edge_simulator.synced_count}")
    print(f"Backend Syncs Failed: {edge_simulator.failed_count}")
    
    if edge_simulator.processed_count > 0:
        success_rate = edge_simulator.synced_count / edge_simulator.processed_count * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    # Parse command line args (optional)
    backend_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    samples = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    
    # Run demo
    run_integrated_demo(
        backend_url=backend_url,
        samples=samples,
        interval_seconds=interval
    )
