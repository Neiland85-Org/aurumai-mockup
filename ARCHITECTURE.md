# AurumAI Platform - Arquitectura Técnica

## Visión Global

AurumAI Platform es una plataforma industrial multi-vertical con núcleo común que soporta:

- **AurumAI Predictivo**: Mantenimiento predictivo y salud de maquinaria
- **AurumAI Carbon**: Huella de carbono, emisiones y reporting ESG
- **AurumAI Energy**: Optimización energética y gestión de consumo
- **AurumAI Water**: Gestión de agua de proceso y vertidos
- **AurumAI Analytics**: BI avanzado y analítica cruzada

## Principios Arquitectónicos

### 1. Arquitectura Hexagonal (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────┐
│                     ADAPTERS (Input)                     │
│  REST API │ MQTT │ OPC-UA │ LoRaWAN │ SCADA Import      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  APPLICATION LAYER                       │
│     Use Cases: IngestTelemetry, ComputePrediction,     │
│     GenerateESGReport, RegisterMachine, etc.            │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    DOMAIN LAYER (Core)                   │
│  Entities: Tenant, Site, Machine, Sensor, Alert,        │
│           EmissionSource, EmissionFactor                 │
│  Value Objects: Measurement, FeatureVector, Prediction  │
│  Repositories: Interfaces (Ports)                        │
│  Domain Services: Business Rules                         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   ADAPTERS (Output)                      │
│  PostgreSQL │ TimescaleDB │ ClickHouse │ ML Engine      │
│  Object Storage │ Prometheus │ ESG Calculator           │
└─────────────────────────────────────────────────────────┘
```

### 2. Domain-Driven Design (DDD)

El dominio es el corazón de la aplicación:

- **Aggregates**: Tenant, Site, Machine
- **Entities**: Alert, Event, EmissionSource
- **Value Objects**: Measurement, Prediction, FeatureVector
- **Repositories**: Interfaces para persistencia
- **Domain Services**: Lógica de negocio compleja

### 3. Multi-tenant & Multi-región

- Aislamiento de datos por tenant
- Configuración de residencia de datos por región
- Cumplimiento GDPR/normativas locales

## Estructura del Proyecto

```
aurumai-mockup/
├── backend/
│   ├── domain/                    # Core domain (framework-agnostic)
│   │   ├── entities/              # Aggregates & Entities
│   │   │   ├── tenant.py
│   │   │   ├── site.py
│   │   │   ├── machine.py
│   │   │   ├── sensor.py
│   │   │   ├── alert.py
│   │   │   ├── event.py
│   │   │   ├── emission_source.py
│   │   │   ├── emission_factor.py
│   │   │   └── emission_record.py
│   │   ├── value_objects/         # Immutable value objects
│   │   │   ├── measurement.py
│   │   │   ├── feature_vector.py
│   │   │   └── prediction.py
│   │   ├── repositories/          # Repository interfaces (ports)
│   │   │   ├── tenant_repository.py
│   │   │   ├── machine_repository.py
│   │   │   ├── measurement_repository.py
│   │   │   ├── alert_repository.py
│   │   │   └── emission_repository.py
│   │   └── services/              # Domain services
│   │
│   ├── application/               # Use cases & orchestration
│   │   ├── use_cases/
│   │   │   ├── ingest_telemetry.py
│   │   │   ├── compute_prediction.py
│   │   │   ├── calculate_emissions.py
│   │   │   └── generate_esg_report.py
│   │   └── ports/                 # Application ports
│   │
│   ├── infrastructure/            # Framework & external concerns
│   │   ├── adapters/
│   │   │   ├── input/             # Entry points
│   │   │   │   ├── rest/          # FastAPI controllers
│   │   │   │   ├── mqtt/          # MQTT listeners
│   │   │   │   └── opcua/         # OPC-UA connectors
│   │   │   └── output/            # External integrations
│   │   │       ├── postgres/      # PostgreSQL repositories
│   │   │       ├── timescale/     # TimescaleDB repositories
│   │   │       ├── ml_engine/     # ML model serving
│   │   │       └── esg_engine/    # ESG calculations
│   │   ├── db/                    # Database setup & migrations
│   │   └── config/                # Configuration management
│   │
│   ├── api/                       # API layer (FastAPI)
│   │   ├── routers/
│   │   │   ├── ingest.py
│   │   │   ├── machines.py
│   │   │   ├── predictions.py
│   │   │   ├── alerts.py
│   │   │   └── esg.py
│   │   └── main.py
│   │
│   ├── models/                    # ML models (pickles, ONNX)
│   ├── data/                      # Data files
│   │   ├── raw/
│   │   └── features/
│   └── tests/
│
├── edge-sim/                      # Edge node simulator
│   ├── main.py
│   ├── buffer.py
│   ├── features.py
│   └── sync.py
│
├── iot-sim/                       # IoT data simulator
│   ├── generator.py
│   ├── anomalies.py
│   └── config.py
│
├── frontend/                      # Next.js dashboard
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── lib/
│   └── public/
│
└── docker-compose.yml             # Multi-service orchestration
```

## Entidades del Dominio

### Tenant

- Representa un cliente/organización
- Configuración multi-región y multi-normativa
- Aislamiento de datos

### Site

- Ubicación física (mina, planta, facility)
- Pertenece a un Tenant
- Contiene múltiples Machines

### Machine

- Activo industrial (truck, mill, boiler, turbine, etc.)
- Tiene Sensors asociados
- Centro de mantenimiento predictivo y métricas ESG

### Sensor

- Punto de medición (vibration, temp, pressure, flow, CO₂, etc.)
- Protocolo (Modbus, OPC-UA, MQTT, LoRa)
- Pertenece a una Machine

### Alert

- Alerta generada por el sistema
- Niveles: Info, Warning, Critical, Emergency
- Categorías: Predictive, ESG, Energy, Water, Operational, Safety

### Event

- Eventos operacionales y de mantenimiento
- Tipos: Maintenance, Failure, Repair, Calibration, etc.
- Trazabilidad y auditoría

### EmissionSource

- Fuente de emisiones GHG
- Tipos: Mobile Combustion, Stationary Combustion, Electricity, Process
- Scopes: 1, 2, 3 (GHG Protocol)

### EmissionFactor

- Factores de conversión a CO₂eq
- Fuentes: IPCC, EPA, DEFRA, country-specific
- Versionado y validez temporal

### EmissionRecord

- Registro calculado de emisiones
- Vincula activity data con emission factors
- Base para reporting ESG

## Value Objects

### Measurement

- Punto de dato de sensor individual
- Inmutable
- Incluye timestamp, valor, unidad, calidad

### FeatureVector

- Features ingenierizadas para ML
- Agregaciones, derivadas, estadísticas
- Listo para inferencia

### Prediction

- Salida de modelo ML
- Risk score, confidence, time-to-event
- Tipos: failure, anomaly, emissions, energy

## Flujos de Datos

### 1. Ingesta de Telemetría

```
Sensor → IoT Gateway → Edge Node → Backend API → TSDB
                                       ↓
                                  Feature Store
                                       ↓
                                   ML Engine
                                       ↓
                                   Prediction
                                       ↓
                                     Alert
```

### 2. Cálculo de Emisiones

```
Activity Data (fuel, kWh) → EmissionSource
                                  ↓
                           EmissionFactor
                                  ↓
                           ESG Calculator
                                  ↓
                           EmissionRecord
                                  ↓
                             ESG Report
```

### 3. Mantenimiento Predictivo

```
Raw Measurements → Feature Engineering → ML Prediction
                                              ↓
                                      Risk > Threshold?
                                              ↓
                                           Alert
                                              ↓
                                   Maintenance Event
```

## Escalabilidad

### Fase 1: 100 máquinas

- Backend monolito (FastAPI)
- PostgreSQL + TimescaleDB
- Docker Compose
- Edge nodes simples

### Fase 2: 1,000 máquinas

- API replicada (3-5 instancias)
- TSDB con particiones
- Kafka para ingesta de alta tasa
- Edge con compresión

### Fase 3: 10,000 máquinas

- Microservicios separados
- TSDB distribuido (ClickHouse cluster)
- Back-pressure y QoS por tenant
- Edge con agregación local agresiva

## Tecnologías

### Backend

- **FastAPI**: API REST moderna y rápida
- **Python 3.11+**: Lenguaje principal
- **Pydantic**: Validación y serialización
- **SQLAlchemy**: ORM para metadata
- **TimescaleDB**: Time series para telemetría
- **PostgreSQL**: Metadata y entidades

### Edge

- **Python**: Lógica de edge
- **SQLite**: Buffer local
- **MQTT**: Comunicación con backend
- **ONNX Runtime**: Inferencia local de modelos

### IoT

- **MQTT**: Protocolo principal
- **OPC-UA**: Integración SCADA
- **Modbus**: Sensores industriales
- **LoRaWAN**: Sensores remotos

### ML

- **scikit-learn**: Modelos básicos
- **XGBoost**: Gradient boosting
- **ONNX**: Formato de modelos portable

### Frontend

- **Next.js**: React framework
- **TailwindCSS**: Styling
- **Recharts/D3**: Visualizaciones

### Infraestructura

- **Docker**: Contenedorización
- **Docker Compose**: Orquestación local
- **Kubernetes**: Orquestación producción (futuro)

## Principios de Diseño

### 1. El dominio NO conoce la infraestructura

- Las entidades no saben nada de FastAPI, PostgreSQL o MQTT
- Dependency Inversion: el dominio define interfaces, la infraestructura las implementa

### 2. Adaptadores reemplazables

- Cambias TSDB → el dominio ni se entera
- Cambias protocolo IoT → solo cambias adaptador
- Cambias modelo ML → solo cambias ML Engine adapter

### 3. Multi-vertical desde el día 1

- Dominio común: Tenant, Site, Machine, Sensor
- Verticales = configuración + modelos específicos + vistas
- NO forks de código

### 4. ESG como first-class citizen

- No es un "add-on"
- Misma telemetría sirve para predictivo y ESG
- EmissionSource, EmissionFactor, EmissionRecord en el dominio core

### 5. Edge-first

- Operación offline por diseño
- Store & forward
- Inferencia local cuando sea posible

## Compliance & Seguridad

### Multi-región

- Cluster EU para tenants EU
- Cluster LATAM para tenants LATAM
- Nunca mezclar datos sensibles entre regiones

### GDPR

- Datos técnicos, no personales
- Minimización de datos
- Derecho al olvido implementable

### Seguridad

- TLS 1.2+ obligatorio
- JWT con scopes
- RBAC: admin, operator, viewer, esg_analyst
- Audit logs para cálculos ESG

## Próximos Pasos (Implementación)

### Inmediato

1. ✅ Estructura de dominio completa
2. ✅ Entidades y Value Objects
3. ✅ Interfaces de repositorios
4. ⏳ Implementar casos de uso de aplicación
5. ⏳ Implementar adaptadores FastAPI
6. ⏳ Implementar repositorios PostgreSQL/TimescaleDB
7. ⏳ Crear simuladores funcionales
8. ⏳ Docker Compose completo

### Corto plazo (1-2 semanas)

- ML engine básico (modelos fake → real)
- ESG calculator con factores IPCC
- Dashboard Next.js funcional
- Demo end-to-end

### Medio plazo (1-2 meses)

- Integración MQTT real
- Edge node en hardware real
- Modelos ML entrenados con datos reales
- Multi-tenant operativo

### Largo plazo (3-6 meses)

- Kubernetes deployment
- Multi-región activa
- Catálogo de modelos ML
- Integración con ERP/CMMS externos

## Referencias

- [GHG Protocol](https://ghgprotocol.org/)
- [IPCC Emission Factors](https://www.ipcc-nggip.iges.or.jp/)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [TimescaleDB](https://www.timescale.com/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

**Nota**: Esta arquitectura está diseñada para escalar desde una demo funcional hasta una plataforma industrial multi-región sin refactors arquitectónicos mayores. El secreto está en la separación de responsabilidades y la inversión de dependencias.
