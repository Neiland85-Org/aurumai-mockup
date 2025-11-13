# AurumAI Platform - Mockup Demo

**Industrial IoT Platform for Predictive Maintenance & ESG Monitoring**

AurumAI Platform es una plataforma industrial multi-vertical diseñada para:

- 🔧 **Mantenimiento Predictivo**: Anticipar fallos de maquinaria antes de que ocurran
- 🌍 **ESG & Carbono**: Calcular y reportar huella de carbono en tiempo real
- ⚡ **Gestión Energética**: Optimizar consumo y costes energéticos
- 💧 **Gestión Hídrica**: Monitorizar uso de agua y vertidos
- 📊 **Analytics**: BI avanzado e insights operacionales

## 🏗️ Arquitectura

Este proyecto implementa **Arquitectura Hexagonal** (Ports & Adapters) con **Domain-Driven Design**:

```
IoT Sensors → Edge Nodes → Backend API → TSDB → ML Engine → Dashboard
                                ↓
                           Domain Core
                    (framework-agnostic)
```

### Estructura del Proyecto

```
aurumai-mockup/
├── backend/              # Backend FastAPI con arquitectura hexagonal
│   ├── domain/           # Core domain (entities, value objects, repositories)
│   ├── application/      # Use cases & application logic
│   ├── infrastructure/   # Adapters (DB, MQTT, ML, ESG)
│   └── api/              # REST API (FastAPI)
│
├── edge-sim/             # Simulador de Edge Node
├── iot-sim/              # Simulador de datos IoT
├── frontend/             # Dashboard Next.js
└── docker-compose.yml    # Orquestación multi-servicio
```

## 🚀 Quick Start

### Opción 1: Docker Compose (Recomendado)

La forma más rápida de levantar el mockup demo completo:

```bash
# Desde la raíz del proyecto
docker compose up --build
```

**Acceder a la demo:**
- 📊 **Dashboard**: [http://localhost:3000](http://localhost:3000)
- 🔧 **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 💚 **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

**Servicios levantados:**
- Backend API (port 8000)
- Frontend Dashboard (port 3000)
- Edge Simulator (port 9000)
- IoT Simulator (background)
- SQLite Database (local volume)

### Opción 2: Setup Manual

Ver [SETUP.md](./SETUP.md) para instrucciones detalladas de setup manual para desarrollo.

### Verificación Rápida

```bash
# Ejecutar tests básicos
./test_setup.sh
```

## 📚 Documentación

### Arquitectura Técnica

Ver [ARCHITECTURE.md](./ARCHITECTURE.md) para detalles completos sobre:
- Arquitectura hexagonal
- Domain-Driven Design
- Entidades del dominio
- Flujos de datos
- Escalabilidad
- Stack tecnológico

### Entidades del Dominio

#### Core Entities

- **Tenant**: Cliente/organización multi-tenant
- **Site**: Ubicación física (mina, planta, facility)
- **Machine**: Activo industrial (truck, mill, boiler, turbine, etc.)
- **Sensor**: Punto de medición (vibration, temp, CO₂, etc.)
- **Alert**: Alertas del sistema (predictive, ESG, operational)
- **Event**: Eventos de mantenimiento y operación

#### ESG Entities

- **EmissionSource**: Fuentes de emisiones GHG (Scope 1/2/3)
- **EmissionFactor**: Factores de conversión IPCC/EPA/custom
- **EmissionRecord**: Registros calculados de emisiones

## 🔧 Desarrollo

### Estructura del Backend (Hexagonal)

```
backend/
├── domain/                    # ❤️  Core (NO dependencies externas)
│   ├── entities/              # Aggregates & Entities
│   ├── value_objects/         # Immutable value objects
│   ├── repositories/          # Repository interfaces (Ports)
│   └── services/              # Domain services
│
├── application/               # 🎯 Use Cases
│   ├── use_cases/             # Business workflows
│   └── ports/                 # Application ports
│
├── infrastructure/            # 🔌 Adapters
│   ├── adapters/              # Input/Output adapters
│   ├── db/                    # Database setup
│   └── config/                # Configuration
│
└── api/                       # 🌐 FastAPI entry point
    ├── routers/
    └── main.py
```

## 📝 Roadmap

### ✅ Completado (Mockup Demo Funcional)
- [x] Arquitectura hexagonal base
- [x] Backend FastAPI completo con endpoints REST
- [x] Base de datos SQLite con tablas operacionales
- [x] IoT Simulator con 3 máquinas (TRUCK-21, MILL-3, BOILER-7)
- [x] Edge Simulator con buffering y feature engineering
- [x] ML Engine fake pero creíble (predictivo)
- [x] ESG Calculator con factores IPCC
- [x] Frontend Next.js con 3 vistas (Overview, Predictivo, ESG)
- [x] Docker Compose orquestación completa
- [x] Datos simulados realistas con anomalías programadas

### 🎯 Estado Actual: **MOCKUP DEMO LISTO**

El proyecto está **listo para demo comercial**. Puedes:
- Presentarlo a inversores
- Mostrarlo a clientes industriales
- Usarlo como base para el producto real

### 🚧 Próximos Pasos para Producción
- [ ] Migrar SQLite → PostgreSQL + TimescaleDB
- [ ] Implementar ML models reales (scikit-learn/XGBoost)
- [ ] Añadir autenticación y multi-tenant real
- [ ] Implementar MQTT broker real (Mosquitto/EMQX)
- [ ] Añadir monitoreo (Prometheus + Grafana)
- [ ] Tests automatizados (pytest + jest)
- [ ] CI/CD pipeline
- [ ] Documentación API completa

## 🔗 Enlaces

- [Documentación de Arquitectura](./ARCHITECTURE.md)
- [FastAPI](https://fastapi.tiangulo.com/)
- [TimescaleDB](https://www.timescale.com/)

---

**Nota**: Este mockup demo está diseñado para escalar a producción sin refactors arquitectónicos mayores. La separación de dominio e infraestructura permite cambiar frameworks, bases de datos y protocolos sin tocar la lógica de negocio.
