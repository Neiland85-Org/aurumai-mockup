# Quick Reference - Observability

## 🚀 Start Commands

### Backend
```bash
cd backend
source .venv/bin/activate
python -m uvicorn app:app --reload
```

**Endpoints:**
- http://localhost:8000/metrics (Prometheus format)
- http://localhost:8000/health (JSON status)

### IoT Simulator
```bash
cd iot-sim
source ../backend/.venv/bin/activate
python generator_simplified.py
```

**Environment Variables:**
```bash
BACKEND_URL=http://localhost:8000
SAMPLES=1000
INTERVAL_SECONDS=1.0
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Integrated Demo (IoT + Edge)
```bash
cd iot-sim
source ../backend/.venv/bin/activate
python run_demo.py
```

---

## 📝 Log Examples

### Backend Log (JSON)
```json
{
  "timestamp": "2025-11-15T16:28:12.fZ",
  "severity": "INFO",
  "logger": "root",
  "message": "Initializing AurumAI Backend",
  "app_name": "AurumAI Platform",
  "app_version": "0.1.0",
  "environment": "development"
}
```

### IoT Simulator Log (JSON)
```json
{
  "timestamp": "2025-11-15T16:35:12.fZ",
  "severity": "WARNING",
  "logger": "iot-simulator",
  "message": "Circuit breaker state changed",
  "circuit_breaker": "iot-backend-connection",
  "old_state": "closed",
  "new_state": "open",
  "fail_counter": 5,
  "machine_id": "TRUCK-21",
  "environment": "development"
}
```

---

## 🔧 Configuration Quick Reference

### Backend (settings.py)

**Logging:**
- `log_level` = "INFO"
- `log_format` = "json"

**Retry:**
- `retry_max_attempts` = 3
- `retry_base_delay` = 1.0
- `retry_max_delay` = 30.0

**Circuit Breaker:**
- `circuit_breaker_fail_max` = 5
- `circuit_breaker_timeout` = 60.0

**Timeouts:**
- `timeout_connect` = 5.0
- `timeout_read` = 30.0

**Tracing:**
- `tracing_enabled` = False
- `tracing_otlp_endpoint` = ""

### IoT Simulator (observability.py)

**Retry:**
- max_attempts = 3
- base_delay = 1.0
- max_delay = 30.0

**Circuit Breaker:**
- fail_max = 5
- timeout_duration = 60.0

**Timeout:**
- connect = 5.0
- read = 30.0

---

## 🧪 Testing Scenarios

### Test 1: Normal Operation
```bash
# Terminal 1: Backend
cd backend && python -m uvicorn app:app --reload

# Terminal 2: Simulator
cd iot-sim && SAMPLES=100 INTERVAL_SECONDS=0.5 python generator_simplified.py
```
**Expected:** 100% success rate

### Test 2: Backend Failure (Circuit Breaker)
```bash
# Terminal 1: Stop backend (Ctrl+C)

# Terminal 2: Run simulator
cd iot-sim && SAMPLES=100 INTERVAL_SECONDS=0.5 python generator_simplified.py
```
**Expected:**
- First 5 samples: 3 retry attempts each
- Circuit breaker opens after 5 failures
- Remaining samples: Immediate failure (no retries)

### Test 3: Backend Recovery
```bash
# Terminal 1: Restart backend after 30s
cd backend && python -m uvicorn app:app --reload

# Terminal 2: Keep simulator running
```
**Expected:**
- Circuit breaker: OPEN → HALF_OPEN (after 60s)
- Circuit breaker: HALF_OPEN → CLOSED (after success)

---

## 📈 Key Metrics (Prometheus)

```promql
# Request rate
rate(http_requests_total[5m])

# Latency P95
histogram_quantile(0.95, http_request_duration_seconds)

# Error rate
rate(errors_total[5m])

# Circuit breaker state
circuit_breaker_state
```

---

## 🔍 Log Queries

```bash
# All errors
cat logs.json | jq 'select(.severity=="ERROR")'

# Circuit breaker events
cat logs.json | jq 'select(.message | contains("Circuit breaker"))'

# Retry attempts
cat logs.json | jq 'select(.message | contains("Retrying"))'

# By machine_id
cat logs.json | jq 'select(.machine_id=="TRUCK-21")'
```

---

## 📚 Documentation

- [OBSERVABILITY_IMPLEMENTATION.md](OBSERVABILITY_IMPLEMENTATION.md) - Backend architecture
- [OBSERVABILITY_COMPLETE.md](OBSERVABILITY_COMPLETE.md) - Backend quick start
- [IOT_OBSERVABILITY_COMPLETE.md](IOT_OBSERVABILITY_COMPLETE.md) - IoT implementation
- [SESION_OBSERVABILIDAD_RESUMEN.md](SESION_OBSERVABILIDAD_RESUMEN.md) - Session summary
- [iot-sim/README.md](iot-sim/README.md) - IoT simulator guide

---

## ✅ Validation Checklist

- [ ] Backend starts without errors
- [ ] GET /metrics returns Prometheus format
- [ ] GET /health returns JSON status
- [ ] Backend logs are JSON formatted
- [ ] IoT simulator starts without errors
- [ ] IoT simulator publishes data successfully
- [ ] Circuit breaker opens on backend failure
- [ ] Circuit breaker closes on backend recovery
- [ ] Retry attempts logged correctly
- [ ] All contextual fields present in logs

---

**Last Updated:** 2025-11-15  
**Status:** ✅ Production-Ready
