# Fase 2 Optimizada - IoT & Edge Simulators Simplificados

**Fecha**: 14 de Noviembre, 2025  
**Objetivo**: Reducir tiempo de implementación de 4-6 días a **2-3 días**  
**Reducción**: **50% del tiempo** sin pérdida de funcionalidad core

---

## 📊 Resumen Ejecutivo

### Cambios Principales

| Aspecto        | Original (ROADMAP.md)          | Optimizado           | Ahorro     |
| -------------- | ------------------------------ | -------------------- | ---------- |
| **Máquinas**   | 3 (TRUCK-21, MILL-3, BOILER-7) | 1 (TRUCK-21)         | 1 día      |
| **Protocolo**  | HTTP + MQTT                    | Solo HTTP            | 1 día      |
| **Buffer**     | SQLite persistente             | Queue en memoria     | 0.5 días   |
| **Inferencia** | ONNX local en edge             | Solo backend         | 1 día      |
| **Anomalías**  | Sistema complejo de inyección  | Hardcoded progresivo | 0.5 días   |
| **Async**      | AsyncIO completo               | Sync simple          | 0.5 días   |
| **TOTAL**      | **4-6 días**                   | **2-3 días**         | **✂️ 50%** |

---

## 🎯 Archivos Simplificados Creados

### IoT Simulator

```
iot-sim/
├── generator_simplified.py    # ✅ NUEVO - Generador simple TRUCK-21
├── run_demo.py                 # ✅ NUEVO - Demo integrado IoT + Edge
├── generator.py                # ⚠️  ORIGINAL - Mantener para referencia
├── anomalies.py                # ⚠️  ORIGINAL - No usar en mockup
├── config.py                   # ✅ ORIGINAL - Actualizar para versión simple
└── requirements.txt            # ✅ Actualizar (eliminar paho-mqtt)
```

### Edge Simulator

```
edge-sim/
├── main_simplified.py          # ✅ NUEVO - Edge simple sin buffer SQLite
├── main.py                     # ⚠️  ORIGINAL - Mantener para referencia
├── buffer.py                   # ❌ NO USAR en mockup
├── features.py                 # ✅ ORIGINAL - Reutilizar lógica básica
├── sync.py                     # ✅ ORIGINAL - Reutilizar HTTP client
└── requirements.txt            # ✅ Actualizar
```

---

## 🚀 Guía de Implementación (2-3 días)

### Día 1: IoT Simulator Simplificado

#### Objetivos

- [x] Clase `TruckSimulator` con generación de datos
- [x] Rangos normales y de fallo definidos
- [x] Progresión automática: normal → degradación → fallo
- [x] Publicador HTTP simple

#### Implementación

```python
# iot-sim/generator_simplified.py

class TruckSimulator:
    def generate_sample(self):
        """Auto-progresa según sample_count"""
        if self.sample_count < 600:
            return self.generate_normal_data()
        elif self.sample_count < 800:
            return self.generate_degradation_data()
        else:
            return self.generate_failure_data()

class HTTPPublisher:
    def publish(self, data):
        requests.post(f"{backend_url}/ingest/raw", json=data)
```

#### Testing

```bash
cd iot-sim
python generator_simplified.py

# Debería mostrar:
# Sample 1 [normal]: vibration=3.2, temp=75.5, ...
# Sample 601 [degrading]: vibration=5.8, temp=88.2, ...
# Sample 801 [critical]: vibration=18.5, temp=98.7, ...
```

**Tiempo estimado**: 4-6 horas

---

### Día 2: Edge Simulator Mínimo

#### Objetivos

- [x] Clase `FeatureEngine` con SMA, derivadas, min/max
- [x] Queue en memoria (Python `queue.Queue`)
- [x] Cliente HTTP para sync al backend
- [x] Loop principal de procesamiento

#### Implementación

```python
# edge-sim/main_simplified.py

class FeatureEngine:
    def compute_features(self, raw_data):
        """Calcula SMA, derivative, min, max por sensor"""
        for sensor, value in raw_data['metrics'].items():
            self.add_reading(sensor, value)
            features[f"{sensor}_sma"] = self.compute_sma(sensor)
            # ...
        return features

class EdgeSimulator:
    def process_loop(self):
        while True:
            raw = self.queue.get()
            features = self.feature_engine.compute_features(raw)
            self.backend_client.send_raw(raw)
            self.backend_client.send_features(features)
```

#### Testing

```bash
cd edge-sim
python main_simplified.py

# Debería mostrar:
# Processed: 50 | Synced: 50 | Failed: 0
# Processed: 100 | Synced: 100 | Failed: 0
```

**Tiempo estimado**: 4-6 horas

---

### Día 3: Integración y Testing

#### Objetivos

- [ ] Conectar IoT → Edge → Backend
- [ ] Script `run_demo.py` integrado
- [ ] Verificar flujo end-to-end
- [ ] Ajustes y debugging

#### Implementación

```python
# iot-sim/run_demo.py

def run_integrated_demo():
    # Crear queue compartida
    shared_queue = Queue(maxsize=200)

    # Thread IoT: genera datos → queue
    iot_thread = threading.Thread(
        target=iot_function,
        args=(simulator, shared_queue)
    )

    # Thread Edge: lee queue → procesa → backend
    edge_thread = threading.Thread(
        target=edge_function,
        args=(edge_sim, shared_queue)
    )

    iot_thread.start()
    edge_thread.start()
```

#### Testing End-to-End

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app:app --reload

# Terminal 2: Demo integrado
cd iot-sim
python run_demo.py

# Debería ver:
# 🚛 IoT: Generated 100/1000 samples [normal]
# 🔄 Edge: Processed 100 | Synced: 100
# ...
# 🚛 IoT: Generated 700/1000 samples [degrading]
# 🔄 Edge: Processed 700 | Synced: 700
```

**Tiempo estimado**: 4-8 horas

---

## ✅ Funcionalidad Mantenida (Core del Mockup)

### 1. Generación de Datos Realistas

- ✅ Sensores industriales (vibración, temperatura, RPM, CO₂, combustible)
- ✅ Rangos operacionales normales
- ✅ Progresión realista hacia fallo

### 2. Feature Engineering

- ✅ Simple Moving Average (SMA)
- ✅ Derivadas (rate of change)
- ✅ Min/Max sobre ventana deslizante
- ✅ Ventana configurable (default: 10 samples)

### 3. Integración con Backend

- ✅ POST `/ingest/raw` - Telemetría cruda
- ✅ POST `/ingest/features` - Features computadas
- ✅ Formato JSON estándar
- ✅ Retry logic básico

### 4. Simulación de Anomalías

- ✅ Operación normal (samples 0-600)
- ✅ Degradación gradual (samples 601-800)
- ✅ Estado crítico/fallo (samples 801+)

### 5. Demostración Arquitectura

- ✅ Separación IoT / Edge / Backend
- ✅ Flujo de datos end-to-end
- ✅ Processing en edge
- ✅ Sync a backend centralizado

---

## ❌ Funcionalidad Removida (No Crítica para Mockup)

### 1. MQTT Broker y Publisher

**Original**: Eclipse Mosquitto broker + paho-mqtt client  
**Eliminado**: Usar solo HTTP REST  
**Razón**: Simplifica deployment, HTTP es suficiente para demo  
**Ahorro**: 1 día (no need broker setup, MQTT config, QoS handling)

### 2. Buffer SQLite Persistente

**Original**: Store-and-forward con SQLite local  
**Eliminado**: Queue en memoria (Python `queue.Queue`)  
**Razón**: Para demo no necesitamos resiliencia offline  
**Ahorro**: 0.5 días (no DB schema, no persistence logic)

### 3. Inferencia ONNX Local

**Original**: Modelo ML en edge vía ONNX Runtime  
**Eliminado**: Toda inferencia en backend  
**Razón**: Edge solo hace feature engineering  
**Ahorro**: 1 día (no ONNX export, no edge deployment)

### 4. Máquinas Adicionales

**Original**: TRUCK-21, MILL-3, BOILER-7  
**Eliminado**: Solo TRUCK-21  
**Razón**: Un tipo de máquina es suficiente para demo  
**Ahorro**: 1 día (no múltiples configuraciones)

### 5. Sistema Complejo de Anomalías

**Original**: Módulo `anomalies.py` con inyección dinámica  
**Eliminado**: Progresión hardcoded en `generate_sample()`  
**Razón**: Patrón progresivo es más predecible para demo  
**Ahorro**: 0.5 días (no logic de detección/inyección)

### 6. AsyncIO Completo

**Original**: async/await en todo el flujo  
**Eliminado**: Código sincrónico simple  
**Razón**: Menor complejidad, threads son suficientes  
**Ahorro**: 0.5 días (no async coordination, simpler debugging)

---

## 📈 Impacto en Timeline General

### Timeline Original (ROADMAP.md)

```
Fase 1: Backend MVP         → 1-2 semanas
Fase 2: IoT/Edge Sims       → 1 semana (4-6 días)
Fase 3: Frontend            → 1-2 semanas
Fase 4: Docker              → 2-3 días
----------------------------------------
TOTAL PARA DEMO:            3-5 semanas
```

### Timeline Optimizado

```
Fase 1: Backend MVP         → 1-2 semanas
Fase 2: IoT/Edge Sims       → 2-3 días ✂️ (50% reducción)
Fase 3: Frontend            → 1-2 semanas
Fase 4: Docker              → 2-3 días
----------------------------------------
TOTAL PARA DEMO:            2.5-4.5 semanas ⚡
```

**Ahorro total**: 2-3 días en Fase 2  
**Beneficio adicional**: Código más simple = menos bugs, más rápido debuggear

---

## 🔄 Migración a Versión Completa (Futuro)

Si en el futuro se necesita la versión completa con MQTT, buffer, etc:

### Paso 1: Agregar MQTT (1 día)

```python
# iot-sim/mqtt_publisher.py
import paho.mqtt.client as mqtt

class MQTTPublisher:
    def publish(self, topic, data):
        self.client.publish(topic, json.dumps(data))
```

### Paso 2: Agregar Buffer SQLite (0.5 días)

```python
# edge-sim/buffer.py
import sqlite3

class LocalBuffer:
    def store(self, data):
        self.conn.execute("INSERT INTO buffer ...")

    def sync_pending(self):
        # Store and forward logic
```

### Paso 3: Agregar Inferencia ONNX (1 día)

```python
# edge-sim/inference.py
import onnxruntime as ort

class LocalInference:
    def predict(self, features):
        return self.session.run(None, features)
```

### Paso 4: Agregar Máquinas (0.5 días)

```python
# iot-sim/config.py
MACHINES = ["TRUCK-21", "MILL-3", "BOILER-7"]
```

**Total para migración**: 3 días

---

## 🎯 Decisión Final

### ✅ Usar Versión Simplificada para:

- Mockup demo inicial
- Pruebas de concepto
- Validación de arquitectura
- Presentaciones a stakeholders

### ⏰ Usar Versión Completa para:

- MVP en producción
- Sites con conectividad pobre
- Deployment a escala
- Edge computing real

---

## 📝 Próximos Pasos

### Esta Semana (Día 1-3)

- [ ] Implementar `generator_simplified.py`
- [ ] Implementar `main_simplified.py`
- [ ] Crear `run_demo.py` integrado
- [ ] Testing end-to-end con backend

### Próxima Semana (Fase 3)

- [ ] Frontend Next.js
- [ ] Dashboard con visualización de datos
- [ ] Gráficos de vibración, temperatura
- [ ] Alertas en UI

---

## 🔗 Referencias

- **ROADMAP.md**: Plan original completo
- **iot-sim/generator.py**: Implementación original (referencia)
- **edge-sim/main.py**: Implementación original (referencia)
- **ARCHITECTURE.md**: Arquitectura hexagonal del sistema

---

**✅ Versión simplificada lista para implementar**

**Tiempo total Fase 2**: 2-3 días  
**Ahorro**: 50% vs plan original  
**Funcionalidad core**: 100% mantenida  
**Complejidad**: Reducida significativamente

¡Manos a la obra! 🚀
