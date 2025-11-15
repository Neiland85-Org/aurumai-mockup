# IoT Simulator - AurumAI Platform

**Status:** ✅ Production-Ready with Enterprise Observability

## 📋 Overview

Simplified IoT data generator for the AurumAI mockup demo. Simulates a mining truck (TRUCK-21) with progressive failure patterns and enterprise-grade observability.

### Key Features

- 🚛 **Single Machine Simulation:** TRUCK-21 (mining truck)
- 📊 **5 Sensors:** vibration, temperature, rpm, CO2, fuel consumption
- 📈 **Progressive Failure:** Normal → Degradation → Critical
- 🔄 **Resilient HTTP Publishing:** Retry + Circuit Breaker
- 📝 **Structured JSON Logging:** Ready for ELK/Loki/CloudWatch
- ⚙️ **Configurable:** Environment variables support

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd iot-sim
source ../backend/.venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Standalone Simulator

```bash
# Default: 1000 samples, 1s interval, INFO logs
python generator_simplified.py

# Custom configuration
BACKEND_URL=http://localhost:8000 \
SAMPLES=500 \
INTERVAL_SECONDS=0.5 \
LOG_LEVEL=DEBUG \
python generator_simplified.py
```

### 3. Run Integrated Demo (IoT + Edge)

```bash
# Requires edge-sim to be set up
python run_demo.py

# Custom configuration
LOG_LEVEL=INFO SAMPLES=200 python run_demo.py http://localhost:8000 200 1.0
```

---

## 📁 Project Structure

```
iot-sim/
├── observability.py          # Observability infrastructure (NEW)
│   ├── IoTJSONFormatter      # JSON logging formatter
│   ├── setup_logging()       # Logging configuration
│   ├── create_retry_decorator()  # Retry with backoff
│   ├── create_circuit_breaker()  # Circuit breaker
│   └── create_timeout_config()   # Timeout management
│
├── generator_simplified.py   # Main IoT simulator (REFACTORED)
│   ├── TruckSimulator        # Data generation
│   └── HTTPPublisher         # Resilient HTTP client
│
├── run_demo.py              # Integrated demo (REFACTORED)
│   ├── iot_thread_function  # IoT generation thread
│   └── edge_thread_function # Edge processing thread
│
├── config.py                # Configuration constants
├── requirements.txt         # Dependencies (UPDATED)
└── README.md               # This file
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | `http://localhost:8000` | Backend API endpoint |
| `SAMPLES` | `1000` | Total samples to generate |
| `INTERVAL_SECONDS` | `1.0` | Time between samples (seconds) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ENVIRONMENT` | `development` | Environment name (appears in logs) |

### Observability Settings

**Retry Policy:**
- Max attempts: 3
- Base delay: 1.0s
- Max delay: 30.0s
- Backoff: Exponential (x2)

**Circuit Breaker:**
- Fail max: 5 consecutive failures
- Timeout: 60s before recovery attempt
- States: CLOSED → OPEN → HALF_OPEN

**Timeouts:**
- Connect: 5s
- Read: 30s
- Write: 30s
- Pool: 5s

---

## 📊 Data Flow

```
┌─────────────┐
│ TruckSim    │
│ (TRUCK-21)  │
└──────┬──────┘
       │ generate_sample()
       ▼
┌─────────────┐      ┌──────────────┐
│ Data        │      │ Retry        │
│ {metrics}   │─────>│ 3 attempts   │
└─────────────┘      └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Circuit      │
                     │ Breaker      │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ HTTP POST    │
                     │ /ingest/raw  │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Backend      │
                     │ (FastAPI)    │
                     └──────────────┘
```

---

## 📝 Sample Data

### Normal Operation (Samples 0-600)

```json
{
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-15T16:30:00.123456Z",
  "sample_number": 150,
  "status": "normal",
  "metrics": {
    "vibration": 3.45,
    "temperature": 78.2,
    "rpm": 1550,
    "co2_ppm": 650,
    "fuel_consumption": 30.5
  }
}
```

### Degradation (Samples 601-800)

```json
{
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-15T16:40:00.123456Z",
  "sample_number": 650,
  "status": "degrading",
  "metrics": {
    "vibration": 5.2,       // ↑ Increasing
    "temperature": 88.5,    // ↑ Increasing
    "rpm": 1700,
    "co2_ppm": 950,         // ↑ Increasing
    "fuel_consumption": 38.0 // ↑ Increasing
  }
}
```

### Critical/Failure (Samples 801+)

```json
{
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-15T16:50:00.123456Z",
  "sample_number": 850,
  "status": "critical",
  "metrics": {
    "vibration": 18.5,      // ⚠️ HIGH
    "temperature": 102.0,   // ⚠️ HIGH
    "rpm": 1650,
    "co2_ppm": 1500,        // ⚠️ HIGH
    "fuel_consumption": 55.0 // ⚠️ HIGH
  }
}
```

---

## 🧪 Testing

### Import Validation

```bash
cd iot-sim
source ../backend/.venv/bin/activate

python -c "from observability import setup_logging, create_circuit_breaker; \
           from generator_simplified import TruckSimulator, HTTPPublisher; \
           print('✅ Imports OK')"
```

**Expected Output:**
```
✅ IoT Simulator imports OK
✅ Observability infrastructure loaded
```

### Functional Tests

**Test 1: Normal Operation**

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app:app --reload

# Terminal 2: Simulator
cd iot-sim
source ../backend/.venv/bin/activate
SAMPLES=100 INTERVAL_SECONDS=0.5 python generator_simplified.py
```

**Expected:**
- ✅ 100% success rate
- ✅ Circuit breaker stays CLOSED
- ✅ No retry attempts
- ✅ JSON logs with machine_id

**Test 2: Backend Failure (Circuit Breaker Test)**

```bash
# Stop backend in Terminal 1 (Ctrl+C)

# Run simulator in Terminal 2
SAMPLES=100 INTERVAL_SECONDS=0.5 python generator_simplified.py
```

**Expected:**
- ⚠️ First 5 samples: 3 retry attempts each (15 total retries)
- 🔴 Circuit breaker opens after 5 failures
- ⚡ Remaining 95 samples: Immediate failure (no retries)
- 📊 Final stats: Circuit Breaker Blocks: 95

**Test 3: Backend Recovery**

```bash
# Terminal 1: Restart backend after 30s
cd backend
python -m uvicorn app:app --reload

# Terminal 2: Keep simulator running
```

**Expected:**
- 🟡 Circuit breaker: OPEN → HALF_OPEN (after 60s timeout)
- ✅ Circuit breaker: HALF_OPEN → CLOSED (after successful request)
- ✅ Normal operation resumes

---

## 📈 Monitoring

### Key Metrics (from JSON logs)

**1. Publish Success Rate**
```
success_count / total_samples * 100
```
Target: > 99%

**2. Circuit Breaker State**
```
grep "Circuit breaker state changed" logs.json
```
Alert: state="open" for > 5 minutes

**3. Retry Attempts**
```
grep "Retrying" logs.json | wc -l
```
Alert: > 10/minute

**4. HTTP Errors**
```
grep "severity\":\"ERROR" logs.json | jq '.error_type' | sort | uniq -c
```

### Sample Log Queries

**All errors:**
```bash
cat logs.json | jq 'select(.severity=="ERROR")'
```

**Circuit breaker events:**
```bash
cat logs.json | jq 'select(.message | contains("Circuit breaker"))'
```

**Retry attempts:**
```bash
cat logs.json | jq 'select(.message | contains("Retrying"))'
```

**Samples by status:**
```bash
cat logs.json | jq 'select(.status) | .status' | sort | uniq -c
```

---

## 🔍 Troubleshooting

### Issue: Connection Refused

**Error:**
```json
{"severity": "ERROR", "message": "HTTP error publishing data", "error": "Connection refused"}
```

**Solution:**
```bash
# Ensure backend is running
cd backend
python -m uvicorn app:app --reload
```

### Issue: Circuit Breaker Always Open

**Error:**
```json
{"severity": "WARNING", "message": "Circuit breaker open - backend unavailable"}
```

**Causes:**
1. Backend is down
2. Backend URL is incorrect
3. Network connectivity issue

**Solution:**
```bash
# Check backend health
curl http://localhost:8000/health

# Verify BACKEND_URL
echo $BACKEND_URL

# Wait for circuit breaker timeout (60s)
# Or restart simulator
```

### Issue: Import Error (pybreaker not found)

**Error:**
```
ModuleNotFoundError: No module named 'pybreaker'
```

**Solution:**
```bash
cd iot-sim
source ../backend/.venv/bin/activate
pip install -r requirements.txt
```

### Issue: High Retry Rate

**Symptom:** Many retry attempts in logs

**Causes:**
1. Backend overloaded
2. Network latency
3. Timeout too short

**Solution:**
```python
# Increase timeout in observability.py
timeout = create_timeout_config(
    connect=10.0,  # Increase from 5.0
    read=60.0,     # Increase from 30.0
)
```

---

## 📚 API Reference

### TruckSimulator

```python
simulator = TruckSimulator(machine_id="TRUCK-21")
data = simulator.generate_sample()
```

**Returns:**
```python
{
    "machine_id": str,
    "timestamp": str,  # ISO 8601
    "sample_number": int,
    "status": str,  # "normal" | "degrading" | "critical"
    "metrics": {
        "vibration": float,
        "temperature": float,
        "rpm": int,
        "co2_ppm": float,
        "fuel_consumption": float
    }
}
```

### HTTPPublisher

```python
from observability import setup_logging

logger = setup_logging(level="INFO")
publisher = HTTPPublisher(
    backend_url="http://localhost:8000",
    logger=logger,
    max_retries=3,
    circuit_breaker_enabled=True
)

success = publisher.publish(data)  # Returns bool
```

### run_simulator

```python
run_simulator(
    backend_url="http://localhost:8000",
    samples=1000,
    interval_seconds=1.0,
    log_level="INFO",
    environment="development"
)
```

---

## 🔗 Related Documentation

- [Backend Observability Guide](../OBSERVABILITY_COMPLETE.md)
- [IoT Observability Details](../IOT_OBSERVABILITY_COMPLETE.md)
- [Architecture Overview](../ARCHITECTURE.md)

---

## 📄 License

See [LICENSE](../LICENSE) and [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)

---

**Last Updated:** 2025-11-15  
**Status:** ✅ Production-Ready
