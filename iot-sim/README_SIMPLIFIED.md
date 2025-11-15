# IoT + Edge Simulators - Versión Simplificada

**Versión**: Mockup Demo (Optimizada)  
**Ahorro de tiempo**: 50% vs versión completa  
**Funcionalidad core**: 100% mantenida

---

## 🎯 Objetivo

Simular el flujo completo de datos industriales:

```
IoT Device (TRUCK-21)
    ↓ Genera telemetría
Edge Gateway
    ↓ Feature engineering
    ↓ Sync HTTP
Backend API
    ↓ Almacena
    ↓ ML Prediction
Dashboard
```

---

## 📁 Archivos

### Versión Simplificada (USAR PARA MOCKUP)

```
iot-sim/
├── generator_simplified.py    # 🟢 Generador simple TRUCK-21
├── run_demo.py                 # 🟢 Demo integrado completo
└── README_SIMPLIFIED.md        # 🟢 Esta documentación

edge-sim/
└── main_simplified.py          # 🟢 Edge processor simple
```

### Versión Original (REFERENCIA)

```
iot-sim/
├── generator.py                # ⚪ Original - async, multi-máquinas
├── anomalies.py                # ⚪ Original - inyección compleja
├── config.py                   # ⚪ Original - configuración
└── requirements.txt            # ⚪ Original - con MQTT

edge-sim/
├── main.py                     # ⚪ Original - async, buffer
├── buffer.py                   # ⚪ Original - SQLite store-and-forward
├── features.py                 # ⚪ Original - feature engineering
└── sync.py                     # ⚪ Original - sync logic
```

---

## 🚀 Quick Start

### Prerequisitos

```bash
# Python 3.9+
python --version

# Dependencias
pip install requests
```

### Opción 1: Demo Integrado (Recomendado)

Ejecuta IoT + Edge juntos en un solo proceso:

```bash
# Terminal 1: Levantar backend
cd backend
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Ejecutar demo
cd iot-sim
python run_demo.py
```

Salida esperada:

```
🏭 AurumAI Mockup - IoT + Edge Integrated Simulator
====================================================================
📡 Backend URL: http://localhost:8000
📊 Total samples: 1000
⏱️  Interval: 1.0s
🚛 Machine: TRUCK-21

🚛 IoT: Generated 100/1000 samples [normal]
🔄 Edge: Processed 100 | Synced: 100 | Failed: 0

🚛 IoT: Generated 700/1000 samples [degrading]
🔄 Edge: Processed 700 | Synced: 700 | Failed: 0

🚛 IoT: Generated 900/1000 samples [critical]
🔄 Edge: Processed 900 | Synced: 900 | Failed: 0
```

### Opción 2: IoT Solo

Solo genera datos y los envía al backend:

```bash
cd iot-sim
python generator_simplified.py
```

### Opción 3: Edge Solo

Solo procesa datos (necesita fuente de datos):

```bash
cd edge-sim
python main_simplified.py
```

---

## 📊 Datos Generados

### TRUCK-21 - Mining Truck

**Sensores**:

- `vibration`: Vibración (mm/s RMS)
- `temperature`: Temperatura motor (°C)
- `rpm`: Revoluciones por minuto
- `co2_ppm`: CO₂ en escape (ppm)
- `fuel_consumption`: Consumo combustible (L/h)

**Rangos Normales**:

```
vibration:         2.0 - 5.0 mm/s
temperature:      70.0 - 85.0 °C
rpm:            1200 - 1800 RPM
co2_ppm:         400 - 800 ppm
fuel_consumption: 25.0 - 35.0 L/h
```

**Rangos de Fallo**:

```
vibration:        15.0 - 25.0 mm/s  ⚠️ Bearing issue
temperature:      95.0 - 105.0 °C   ⚠️ Overheating
co2_ppm:        1200 - 1800 ppm     ⚠️ Incomplete combustion
fuel_consumption: 45.0 - 60.0 L/h   ⚠️ Inefficiency
```

### Progresión de Anomalías

El simulador genera un patrón progresivo predecible:

```
Samples 0-600   (60%): Normal operation
Samples 601-800 (20%): Gradual degradation
Samples 801+    (20%): Critical/failure state
```

**Ejemplo de datos generados**:

```json
// Sample 100 (Normal)
{
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-14T10:23:45.123Z",
  "sample_number": 100,
  "status": "normal",
  "metrics": {
    "vibration": 3.2,
    "temperature": 75.5,
    "rpm": 1450,
    "co2_ppm": 620,
    "fuel_consumption": 28.3
  }
}

// Sample 700 (Degrading)
{
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-14T10:33:45.123Z",
  "sample_number": 700,
  "status": "degrading",
  "metrics": {
    "vibration": 5.8,
    "temperature": 88.2,
    "rpm": 1620,
    "co2_ppm": 950,
    "fuel_consumption": 38.1
  }
}

// Sample 900 (Critical)
{
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-14T10:36:45.123Z",
  "sample_number": 900,
  "status": "critical",
  "metrics": {
    "vibration": 18.5,
    "temperature": 98.7,
    "rpm": 1380,
    "co2_ppm": 1450,
    "fuel_consumption": 52.6
  }
}
```

---

## 🔄 Features Computadas (Edge)

El edge simulator calcula features sobre ventana deslizante:

**Features por sensor**:

- `{sensor}_sma`: Simple Moving Average (ventana: 10 samples)
- `{sensor}_derivative`: Tasa de cambio (current - previous)
- `{sensor}_min`: Mínimo en ventana
- `{sensor}_max`: Máximo en ventana

**Ejemplo**:

```json
{
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-14T10:23:45.123Z",
  "features": {
    "vibration_sma": 3.15,
    "vibration_derivative": 0.08,
    "vibration_min": 2.85,
    "vibration_max": 3.52,
    "temperature_sma": 75.2,
    "temperature_derivative": -0.3,
    ...
  }
}
```

---

## 🎛️ Configuración

### Parámetros de Demo

Editar en `run_demo.py`:

```python
run_integrated_demo(
    backend_url="http://localhost:8000",  # URL del backend
    samples=1000,                          # Total de muestras
    interval_seconds=1.0                   # Intervalo entre muestras
)
```

### Parámetros de Simulador

Editar en `generator_simplified.py`:

```python
class TruckSimulator:
    def __init__(self, machine_id="TRUCK-21"):
        # Cambiar rangos normales
        self.normal_ranges = {
            "vibration": (2.0, 5.0),  # Ajustar aquí
            ...
        }

        # Cambiar rangos de fallo
        self.failure_ranges = {
            "vibration": (15.0, 25.0),  # Ajustar aquí
            ...
        }
```

### Parámetros de Features

Editar en `main_simplified.py`:

```python
edge_simulator = EdgeSimulator(
    backend_url="http://localhost:8000",
    queue_size=200,      # Tamaño de queue en memoria
    window_size=10       # Ventana para SMA, min, max
)
```

---

## 📡 Endpoints del Backend

El simulador envía datos a estos endpoints:

### POST /ingest/raw

Recibe telemetría cruda del IoT

**Request**:

```json
{
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-14T10:23:45.123Z",
  "sample_number": 100,
  "status": "normal",
  "metrics": {
    "vibration": 3.2,
    "temperature": 75.5,
    ...
  }
}
```

**Response**: `200 OK`

### POST /ingest/features

Recibe features computadas del Edge

**Request**:

```json
{
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-14T10:23:45.123Z",
  "features": {
    "vibration_sma": 3.15,
    "vibration_derivative": 0.08,
    ...
  }
}
```

**Response**: `200 OK`

---

## 🐛 Troubleshooting

### Error: Connection refused (backend)

```
❌ Publish failed: Connection refused
```

**Solución**: Verificar que el backend esté corriendo:

```bash
# Verificar backend
curl http://localhost:8000/health

# Si no responde, levantar backend
cd backend
python -m uvicorn app:app --reload
```

### Error: ImportError en run_demo.py

```
ImportError: cannot import name 'EdgeSimulator'
```

**Solución**: El demo integrado necesita acceso al edge-sim. Ejecutar desde iot-sim/:

```bash
cd iot-sim
python run_demo.py
```

### Samples muy rápidos

Si los samples se generan demasiado rápido, ajustar `interval_seconds`:

```python
run_integrated_demo(
    interval_seconds=2.0  # 1 sample cada 2 segundos
)
```

### Queue llena

```
⚠️  Queue full, dropping sample
```

**Solución**: Aumentar `queue_size` en EdgeSimulator:

```python
EdgeSimulator(queue_size=500)  # Default: 200
```

---

## 📈 Próximos Pasos

### Testing

1. Ejecutar `run_demo.py` con backend activo
2. Verificar logs en terminal
3. Verificar datos en base de datos backend
4. Verificar que predicciones ML funcionen

### Integración Frontend

1. Dashboard debe mostrar gráficos en tiempo real
2. Visualizar progresión normal → degradación → fallo
3. Mostrar features computadas
4. Alertas cuando vibración > 15 mm/s

### Docker

1. Crear Dockerfile para iot-sim
2. Crear Dockerfile para edge-sim
3. Agregar a docker-compose.yml
4. Test completo con `docker compose up`

---

## 🔗 Referencias

- **FASE2_OPTIMIZADA.md**: Comparación detallada vs versión completa
- **ROADMAP.md**: Plan general del proyecto
- **backend/api/routers/ingest.py**: Endpoints de ingesta
- **backend/domain/entities/**: Entidades del dominio

---

## ✅ Checklist Pre-Demo

Antes de demostrar a stakeholders:

- [ ] Backend corriendo en `http://localhost:8000`
- [ ] `curl http://localhost:8000/health` responde OK
- [ ] `python run_demo.py` se ejecuta sin errores
- [ ] Logs muestran samples generados y synced
- [ ] Base de datos tiene registros de telemetría
- [ ] Dashboard frontend muestra datos (si está listo)

---

**¡Fase 2 Optimizada lista para usar!** 🚀

Tiempo de implementación: **2-3 días** (vs 4-6 días original)  
Funcionalidad core: **100% mantenida**  
Código más simple: **Menos bugs, más fácil debug**
