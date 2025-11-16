# 📊 Grafana Observability Setup

**Fecha:** 15 de noviembre de 2025  
**Versión:** 1.0.0

---

## 📋 Resumen

Setup completo de Grafana para observabilidad de AurumAI Platform.

### Componentes Incluidos

1. ✅ **Backend Overview Dashboard** - Métricas HTTP, DB, MQTT
2. ✅ **Datasources** - Prometheus + PostgreSQL + TimescaleDB
3. ✅ **Grafana Config** - grafana.ini production-ready
4. ✅ **Provisioning** - Auto-configuración de dashboards

---

## 🚀 Quick Start

### Con Docker Compose

```bash
# Añadir a docker-compose.prod.yml:

services:
  grafana:
    image: grafana/grafana:10.2.0
    container_name: aurumai-grafana
    ports:
      - "3001:3000"
    volumes:
      - ./grafana/grafana.ini:/etc/grafana/grafana.ini
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    depends_on:
      - prometheus
      - backend
    networks:
      - aurumai-network
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:v2.48.0
    container_name: aurumai-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    networks:
      - aurumai-network
    restart: unless-stopped

volumes:
  grafana-data:
  prometheus-data:
```

### Levantar Stack Completo

```bash
# Build y start
docker-compose -f docker-compose.prod.yml up -d

# Verificar logs
docker-compose -f docker-compose.prod.yml logs -f grafana

# Acceder a Grafana
open http://localhost:3001
```

---

## 🔐 Credenciales Default

```bash
# Grafana Login
Usuario: admin
Password: <GRAFANA_ADMIN_PASSWORD from .env>

# Cambiar password en primer login
```

---

## 📊 Dashboards Disponibles

### 1. Backend Overview

**Ubicación:** `grafana/dashboards/backend-overview.json`

**Panels:**

1. **HTTP Request Rate** - Requests por segundo por endpoint
2. **HTTP Response Time** - p95 y p99 latency
3. **Success Rate** - % de respuestas 2xx
4. **Error Rate** - Rate de errores 5xx
5. **Active DB Connections** - Conexiones PostgreSQL activas
6. **Memory Usage** - Uso de memoria del backend
7. **Database Query Duration** - Tiempo promedio de queries
8. **MQTT Messages** - Rate de mensajes MQTT recibidos
9. **HTTP Status Codes** - Distribution de status codes

**Acceso:** http://localhost:3001/d/aurumai-backend

### 2. ESG Metrics (Futuro)

```json
{
  "title": "AurumAI - ESG Carbon Tracking",
  "panels": [
    "Total CO2 Emissions",
    "Energy Consumption",
    "Carbon Intensity by Machine",
    "Waste Recycling Rate",
    "Water Usage"
  ]
}
```

### 3. Machine Learning (Futuro)

```json
{
  "title": "AurumAI - ML Model Performance",
  "panels": [
    "Prediction Accuracy",
    "Model Inference Time",
    "Training Job Status",
    "Feature Drift Detection"
  ]
}
```

---

## 📝 Configuración de Prometheus

### Crear `prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: "aurumai-prod"
    environment: "production"

scrape_configs:
  # Backend FastAPI metrics
  - job_name: "aurumai-backend"
    static_configs:
      - targets: ["backend:8000"]
    metrics_path: "/metrics"
    scrape_interval: 5s

  # Prometheus self-monitoring
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  # PostgreSQL Exporter (opcional)
  - job_name: "postgres"
    static_configs:
      - targets: ["postgres-exporter:9187"]

  # MQTT Exporter (opcional)
  - job_name: "mqtt"
    static_configs:
      - targets: ["mqtt-exporter:9234"]
```

---

## 🔧 Configuración Avanzada

### Alerting Rules

Crear `prometheus/alerts.yml`:

```yaml
groups:
  - name: backend_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) 
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      # Slow response time
      - alert: SlowResponseTime
        expr: |
          histogram_quantile(0.95, 
            rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow API response time"
          description: "p95 latency is {{ $value }}s"

      # High memory usage
      - alert: HighMemoryUsage
        expr: |
          process_resident_memory_bytes{job="aurumai-backend"} 
          / 1024 / 1024 > 500
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}MB"

      # Database connection pool exhausted
      - alert: DatabasePoolExhausted
        expr: db_connections_active{job="aurumai-backend"} > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool exhausted"
          description: "Active connections: {{ $value }}"
```

### Notification Channels

Configurar en Grafana UI:

```bash
# Email
1. Alerting → Notification channels
2. New channel → Email
3. Addresses: ops@aurumai.com
4. Test y Save

# PagerDuty
1. Alerting → Notification channels
2. New channel → PagerDuty
3. Integration Key: <YOUR_KEY>
4. Test y Save
```

---

## 📈 Queries Útiles

### PromQL Examples

```promql
# Request rate por endpoint
rate(http_requests_total{job="aurumai-backend"}[5m])

# P95 latency
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m]))

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m]))
/ sum(rate(http_requests_total[5m]))

# DB query time avg
rate(db_query_duration_seconds_sum[5m])
/ rate(db_query_duration_seconds_count[5m])

# MQTT message rate
rate(mqtt_messages_received_total[5m])

# Memory usage MB
process_resident_memory_bytes / 1024 / 1024

# Active DB connections
db_connections_active
```

---

## 🌐 Acceso Cloud

### Railway

```bash
# Añadir servicio Grafana
1. Add Service → Docker Image
2. Image: grafana/grafana:10.2.0
3. Port: 3000
4. Variables: GF_SECURITY_ADMIN_PASSWORD

# Domain
grafana-aurumai.railway.app
```

### Cloud Run

```bash
# No recomendado (stateful)
# Mejor usar Grafana Cloud (free tier)
```

### Grafana Cloud (Recomendado)

```bash
# Free tier:
- 10K metrics series
- 14 días retention
- 3 dashboards

# Conectar:
1. Signup: https://grafana.com/auth/sign-up/create-user
2. Get API key
3. Configure Prometheus remote_write:

# prometheus.yml
remote_write:
  - url: https://<user-id>.grafana.net/api/prom/push
    basic_auth:
      username: <username>
      password: <grafana-cloud-api-key>
```

---

## 📊 Métricas Personalizadas

### Backend Code

```python
# backend/infrastructure/observability/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Custom metrics
esg_carbon_emissions = Gauge(
    'esg_carbon_emissions_kg_co2',
    'Total carbon emissions in kg CO2',
    ['region', 'machine_type']
)

ml_predictions_total = Counter(
    'ml_predictions_total',
    'Total ML predictions made',
    ['model_version', 'prediction_type']
)

ml_inference_duration = Histogram(
    'ml_inference_duration_seconds',
    'ML model inference time',
    ['model_name']
)

# Usage
esg_carbon_emissions.labels(
    region='EU',
    machine_type='CNC'
).set(1234.56)

ml_predictions_total.labels(
    model_version='v1.0.0',
    prediction_type='anomaly'
).inc()

with ml_inference_duration.labels(
    model_name='anomaly-detector'
).time():
    result = model.predict(data)
```

---

## 🧪 Testing Grafana Setup

```bash
# Verificar Grafana está UP
curl http://localhost:3001/api/health

# Verificar Prometheus está UP
curl http://localhost:9090/-/healthy

# Verificar datasource conectado
curl -u admin:<password> \
  http://localhost:3001/api/datasources

# Listar dashboards
curl -u admin:<password> \
  http://localhost:3001/api/search

# Importar dashboard vía API
curl -X POST \
  -H "Content-Type: application/json" \
  -u admin:<password> \
  -d @grafana/dashboards/backend-overview.json \
  http://localhost:3001/api/dashboards/db
```

---

## 📚 Referencias

- **Grafana Docs:** https://grafana.com/docs/
- **Prometheus Docs:** https://prometheus.io/docs/
- **PromQL Tutorial:** https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Grafana Dashboards:** https://grafana.com/grafana/dashboards/

---

**Última actualización:** 15 Nov 2025  
**Próxima acción:** Levantar Grafana con Docker cuando esté instalado
