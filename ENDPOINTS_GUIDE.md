# Guía de Endpoints - AurumAI Backend API

## 🌐 Acceso a la Documentación Interactiva

**La forma más fácil de probar todos los endpoints:**

```
http://localhost:8000/docs
```

Esta interfaz Swagger permite:

- ✅ Ver todos los endpoints disponibles
- ✅ Probar cada endpoint con un formulario
- ✅ Ver ejemplos de request/response
- ✅ Ejecutar peticiones POST sin cURL

---

## 📋 Endpoints Disponibles

### 1. Health Check

**GET** `/`

```bash
curl http://localhost:8000/
```

**Navegador:**

```
http://localhost:8000/
```

**Respuesta:**

```json
{
  "status": "ok",
  "name": "AurumAI Platform",
  "version": "0.1.0"
}
```

---

### 2. Machines - Listar Todas

**GET** `/machines/`

```bash
curl http://localhost:8000/machines/
```

**Navegador:**

```
http://localhost:8000/machines/
```

**Respuesta:**

```json
[
  {
    "machine_id": "TRUCK-21",
    "type": "haul_truck",
    "site": "Copper Mine - North Pit",
    "status": "operational",
    "last_reading": "2025-11-15T06:40:50.804329"
  }
]
```

---

### 3. Machines - Detalle Específica

**GET** `/machines/{machine_id}`

```bash
curl http://localhost:8000/machines/TRUCK-21
```

**Navegador:**

```
http://localhost:8000/machines/TRUCK-21
```

**Respuesta:**

```json
{
  "machine_id": "TRUCK-21",
  "type": "haul_truck",
  "site": "Copper Mine - North Pit",
  "status": "operational",
  "last_reading": "2025-11-15T06:40:50.804329"
}
```

---

### 4. Machines - Métricas (Time Series)

**GET** `/machines/{machine_id}/metrics`

```bash
curl http://localhost:8000/machines/TRUCK-21/metrics
```

**Navegador:**

```
http://localhost:8000/machines/TRUCK-21/metrics
```

**Respuesta:**

```json
{
  "machine_id": "TRUCK-21",
  "data": [
    {
      "timestamp": "2025-11-15T05:40:00",
      "vibration": 3.45,
      "temperature": 78.23,
      "rpm": 1456.78,
      "co2_ppm": 623.45,
      "fuel_consumption": 28.91
    }
    // ... 60 data points (1 hora)
  ],
  "summary": {
    "avg_vibration": 3.5,
    "avg_temperature": 80.0,
    "avg_rpm": 1500.0,
    "total_readings": 60
  }
}
```

---

### 5. Predictions - ML Predictions

**GET** `/predict?machine_id={id}`

```bash
curl "http://localhost:8000/predict?machine_id=TRUCK-21"
```

**Navegador:**

```
http://localhost:8000/predict?machine_id=TRUCK-21
```

**Respuesta:**

```json
{
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-15T06:41:52.711608",
  "prediction": {
    "failure_probability": 0.065,
    "risk_level": "low",
    "time_to_failure_hours": 377.0,
    "confidence": 0.78
  },
  "recommendations": [
    "Continue normal operation",
    "Standard maintenance schedule"
  ],
  "model_version": "mock-v1.0.0"
}
```

---

### 6. ESG - Current Metrics

**GET** `/esg/current?machine_id={id}`

```bash
curl "http://localhost:8000/esg/current?machine_id=TRUCK-21"
```

**Navegador:**

```
http://localhost:8000/esg/current?machine_id=TRUCK-21
```

**Respuesta:**

```json
{
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-15T06:41:13.468141",
  "carbon": {
    "co2_kg_per_hour": 22.58,
    "co2_total_kg": 725.1,
    "carbon_intensity": 0.678
  },
  "energy": {
    "kwh_consumed": 68.24,
    "efficiency_score": 0.73
  },
  "esg_score": 79.8,
  "rating": "B",
  "trend": "improving"
}
```

---

### 7. ESG - Summary (All Machines)

**GET** `/esg/summary`

```bash
curl http://localhost:8000/esg/summary
```

**Navegador:**

```
http://localhost:8000/esg/summary
```

**Respuesta:**

```json
{
  "timestamp": "2025-11-15T06:41:17.608271",
  "total_machines": 1,
  "summary": {
    "total_co2_kg": 593.95,
    "total_kwh": 51.78,
    "avg_esg_score": 75.4,
    "overall_rating": "B"
  },
  "by_machine": [
    {
      "machine_id": "TRUCK-21",
      "esg_score": 70.6,
      "co2_kg": 840.86,
      "rating": "B"
    }
  ],
  "recommendations": [
    "Consider reducing idle time to improve carbon footprint",
    "Optimize fuel consumption during peak operations",
    "Schedule energy efficiency audit"
  ]
}
```

---

### 8. Ingest - Raw Telemetry (POST)

**POST** `/ingest/raw`

⚠️ **No se puede probar en navegador - Requiere POST con JSON body**

**cURL:**

```bash
curl -X POST http://localhost:8000/ingest/raw \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "TRUCK-21",
    "timestamp": "2024-11-15T08:00:00Z",
    "sample_number": 1,
    "status": "normal",
    "metrics": {
      "vibration": 3.5,
      "temperature": 82.0,
      "rpm": 1500.0,
      "co2_ppm": 650.0,
      "fuel_consumption": 30.0
    }
  }'
```

**Respuesta:**

```json
{
  "status": "success",
  "stored": 1,
  "total": 1
}
```

---

### 9. Ingest - Features (POST)

**POST** `/ingest/features`

⚠️ **No se puede probar en navegador - Requiere POST con JSON body**

**cURL:**

```bash
curl -X POST http://localhost:8000/ingest/features \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "TRUCK-21",
    "timestamp": "2024-11-15T08:00:00Z",
    "features": {
      "vibration_sma": 3.2,
      "vibration_derivative": 0.1,
      "vibration_min": 2.8,
      "vibration_max": 4.1,
      "temperature_sma": 80.5,
      "temperature_derivative": 1.2,
      "temperature_min": 75.0,
      "temperature_max": 85.0
    }
  }'
```

**Respuesta:**

```json
{
  "status": "success",
  "stored": 1,
  "total": 1
}
```

---

### 10. Ingest - Telemetry Stats (GET)

**GET** `/ingest/telemetry/stats`

```bash
curl http://localhost:8000/ingest/telemetry/stats
```

**Navegador:**

```
http://localhost:8000/ingest/telemetry/stats
```

**Respuesta:**

```json
{
  "total_raw": 22,
  "total_features": 23,
  "last_raw": {
    "machine_id": "TRUCK-21",
    "timestamp": "2025-11-15T06:30:14.800017",
    "sample_number": 551,
    "status": "normal",
    "metrics": {
      "vibration": 2.99,
      "temperature": 84.7,
      "rpm": 1211.84,
      "co2_ppm": 654.47,
      "fuel_consumption": 25.38
    }
  },
  "last_features": {
    "machine_id": "TRUCK-21",
    "timestamp": "2025-11-15T06:30:14.800017",
    "features": {
      "vibration_sma": 3.7,
      "vibration_derivative": -1.86,
      "vibration_min": 2.5,
      "vibration_max": 4.85
    }
  }
}
```

---

## 🛠️ Herramientas Recomendadas

### 1. FastAPI Docs (Swagger UI) ⭐ **RECOMENDADO**

```
http://localhost:8000/docs
```

- ✅ Interfaz gráfica interactiva
- ✅ Prueba todos los endpoints (GET y POST)
- ✅ Sin necesidad de instalar nada
- ✅ Schemas y ejemplos incluidos

### 2. cURL (Terminal)

```bash
# Ya instalado en macOS/Linux
curl http://localhost:8000/machines/
```

### 3. HTTPie (Terminal, más legible)

```bash
# Instalar: brew install httpie
http GET http://localhost:8000/machines/
```

### 4. Postman (GUI)

- Descargar: https://www.postman.com/downloads/
- Interfaz gráfica completa
- Guardar colecciones de requests

### 5. VS Code REST Client Extension

```
# Instalar extensión "REST Client"
# Crear archivo .http con requests
GET http://localhost:8000/machines/
```

---

## 📝 Resumen de Métodos HTTP

| Endpoint                  | Método | Navegador | cURL/Postman |
| ------------------------- | ------ | --------- | ------------ |
| `/`                       | GET    | ✅        | ✅           |
| `/machines/`              | GET    | ✅        | ✅           |
| `/machines/{id}`          | GET    | ✅        | ✅           |
| `/machines/{id}/metrics`  | GET    | ✅        | ✅           |
| `/predict`                | GET    | ✅        | ✅           |
| `/esg/current`            | GET    | ✅        | ✅           |
| `/esg/summary`            | GET    | ✅        | ✅           |
| `/ingest/telemetry/stats` | GET    | ✅        | ✅           |
| `/ingest/raw`             | POST   | ❌        | ✅           |
| `/ingest/features`        | POST   | ❌        | ✅           |

---

## 🔧 Troubleshooting

### "404 Not Found"

- Verifica que el endpoint esté escrito correctamente
- Recuerda que `/machines/{id}` necesita un ID real: `/machines/TRUCK-21`

### "Method Not Allowed"

- Estás usando GET en un endpoint POST
- Usa la documentación interactiva: `http://localhost:8000/docs`

### "Failed to fetch" (Frontend)

- Verifica que el backend esté corriendo: `curl http://localhost:8000/`
- Revisa la consola del navegador para más detalles
- CORS debe estar habilitado (ya configurado en el backend)

---

**Última actualización:** 15 de noviembre de 2025
