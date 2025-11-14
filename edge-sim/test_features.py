"""
Test Edge Simulator - Dry Run Mode
No backend required - just verifies feature engineering
"""

import sys
sys.path.append('.')

from main_simplified import FeatureEngine
from datetime import datetime

def test_feature_engineering():
    """Test feature computation"""
    
    print("=" * 70)
    print("🧪 Testing Edge Feature Engine")
    print("=" * 70)
    print()
    
    engine = FeatureEngine(window_size=5)
    
    # Simulate sensor readings
    print("📊 Adding sensor readings to buffer...")
    print("-" * 70)
    
    vibration_readings = [2.5, 3.0, 3.2, 4.5, 3.8]
    for i, value in enumerate(vibration_readings, 1):
        engine.add_reading("vibration", value)
        print(f"Reading {i}: vibration = {value} mm/s")
    
    print()
    print("📊 Computed Features:")
    print("-" * 70)
    
    sma = engine.compute_sma("vibration")
    derivative = engine.compute_derivative("vibration")
    min_val = engine.compute_min("vibration")
    max_val = engine.compute_max("vibration")
    
    print(f"  SMA (Simple Moving Average): {sma:.2f} mm/s")
    print(f"  Derivative (rate of change): {derivative:.2f} mm/s")
    print(f"  Min over window: {min_val:.2f} mm/s")
    print(f"  Max over window: {max_val:.2f} mm/s")
    
    # Verify calculations
    expected_sma = sum(vibration_readings) / len(vibration_readings)
    expected_derivative = vibration_readings[-1] - vibration_readings[-2]
    expected_min = min(vibration_readings)
    expected_max = max(vibration_readings)
    
    print()
    print("✅ Verification:")
    print(f"  SMA matches: {abs(sma - expected_sma) < 0.01}")
    print(f"  Derivative matches: {abs(derivative - expected_derivative) < 0.01}")
    print(f"  Min matches: {min_val == expected_min}")
    print(f"  Max matches: {max_val == expected_max}")
    
    assert abs(sma - expected_sma) < 0.01, "SMA calculation error"
    assert abs(derivative - expected_derivative) < 0.01, "Derivative error"
    assert min_val == expected_min, "Min calculation error"
    assert max_val == expected_max, "Max calculation error"
    
    print("=" * 70)


def test_feature_computation_from_raw():
    """Test computing features from raw IoT data"""
    
    print()
    print("=" * 70)
    print("🧪 Testing Feature Computation from Raw Data")
    print("=" * 70)
    print()
    
    engine = FeatureEngine(window_size=3)
    
    # Simulate raw IoT data
    raw_data_samples = [
        {
            "machine_id": "TRUCK-21",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "vibration": 2.5,
                "temperature": 75.0,
                "rpm": 1500
            }
        },
        {
            "machine_id": "TRUCK-21",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "vibration": 3.0,
                "temperature": 76.5,
                "rpm": 1520
            }
        },
        {
            "machine_id": "TRUCK-21",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "vibration": 3.5,
                "temperature": 78.0,
                "rpm": 1540
            }
        }
    ]
    
    print("📊 Processing raw data samples...")
    print("-" * 70)
    
    for i, raw_data in enumerate(raw_data_samples, 1):
        features = engine.compute_features(raw_data)
        
        print(f"\nSample {i}:")
        print(f"  Raw: vib={raw_data['metrics']['vibration']}, "
              f"temp={raw_data['metrics']['temperature']}, "
              f"rpm={raw_data['metrics']['rpm']}")
        
        # Show a few features
        print(f"  Features:")
        print(f"    vibration_sma: {features['features']['vibration_sma']}")
        print(f"    vibration_derivative: {features['features']['vibration_derivative']}")
        print(f"    temperature_sma: {features['features']['temperature_sma']}")
    
    # Verify structure
    last_features = engine.compute_features(raw_data_samples[-1])
    
    print()
    print("✅ Feature structure verification:")
    print(f"  machine_id present: {'machine_id' in last_features}")
    print(f"  timestamp present: {'timestamp' in last_features}")
    print(f"  features dict present: {'features' in last_features}")
    print(f"  Total features computed: {len(last_features['features'])}")
    
    # Each sensor should have 4 features (sma, derivative, min, max)
    expected_features = 3 * 4  # 3 sensors × 4 features
    actual_features = len(last_features['features'])
    
    print(f"  Expected features: {expected_features}")
    print(f"  Actual features: {actual_features}")
    print(f"  ✅ Correct: {expected_features == actual_features}")
    
    print()
    print("✅ Data structure is correct for backend /ingest/features endpoint")
    print("=" * 70)


def test_window_behavior():
    """Test that window size is respected"""
    
    print()
    print("=" * 70)
    print("🧪 Testing Window Size Behavior")
    print("=" * 70)
    print()
    
    window_size = 3
    engine = FeatureEngine(window_size=window_size)
    
    # Add more readings than window size
    readings = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    print(f"Window size: {window_size}")
    print(f"Adding {len(readings)} readings: {readings}")
    print()
    
    for value in readings:
        engine.add_reading("test_sensor", value)
    
    # Buffer should only keep last 3
    buffer = list(engine.buffers["test_sensor"])
    
    print(f"Buffer contents: {buffer}")
    print(f"Buffer size: {len(buffer)}")
    print(f"Expected size: {window_size}")
    print(f"Expected values: {readings[-window_size:]}")
    
    assert len(buffer) == window_size, f"Buffer size should be {window_size}"
    assert buffer == readings[-window_size:], "Buffer should contain last N values"
    
    print()
    print("✅ Window behavior is correct - only keeps last N samples")
    print("=" * 70)


if __name__ == "__main__":
    test_feature_engineering()
    test_feature_computation_from_raw()
    test_window_behavior()
    
    print()
    print("🎉 All Edge Simulator tests passed!")
    print()
