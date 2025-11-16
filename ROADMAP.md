# AurumAI Platform - Roadmap de Implementación

## Estado Actual ✅

### Completado (Fundación Arquitectónica)

- ✅ **Arquitectura Hexagonal**: Estructura completa implementada
- ✅ **Domain Layer**:
  - 9 entidades completas (Tenant, Site, Machine, Sensor, Alert, Event,
    EmissionSource, EmissionFactor, EmissionRecord)
  - 3 value objects (Measurement, FeatureVector, Prediction)
  - 6 interfaces de repositorios
- ✅ **Configuración**: Settings con Pydantic, .env.example
- ✅ **Documentación**: ARCHITECTURE.md y README.md completos
- ✅ **Requirements**: Dependencias Python definidas

## Fase 1: Backend MVP Funcional (1-2 semanas)

### 1.1 Application Layer (3-4 días)

**Crear casos de uso principales:**

```
backend/application/use_cases/
├── ingest_telemetry_use_case.py      # Ingesta de telemetría raw
├── compute_features_use_case.py       # Feature engineering
├── run_prediction_use_case.py         # Ejecutar modelo ML
├── raise_alert_use_case.py            # Crear alertas
├── calculate_emissions_use_case.py    # Calcular emisiones
├── register_machine_use_case.py       # Registrar nueva máquina
└── get_machine_metrics_use_case.py    # Obtener métricas
```

**Puertos de aplicación:**

```
backend/application/ports/
├── ml_engine_port.py          # Interface para ML Engine
├── esg_calculator_port.py     # Interface para ESG Calculator
└── notification_port.py       # Interface para notificaciones
```

### 1.2 Infrastructure - Database Layer (2-3 días)

**Implementar repositorios concretos:**

```
backend/infrastructure/adapters/output/postgres/
├── postgres_tenant_repository.py
├── postgres_machine_repository.py
├── postgres_sensor_repository.py
├── postgres_alert_repository.py
├── postgres_event_repository.py
└── postgres_emission_repository.py
```

**Implementar TSDB para métricas:**

```
backend/infrastructure/adapters/output/timescale/
├── timescale_measurement_repository.py
└── timescale_feature_repository.py
```

**Database setup:**

```
backend/infrastructure/db/
├── base.py              # SQLAlchemy Base
├── session.py           # Database sessions
├── models.py            # ORM models (mapping domain → tables)
└── migrations/          # Alembic migrations
    └── versions/
```

### 1.3 Infrastructure - ML & ESG Engines (2-3 días)

**ML Engine básico (modelos fake inicialmente):**

```
backend/infrastructure/adapters/output/ml_engine/
├── simple_ml_engine.py           # Implementación simple
├── model_loader.py               # Carga de modelos
└── predictive_model.py           # Modelo predictivo básico
```

**ESG Calculator:**

```
backend/infrastructure/adapters/output/esg_engine/
├── simple_esg_calculator.py      # Cálculo básico
├── emission_factor_loader.py     # Carga de factores
└── ipcc_factors.py               # Factores IPCC predefinidos
```

### 1.4 API Layer - FastAPI (2-3 días)

**Implementar routers:**

```
backend/api/routers/
├── health.py             # Health check
├── ingest.py             # POST /ingest/raw, /ingest/features
├── machines.py           # CRUD máquinas
├── sensors.py            # CRUD sensores
├── metrics.py            # GET métricas time series
├── predictions.py        # GET predicciones
├── alerts.py             # CRUD alertas
├── events.py             # CRUD eventos
└── esg.py                # ESG endpoints (emisiones, reportes)
```

**Main API:**

```
backend/api/main.py       # FastAPI app con todos los routers
backend/api/dependencies.py  # Dependency injection
backend/api/middleware.py # CORS, logging, etc.
```

### 1.5 Testing (continuo)

```
backend/tests/
├── domain/
│   ├── test_tenant.py
│   ├── test_machine.py
│   ├── test_emission_record.py
│   └── ...
├── application/
│   ├── test_ingest_telemetry.py
│   └── ...
└── infrastructure/
    ├── test_postgres_repositories.py
    └── ...
```

## Fase 2: Edge & IoT Simulators (1 semana)

### 2.1 IoT Simulator (2-3 días)

```
iot-sim/
├── generator.py          # ✅ Esqueleto existe
│   ├── MachineSimulator class
│   ├── generate_normal_data()
│   ├── generate_drift_data()
│   └── generate_failure_data()
│
├── anomalies.py          # ✅ Esqueleto existe
│   ├── inject_vibration_spike()
│   ├── inject_temperature_drift()
│   └── inject_co2_excess()
│
├── config.py             # ✅ Esqueleto existe
│   └── Configuración de máquinas simuladas
│
├── mqtt_publisher.py     # Publicar vía MQTT
└── http_publisher.py     # Publicar vía HTTP REST
```

**Máquinas a simular:**

- TRUCK-21 (mining truck)
- MILL-3 (grinding mill)
- BOILER-7 (industrial boiler)

### 2.2 Edge Simulator (2-3 días)

```
edge-sim/
├── main.py               # ✅ Esqueleto existe
│   └── Main event loop
│
├── buffer.py             # ✅ Esqueleto existe
│   ├── LocalBuffer class (SQLite)
│   └── Store & forward logic
│
├── features.py           # ✅ Esqueleto existe
│   ├── FeatureEngineering class
│   ├── compute_sma()
│   ├── compute_derivative()
│   └── detect_peaks()
│
├── sync.py               # ✅ Esqueleto existe
│   ├── BackendSyncClient
│   └── Batch upload logic
│
├── inference.py          # NEW
│   └── Local ML inference (ONNX)
│
└── config.py             # ✅ Esqueleto existe
    └── Edge configuration
```

## Fase 3: Frontend Dashboard (1-2 semanas)

### 3.1 Setup Next.js (1 día)

```
frontend/
├── src/
│   ├── app/              # Next.js 13+ App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx       # Dashboard home
│   │   ├── predictive/    # Predictive view
│   │   ├── esg/           # ESG view
│   │   └── machines/      # Machines list
│   │
│   ├── components/
│   │   ├── MachineCard.tsx
│   │   ├── MetricCard.tsx
│   │   ├── LineChart.tsx
│   │   ├── AlertFeed.tsx
│   │   └── ESGSummary.tsx
│   │
│   ├── lib/
│   │   ├── api.ts         # API client
│   │   └── types.ts       # TypeScript types
│   │
│   └── styles/
│       └── globals.css    # Tailwind + custom
│
└── public/
    └── assets/
```

### 3.2 Componentes clave (5-7 días)

**Dashboard Principal:**

- Vista general de máquinas
- KPIs: máquinas activas, alertas abiertas, CO₂ hoy
- Mapa de site

**Vista Predictiva:**

- Gráfico de vibración, temperatura, RPM en tiempo real
- Tarjeta "Riesgo de fallo" con ML score
- Histórico de predicciones

**Vista ESG:**

- CO₂eq instantáneo y acumulado
- Desglose por scope (1, 2, 3)
- Gráfico de emisiones por máquina
- Export de reporte PDF/Excel

**Lista de Máquinas:**

- Tabla con filtros
- Estado operacional
- Última predicción
- Alertas activas

## Fase 4: Docker Compose & Deployment (2-3 días)

### 4.1 Docker Compose completo

```yaml
version: "3.9"

services:
  # PostgreSQL (metadata)
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: aurumai
      POSTGRES_PASSWORD: aurumai_dev
      POSTGRES_DB: aurumai
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # TimescaleDB (time series)
  timescaledb:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_USER: aurumai
      POSTGRES_PASSWORD: aurumai_dev
      POSTGRES_DB: aurumai_timeseries
    ports:
      - "5433:5432"
    volumes:
      - timescale_data:/var/lib/postgresql/data

  # MQTT Broker
  mqtt:
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mqtt/config:/mosquitto/config

  # Backend API
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DB_HOST: postgres
      TSDB_HOST: timescaledb
      MQTT_BROKER_HOST: mqtt
    depends_on:
      - postgres
      - timescaledb
      - mqtt
    volumes:
      - ./backend:/app

  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend

  # IoT Simulator
  iot-sim:
    build: ./iot-sim
    environment:
      MQTT_BROKER_HOST: mqtt
      BACKEND_API_URL: http://backend:8000
    depends_on:
      - mqtt
      - backend

  # Edge Simulator
  edge-sim:
    build: ./edge-sim
    environment:
      MQTT_BROKER_HOST: mqtt
      BACKEND_API_URL: http://backend:8000
    depends_on:
      - mqtt
      - backend

volumes:
  postgres_data:
  timescale_data:
```

### 4.2 Dockerfiles

Crear Dockerfiles para:

- backend/Dockerfile
- frontend/Dockerfile
- edge-sim/Dockerfile
- iot-sim/Dockerfile

### 4.3 Scripts de inicialización

```
scripts/
├── init_db.py            # Crear esquema inicial
├── seed_data.py          # Datos de ejemplo (tenants, sites, machines)
├── load_emission_factors.py  # Cargar factores IPCC
└── start_demo.sh         # Script para iniciar demo completa
```

## Fase 5: ML Real & ESG Avanzado (2-3 semanas)

### 5.1 Modelos ML reales

- Entrenar modelo predictivo con datos sintéticos/reales
- Exportar a ONNX
- Integrar en ML Engine
- Métricas de performance (precision, recall, F1)

### 5.2 ESG avanzado

- Cargar factores IPCC completos
- Factores por país (España, Argentina, Chile, etc.)
- Cálculo de Scope 3
- Reportes ESG automatizados (PDF/Excel)
- Integración con GHG Protocol

### 5.3 Features adicionales

- Detección de anomalías (Isolation Forest)
- Forecasting de consumo energético
- Optimización de mantenimiento (calendario óptimo)
- Correlación entre fallos y emisiones

## Fase 6: Producción & Escalabilidad (largo plazo)

### 6.1 Kubernetes deployment

- Helm charts
- Auto-scaling
- Multi-región (EU, LATAM, NA)

### 6.2 Observabilidad

- Prometheus + Grafana
- OpenTelemetry tracing
- Structured logging (ELK stack)
- Alerting (PagerDuty)

### 6.3 Seguridad

- JWT authentication
- RBAC completo
- mTLS para edge nodes
- Secrets management (Vault)
- GDPR compliance

### 6.4 Integraciones

- ERP (SAP, Oracle)
- CMMS (Maximo, SAP PM)
- SCADA real (OPC-UA, Modbus)
- Plataformas ESG (Watershed, Persefoni)

## Priorización por Valor

### Alta prioridad (para demo funcional)

1. ✅ Domain layer completo
2. 🔄 Application use cases básicos
3. 🔄 API REST funcional
4. 🔄 Simuladores IoT/Edge
5. 🔄 Dashboard básico
6. 🔄 Docker Compose

### Media prioridad (para MVP)

1. ML engine real
2. ESG calculator avanzado
3. Dashboard completo
4. Testing exhaustivo
5. Documentación de API

### Baja prioridad (para producción)

1. Kubernetes
2. Multi-región activa
3. Integraciones externas
4. Advanced analytics
5. Mobile app

## Estimaciones Totales

| Fase | Descripción            | Tiempo estimado |
| ---- | ---------------------- | --------------- |
| ✅ 0 | Arquitectura & Domain  | **Completado**  |
| 1    | Backend MVP            | 1-2 semanas     |
| 2    | Edge & IoT Simulators  | 1 semana        |
| 3    | Frontend Dashboard     | 1-2 semanas     |
| 4    | Docker & Deployment    | 2-3 días        |
| 5    | ML Real & ESG Avanzado | 2-3 semanas     |
| 6    | Producción             | 3-6 meses       |

**Total para demo funcional:** 3-5 semanas
**Total para MVP completo:** 2-3 meses
**Total para producción:** 6-12 meses

## Próximos Pasos Inmediatos

### Esta semana

1. Implementar use cases de aplicación (IngestTelemetry, ComputePrediction, CalculateEmissions)
2. Crear repositorios PostgreSQL básicos
3. Implementar routers FastAPI (ingest, machines, metrics)
4. Configurar base de datos con SQLAlchemy

### Próxima semana

1. ML Engine fake funcional
2. ESG Calculator con factores básicos
3. Completar API REST
4. Iniciar IoT simulator

### Semana 3

1. Edge simulator funcional
2. Integración MQTT
3. Iniciar frontend Next.js
4. Docker Compose básico

---

**Nota**: Este roadmap es adaptable. Las prioridades pueden cambiar
según feedback de stakeholders y necesidades del negocio.
