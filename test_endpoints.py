#!/usr/bin/env python3
"""
Quick test script to verify backend ingest endpoints are working
"""

import httpx
from datetime import datetime


def test_ingest_raw():
    """Test POST /ingest/raw endpoint"""
    url = "http://localhost:8000/ingest/raw"
    
    data = {
        "machine_id": "TRUCK-21",
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "vibration": 3.5,
            "temperature": 75.2,
            "rpm": 1500,
            "co2_ppm": 400,
            "fuel_consumption": 25.5
        }
    }
    
    print("🧪 Testing POST /ingest/raw")
    print(f"   URL: {url}")
    print(f"   Data: {data}")
    
    try:
        with httpx.Client() as client:
            response = client.post(url, json=data, timeout=5.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_ingest_features():
    """Test POST /ingest/features endpoint"""
    url = "http://localhost:8000/ingest/features"
    
    data = {
        "machine_id": "TRUCK-21",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "vibration_sma": 3.2,
            "vibration_derivative": 0.1,
            "vibration_min": 2.5,
            "vibration_max": 4.0,
            "temperature_sma": 76.0,
            "temperature_derivative": 0.5,
            "temperature_min": 70.0,
            "temperature_max": 80.0,
            "rpm_sma": 1480.0,
            "rpm_derivative": 10.0,
            "rpm_min": 1400,
            "rpm_max": 1600
        }
    }
    
    print("\n🧪 Testing POST /ingest/features")
    print(f"   URL: {url}")
    print(f"   Data: machine_id={data['machine_id']}, features_count={len(data['features'])}")
    
    try:
        with httpx.Client() as client:
            response = client.post(url, json=data, timeout=5.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 70)
    print("🔍 Testing Backend Ingest Endpoints")
    print("=" * 70)
    print("\n⚠️  Make sure backend is running: python -m uvicorn app:app --reload\n")
    
    # Test raw endpoint
    raw_ok = test_ingest_raw()
    
    # Test features endpoint
    features_ok = test_ingest_features()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print(f"   /ingest/raw:      {'✅ PASS' if raw_ok else '❌ FAIL'}")
    print(f"   /ingest/features: {'✅ PASS' if features_ok else '❌ FAIL'}")
    print("=" * 70)
    
    if raw_ok and features_ok:
        print("\n🎉 All endpoints working! Ready for IoT/Edge integration.")
        return 0
    else:
        print("\n⚠️  Some endpoints failed. Check backend logs.")
        return 1


if __name__ == "__main__":
    exit(main())
