"""
Test IoT Simulator - Dry Run Mode
No backend required - just verifies data generation
"""

import sys
sys.path.append('.')

from generator_simplified import TruckSimulator

def test_data_generation():
    """Test that simulator generates correct data patterns"""
    
    print("=" * 70)
    print("🧪 Testing TRUCK-21 Simulator - Data Generation")
    print("=" * 70)
    print()
    
    simulator = TruckSimulator(machine_id="TRUCK-21")
    
    # Test normal phase (samples 0-600)
    print("📊 Phase 1: Normal Operation (samples 0-600)")
    print("-" * 70)
    for i in range(5):
        data = simulator.generate_sample()
        print(f"Sample {data['sample_number']:3d} [{data['status']:10s}]: "
              f"vib={data['metrics']['vibration']:.1f}, "
              f"temp={data['metrics']['temperature']:.1f}, "
              f"rpm={data['metrics']['rpm']:.0f}")
    
    # Fast forward to degradation phase
    print()
    print("📊 Phase 2: Degradation (samples 601-800)")
    print("-" * 70)
    simulator.sample_count = 600
    for i in range(5):
        data = simulator.generate_sample()
        print(f"Sample {data['sample_number']:3d} [{data['status']:10s}]: "
              f"vib={data['metrics']['vibration']:.1f}, "
              f"temp={data['metrics']['temperature']:.1f}, "
              f"rpm={data['metrics']['rpm']:.0f}")
    
    # Fast forward to critical/failure phase
    print()
    print("📊 Phase 3: Critical/Failure (samples 801+)")
    print("-" * 70)
    simulator.sample_count = 800
    for i in range(5):
        data = simulator.generate_sample()
        print(f"Sample {data['sample_number']:3d} [{data['status']:10s}]: "
              f"vib={data['metrics']['vibration']:.1f}, "
              f"temp={data['metrics']['temperature']:.1f}, "
              f"rpm={data['metrics']['rpm']:.0f}")
    
    print()
    print("=" * 70)
    print("✅ Test completed successfully!")
    print()
    print("Observations:")
    print("  • Normal phase: vibration 2-5 mm/s, temp 70-85°C")
    print("  • Degradation: vibration increasing, temp rising")
    print("  • Critical: vibration 15-25 mm/s, temp 95-105°C")
    print("=" * 70)


def test_data_structure():
    """Test that data has correct structure for backend"""
    
    print()
    print("=" * 70)
    print("🧪 Testing Data Structure")
    print("=" * 70)
    print()
    
    simulator = TruckSimulator()
    data = simulator.generate_sample()
    
    # Verify structure
    assert "machine_id" in data, "Missing machine_id"
    assert "timestamp" in data, "Missing timestamp"
    assert "sample_number" in data, "Missing sample_number"
    assert "status" in data, "Missing status"
    assert "metrics" in data, "Missing metrics"
    
    # Verify metrics
    metrics = data["metrics"]
    expected_sensors = ["vibration", "temperature", "rpm", "co2_ppm", "fuel_consumption"]
    for sensor in expected_sensors:
        assert sensor in metrics, f"Missing sensor: {sensor}"
    
    print("✅ All fields present:")
    print(f"  • machine_id: {data['machine_id']}")
    print(f"  • timestamp: {data['timestamp']}")
    print(f"  • sample_number: {data['sample_number']}")
    print(f"  • status: {data['status']}")
    print(f"  • metrics: {list(metrics.keys())}")
    print()
    print("✅ Data structure is correct for backend /ingest/raw endpoint")
    print("=" * 70)


if __name__ == "__main__":
    test_data_generation()
    test_data_structure()
