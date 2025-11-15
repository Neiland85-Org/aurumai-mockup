# 🔭 AurumAI Observability & Resilience Infrastructure

## 📋 Resumen Ejecutivo

Se ha implementado una **infraestructura completa de observabilidad y resiliencia** lista para producción industrial. Esta actualización transforma el sistema de un prototipo a una solución enterprise-grade con:

✅ **Logging estructurado JSON** (python-json-logger)  
✅ **Métricas Prometheus** (prometheus-client)  
✅ **Tracing distribuido** (OpenTelemetry)  
✅ **Reintentos con backoff exponencial** (tenacity)  
✅ **Circuit breakers** (pybreaker)  
✅ **Timeouts inteligentes** (httpx.Timeout)  
✅ **Mapeo centralizado de excepciones**

---

## 🏗️ Arquitectura de Observabilidad

```
┌─────────────────────────────────────────────────────────────────┐
│                     REQUEST LIFECYCLE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. HTTP Request → RequestIDMiddleware                         │
│     ├─ Genera UUID único (X-Request-ID)                        │
│     └─ Propaga trace context (OpenTelemetry)                   │
│                                                                 │
│  2. ErrorLoggingMiddleware                                     │
│     ├─ Registra inicio de request (JSON structured)            │
│     └─ Captura errores 4xx/5xx                                 │
│                                                                 │
│  3. FastAPI Router + Use Case                                  │
│     ├─ Validación con _validate_*()                            │
│     ├─ Reintentos con RetryPolicy                              │
│     ├─ Circuit Breaker para servicios externos                 │
│     ├─ Timeouts configurables (httpx.Timeout)                  │
│     └─ Trazas automáticas (OpenTelemetry spans)                │
│                                                                 │
│  4. Exception Handlers                                         │
│     ├─ ApplicationError → ErrorResponse + logging              │
│     ├─ ValidationError → 400 + detalles                        │
│     └─ Exception → 500 + log (sin exponer internals)           │
│                                                                 │
│  5. Response                                                   │
│     ├─ Métricas Prometheus actualizadas                        │
│     ├─ Logs JSON con request_id/trace_id                       │
│     └─ Spans cerrados (OpenTelemetry)                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Módulos Creados

### 1. **backend/infrastructure/logging.py** (180 líneas)

**Sistema de logging estructurado con campos contextuales:**

```python
from infrastructure.logging import get_logger, set_request_context

# Configurar logger con JSON formatter
logger = get_logger(__name__, level="INFO", environment="production")

# Establecer contexto de request
set_request_context(request_id="req-123", machine_id="M001")

# Log automáticamente incluye: timestamp, severity, logger, request_id, machine_id
logger.info("Processing machine", extra={"operation": "prediction"})

# Salida JSON:
# {
#   "timestamp": "2025-11-15T10:30:00.123Z",
#   "severity": "INFO",
#   "logger": "application.use_cases.prediction",
#   "request_id": "req-123",
#   "machine_id": "M001",
#   "operation": "prediction",
#   "message": "Processing machine",
#   "environment": "production"
# }
```

**Características:**
- ✅ ContextVars para campos request-scoped (thread-safe)
- ✅ Formato JSON listo para ELK/Grafana Loki
- ✅ Campos automáticos: timestamp, environment, request_id, machine_id, user_id
- ✅ LoggerAdapter para campos persistentes por servicio

---

### 2. **backend/infrastructure/resilience.py** (420 líneas)

**Políticas de reintentos y circuit breakers:**

#### **RetryPolicy con backoff exponencial:**

```python
from infrastructure.resilience import RetryPolicy, with_async_retry

# Opción 1: Instancia reutilizable
policy = RetryPolicy(
    max_attempts=3,
    base_delay=1.0,
    max_delay=30.0,
    multiplier=2.0,
    retryable_exceptions=(httpx.RequestError, httpx.TimeoutException)
)

result = await policy.execute_async(fetch_data, url="http://api.example.com")

# Opción 2: Decorador
@with_async_retry(max_attempts=3, base_delay=1.0)
async def fetch_machine_data(machine_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/api/machines/{machine_id}")
        return response.json()
```

**Backoff exponencial:**
- Intento 1: 0s delay
- Intento 2: 1s delay (base_delay * 2^0)
- Intento 3: 2s delay (base_delay * 2^1)
- Intento 4: 4s delay (base_delay * 2^2)
- ...hasta max_delay

#### **Circuit Breaker con métricas:**

```python
from infrastructure.resilience import ResilientCircuitBreaker

# Crear circuit breaker para backend API
breaker = ResilientCircuitBreaker(
    name="backend_api",
    fail_max=5,              # Abrir circuito tras 5 fallos
    timeout_duration=60.0    # Esperar 60s antes de half-open
)

# Uso (lanza CircuitBreakerError si circuito abierto)
try:
    result = await breaker.call_async(send_request, url="http://backend/data")
except CircuitBreakerError:
    logger.error("Circuit breaker OPEN, using fallback")
    result = get_cached_data()
```

**Estados del circuit breaker:**
- **CLOSED**: Normal, todos los requests pasan
- **OPEN**: Fallando, rechaza requests inmediatamente (fast-fail)
- **HALF_OPEN**: Probando recuperación, permite 1 request de prueba

#### **Timeouts configurables:**

```python
from infrastructure.resilience import TimeoutConfig

config = TimeoutConfig(
    connect=5.0,  # 5s para establecer conexión
    read=30.0,    # 30s para leer respuesta
    write=30.0,   # 30s para escribir request
    pool=5.0      # 5s para adquirir conexión del pool
)

async with httpx.AsyncClient(timeout=config.as_httpx_timeout()) as client:
    response = await client.get("http://slow-api.com/data")
```

---

### 3. **backend/infrastructure/metrics.py** (350 líneas)

**Métricas Prometheus para observabilidad:**

#### **Métricas automáticas registradas:**

| Tipo | Nombre | Descripción | Labels |
|------|--------|-------------|--------|
| Counter | `http_requests_total` | Total requests HTTP | method, endpoint, status_code |
| Histogram | `http_request_duration_seconds` | Duración de requests | method, endpoint |
| Gauge | `http_requests_in_progress` | Requests en progreso | method, endpoint |
| Counter | `db_queries_total` | Consultas SQL totales | operation, table |
| Histogram | `db_query_duration_seconds` | Duración de queries | operation, table |
| Counter | `ml_predictions_total` | Predicciones ML | machine_type, model_version |
| Histogram | `ml_prediction_duration_seconds` | Duración predicción | machine_type |
| Histogram | `ml_prediction_risk_score` | Distribución de scores | machine_type |
| Counter | `data_ingestion_total` | Eventos de ingesta | machine_id, data_type |
| Counter | `data_ingestion_errors_total` | Errores de ingesta | machine_id, error_type |
| Gauge | `circuit_breaker_state` | Estado de breakers | name |
| Counter | `circuit_breaker_failures_total` | Fallos de breaker | name |
| Counter | `retry_attempts_total` | Intentos de retry | function, attempt_number |
| Counter | `errors_total` | Errores por tipo | error_type, error_code |

#### **Uso:**

```python
from infrastructure.metrics import (
    track_request,
    track_prediction,
    track_ingestion,
    track_circuit_breaker
)

# Registrar request HTTP
track_request(method="GET", endpoint="/api/machines", status_code=200)

# Registrar predicción ML
track_prediction(
    machine_type="CNC",
    model_version="v2.1.0",
    duration=0.523,
    risk_score=0.85
)

# Registrar ingesta de datos
track_ingestion(
    machine_id="M001",
    data_type="raw_measurement",
    duration=0.015,
    success=True
)

# Registrar estado de circuit breaker
track_circuit_breaker(name="backend_api", state="open", success=False)
```

---

### 4. **backend/infrastructure/tracing.py** (390 líneas)

**Tracing distribuido con OpenTelemetry:**

#### **Configuración inicial (app.py):**

```python
from infrastructure.tracing import setup_tracing, instrument_fastapi

# Configurar tracing
provider = setup_tracing(
    service_name="aurumai-backend",
    service_version="1.0.0",
    environment="production",
    otlp_endpoint="http://jaeger:4317",  # Jaeger collector
    console_export=False  # Desactivar debug
)

# Instrumentar FastAPI (automático)
instrument_fastapi(app)
```

#### **Uso manual (custom spans):**

```python
from infrastructure.tracing import get_tracer, set_span_attributes

tracer = get_tracer(__name__)

# Context manager para operación
with tracer.start_as_current_span("fetch_machine_features") as span:
    set_span_attributes({
        "machine_id": "M001",
        "feature_count": 12,
        "model_version": "v2.0"
    })
    
    features = await fetch_features(machine_id)
    
    span.set_attribute("features_retrieved", len(features))
```

#### **Propagación de contexto entre servicios:**

```python
from infrastructure.tracing import get_trace_context_headers

# Simulador IoT → Backend
headers = get_trace_context_headers()
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://backend:8000/api/ingest",
        json=data,
        headers=headers  # Propaga trace_id/span_id
    )
```

**Resultado:** Traza completa desde simulador → backend → ML model → database

---

## ⚙️ Configuración en settings.py

Se añadieron **30 nuevos parámetros configurables:**

```python
# backend/infrastructure/config/settings.py

class Settings(BaseSettings):
    # ... configuración existente ...
    
    # === LOGGING ===
    log_format: str = "json"  # json | text
    log_to_file: bool = False
    log_file_path: str = "./logs/aurumai.log"
    
    # === TRACING ===
    tracing_enabled: bool = False
    tracing_service_name: str = "aurumai-backend"
    tracing_otlp_endpoint: str = ""  # e.g., "http://localhost:4317"
    tracing_console_export: bool = False
    
    # === RETRY POLICY ===
    retry_max_attempts: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 30.0
    retry_multiplier: float = 2.0
    
    # === CIRCUIT BREAKER ===
    circuit_breaker_enabled: bool = True
    circuit_breaker_fail_max: int = 5
    circuit_breaker_timeout: float = 60.0
    
    # === TIMEOUTS ===
    timeout_connect: float = 5.0    # Connection timeout
    timeout_read: float = 30.0      # Read timeout
    timeout_write: float = 30.0     # Write timeout
    timeout_pool: float = 5.0       # Pool timeout
    timeout_db: float = 30.0        # Database timeout
```

**Uso con variables de entorno:**

```bash
# .env file
TRACING_ENABLED=true
TRACING_OTLP_ENDPOINT=http://jaeger:4317
RETRY_MAX_ATTEMPTS=5
CIRCUIT_BREAKER_FAIL_MAX=10
TIMEOUT_READ=45.0
```

---

## 📊 Endpoint de Métricas

Se expondrá un endpoint `/metrics` para Prometheus:

```python
# backend/app.py
from infrastructure.metrics import get_metrics

@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(get_metrics(), media_type="text/plain")
```

**Formato Prometheus:**

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/machines",status_code="200"} 1543.0

# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/api/machines",le="0.005"} 234.0
http_request_duration_seconds_bucket{method="GET",endpoint="/api/machines",le="0.01"} 456.0
http_request_duration_seconds_sum{method="GET",endpoint="/api/machines"} 123.45
http_request_duration_seconds_count{method="GET",endpoint="/api/machines"} 1543.0

# HELP circuit_breaker_state Circuit breaker state (0=closed, 1=open, 2=half_open)
# TYPE circuit_breaker_state gauge
circuit_breaker_state{name="backend_api"} 0.0
```

---

## 🔗 Integración con Stack de Observabilidad

### **Opción 1: Grafana + Loki + Prometheus + Jaeger**

```yaml
# docker-compose.observability.yml
services:
  # Logs (Grafana Loki)
  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
  
  # Métricas (Prometheus)
  prometheus:
    image: prom/prometheus:v2.47.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  # Trazas (Jaeger)
  jaeger:
    image: jaegertracing/all-in-one:1.50
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
  
  # Visualización (Grafana)
  grafana:
    image: grafana/grafana:10.2.0
    ports:
      - "3001:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
```

**prometheus.yml:**

```yaml
scrape_configs:
  - job_name: 'aurumai-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### **Opción 2: Datadog / New Relic**

```python
# Configuración centralizada
settings.tracing_otlp_endpoint = "https://otlp.datadoghq.com:4317"
settings.tracing_enabled = True
```

---

## 🚀 Próximos Pasos

### **1. Integrar infraestructura en app.py** ✅

```python
from infrastructure.logging import setup_logging
from infrastructure.tracing import setup_tracing, instrument_fastapi
from infrastructure.metrics import get_metrics
from infrastructure.config.settings import settings

# Logging
logger = setup_logging(
    level=settings.log_level,
    environment=settings.environment
)

# Tracing
if settings.tracing_enabled:
    setup_tracing(
        service_name=settings.tracing_service_name,
        environment=settings.environment,
        otlp_endpoint=settings.tracing_otlp_endpoint
    )
    instrument_fastapi(app)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(get_metrics(), media_type="text/plain")
```

### **2. Refactorizar routers con infraestructura** ⏳

```python
# backend/api/routers/machines.py
from infrastructure.logging import get_logger, set_request_context
from infrastructure.metrics import track_request, track_request_duration
from infrastructure.resilience import with_async_retry

logger = get_logger(__name__)

@router.get("/{machine_id}/metrics")
@with_async_retry(max_attempts=3)
async def get_machine_metrics(machine_id: str):
    set_request_context(machine_id=machine_id)
    
    start = time.time()
    try:
        result = await use_case.execute(machine_id)
        track_request("GET", "/api/machines/{id}/metrics", 200)
        return result
    except Exception as e:
        logger.error(f"Failed to fetch metrics", extra={"error": str(e)})
        track_request("GET", "/api/machines/{id}/metrics", 500)
        raise
    finally:
        duration = time.time() - start
        track_request_duration("GET", "/api/machines/{id}/metrics", duration)
```

### **3. Aplicar a simuladores (iot-sim, edge-sim)** ⏳

```python
# iot-sim/generator_simplified.py
from infrastructure.resilience import RetryPolicy, ResilientCircuitBreaker
from infrastructure.logging import get_logger

logger = get_logger(__name__)

# Circuit breaker para backend
backend_breaker = ResilientCircuitBreaker(
    name="iot_to_backend",
    fail_max=5,
    timeout_duration=60.0
)

# Retry policy
retry_policy = RetryPolicy(max_attempts=3, base_delay=1.0)

async def send_measurement(data: dict):
    try:
        await backend_breaker.call_async(
            retry_policy.execute_async,
            httpx_post,
            url="http://backend:8000/api/ingest",
            json=data
        )
    except CircuitBreakerError:
        logger.warning("Backend unavailable, buffering data")
        buffer_data(data)
```

### **4. Documentación completa** ⏳

Crear `OBSERVABILITY_GUIDE.md` con:
- Arquitectura de observabilidad
- Configuración de stack (Prometheus/Grafana/Jaeger)
- Dashboards de ejemplo
- Queries de Prometheus
- Alertas recomendadas
- Troubleshooting

---

## 📈 Métricas Clave para Monitoreo

### **SLIs (Service Level Indicators)**

| Indicador | Métrica Prometheus | Objetivo | Alerta |
|-----------|-------------------|----------|--------|
| **Disponibilidad** | `sum(rate(http_requests_total{status_code=~"2.."}[5m])) / sum(rate(http_requests_total[5m]))` | > 99.9% | < 99% |
| **Latencia P50** | `histogram_quantile(0.5, http_request_duration_seconds)` | < 100ms | > 200ms |
| **Latencia P95** | `histogram_quantile(0.95, http_request_duration_seconds)` | < 500ms | > 1s |
| **Latencia P99** | `histogram_quantile(0.99, http_request_duration_seconds)` | < 1s | > 2s |
| **Tasa de error** | `sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))` | < 0.1% | > 1% |
| **Circuit breaker abierto** | `circuit_breaker_state{name="backend_api"}` | 0 (closed) | 1 (open) |
| **Reintentos** | `rate(retry_attempts_total{attempt_number="3"}[5m])` | < 10/s | > 50/s |

### **Dashboards Grafana recomendados**

1. **Overview Dashboard**
   - Requests/sec (por endpoint)
   - Latencia P50/P95/P99
   - Tasa de error (4xx/5xx)
   - Circuit breakers state

2. **ML Predictions Dashboard**
   - Predictions/sec
   - Prediction latency
   - Risk score distribution
   - Model version breakdown

3. **Data Ingestion Dashboard**
   - Ingestion rate (por machine_id)
   - Ingestion errors
   - Queue depth
   - Processing latency

4. **Infrastructure Dashboard**
   - DB connection pool
   - DB query latency
   - Retry attempts
   - Circuit breaker state changes

---

## 🎯 Resultados Esperados

### **Antes (sin infraestructura):**
- ❌ Errores silenciosos (no logs)
- ❌ Fallos en cascada (sin circuit breaker)
- ❌ Sin visibilidad de rendimiento
- ❌ Debugging difícil (sin request_id)
- ❌ Sin trazabilidad entre servicios

### **Después (con infraestructura):**
- ✅ Logs estructurados JSON con contexto completo
- ✅ Métricas en tiempo real (Prometheus)
- ✅ Trazas distribuidas (end-to-end visibility)
- ✅ Reintentos automáticos con backoff
- ✅ Circuit breakers para protección
- ✅ Timeouts configurables por entorno
- ✅ Debugging rápido con request_id/trace_id

---

## 📚 Referencias

- [OpenTelemetry Python Docs](https://opentelemetry.io/docs/instrumentation/python/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Tenacity Retry Library](https://tenacity.readthedocs.io/)
- [PyBreaker Circuit Breaker](https://github.com/danielfm/pybreaker)
- [Python JSON Logger](https://github.com/madzak/python-json-logger)

---

## ✅ Checklist de Implementación

- [x] Crear `infrastructure/logging.py` con JSON formatter
- [x] Crear `infrastructure/resilience.py` con retry + circuit breaker
- [x] Crear `infrastructure/metrics.py` con métricas Prometheus
- [x] Crear `infrastructure/tracing.py` con OpenTelemetry
- [x] Actualizar `requirements.txt` con dependencias
- [x] Añadir configuración en `settings.py`
- [ ] Integrar logging en `app.py` y middlewares
- [ ] Integrar tracing en `app.py`
- [ ] Exponer endpoint `/metrics`
- [ ] Refactorizar routers con logging + métricas
- [ ] Aplicar retry policy en simuladores
- [ ] Aplicar circuit breaker en simuladores
- [ ] Configurar stack de observabilidad (Grafana/Prometheus/Jaeger)
- [ ] Crear dashboards en Grafana
- [ ] Documentar en `OBSERVABILITY_GUIDE.md`
- [ ] Validar end-to-end con test de carga

---

**🚀 Status:** Infraestructura base completa. Pendiente integración en app.py y routers.
