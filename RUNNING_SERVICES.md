# AurumAI - Servicios Corriendo

**Fecha:** 16 de noviembre de 2025 - 02:00 AM  
**Estado:** ✅ TODOS LOS SERVICIOS ACTIVOS

---

## 🎯 Servicios en Ejecución

### ✅ **Backend (FastAPI + Uvicorn)**

**Status:** 🟢 Corriendo  
**URL:** http://localhost:8000  
**Proceso:** `python -m uvicorn app:app --reload`  
**PID:** 66755

**Health Check:**

```json
{
  "status": "healthy",
  "app_name": "AurumAI Platform",
  "app_version": "0.1.0",
  "environment": "development",
  "features": {
    "predictive": true,
    "carbon": true,
    "energy": true,
    "water": false,
    "analytics": true
  },
  "observability": {
    "logging": "json",
    "tracing_enabled": false,
    "prometheus_enabled": true
  }
}
```

**Endpoints Disponibles:**

| Endpoint                               | Descripción          |
| -------------------------------------- | -------------------- |
| http://localhost:8000                  | API Root             |
| http://localhost:8000/health           | Health check         |
| http://localhost:8000/docs             | Swagger UI (OpenAPI) |
| http://localhost:8000/redoc            | ReDoc documentation  |
| http://localhost:8000/api/v1/machines  | Máquinas             |
| http://localhost:8000/api/v1/metrics   | Métricas             |
| http://localhost:8000/api/v1/analytics | Analytics            |
| http://localhost:8000/metrics          | Prometheus metrics   |

---

### ✅ **Frontend (React + Next.js)**

**Status:** 🟢 Corriendo  
**URL:** http://localhost:3000  
**Proceso:** `npm run dev`  
**PID:** 66831

**Características:**

- ⚡ Hot reload activo
- 🎨 TailwindCSS
- 📊 Dashboard de máquinas
- 📈 Gráficos en tiempo real
- 🌐 API integration con backend

**Navegador Simple:** Abierto en VS Code ✅

---

### ⏸️ **Simulador IoT**

**Status:** 🟡 Proceso corriendo pero verificar output  
**Comando:** `python run_demo.py`  
**Directorio:** `/iot-sim`

**Función:**

- Genera datos simulados de sensores
- Publica a MQTT broker
- Simula múltiples máquinas industriales

---

## 🔗 Enlaces Rápidos

### **Frontend:**

- 🏠 Dashboard: http://localhost:3000
- 📊 Máquinas: http://localhost:3000/machines (si existe)

### **Backend API:**

- 📚 Swagger UI: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc
- ❤️ Health: http://localhost:8000/health
- 📊 Metrics: http://localhost:8000/metrics

---

## 🧪 Testing Rápido

### **1. Verificar Health Backend:**

```bash
curl http://localhost:8000/health | jq
```

### **2. Listar Máquinas:**

```bash
curl http://localhost:8000/api/v1/machines | jq
```

### **3. Obtener Métricas:**

```bash
curl http://localhost:8000/api/v1/metrics | jq
```

### **4. Ver Prometheus Metrics:**

```bash
curl http://localhost:8000/metrics
```

### **5. Verificar Frontend:**

```bash
curl -I http://localhost:3000
```

---

## 📊 Arquitectura Activa

```
┌─────────────────────────────────────────────────┐
│            NAVEGADOR (localhost:3000)           │
│              React + Next.js Frontend           │
└────────────────────┬────────────────────────────┘
                     │ HTTP/REST
                     ↓
┌─────────────────────────────────────────────────┐
│          BACKEND API (localhost:8000)           │
│              FastAPI + Uvicorn                  │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │   Database   │  │  TimescaleDB │            │
│  │  PostgreSQL  │  │  (Time-series)│           │
│  └──────────────┘  └──────────────┘            │
│         ↑                  ↑                    │
└─────────┼──────────────────┼────────────────────┘
          │                  │
          │                  │
┌─────────┴──────────────────┴────────────────────┐
│              MQTT Broker (Mosquitto)            │
│                localhost:1883                   │
└────────────────────┬────────────────────────────┘
                     ↑
                     │ MQTT Publish
┌────────────────────┴────────────────────────────┐
│           IoT Simulator (run_demo.py)           │
│         Genera datos de sensores industriales   │
└─────────────────────────────────────────────────┘
```

---

## 🛑 Detener Servicios

### **Opción 1: Desde VS Code**

En el panel de terminales, busca:

- Terminal: **Backend**
- Terminal: **Frontend**
- Terminal: **Simulador IoT**

Presiona `Ctrl + C` en cada uno.

### **Opción 2: Desde la línea de comandos**

```bash
# Detener todos los procesos relacionados
pkill -f "uvicorn app:app"
pkill -f "npm run dev"
pkill -f "run_demo.py"
```

### **Opción 3: Por PID**

```bash
kill 66755  # Backend
kill 66831  # Frontend
```

---

## 🔄 Reiniciar Servicios

### **Usando Tasks de VS Code (Recomendado):**

1. Presiona `Cmd + Shift + P`
2. Escribe: "Tasks: Run Task"
3. Selecciona: "Levantar todo (AurumAI)"

O individualmente:

- "Backend"
- "Frontend"
- "Simulador IoT"

### **Manualmente:**

```bash
# Backend
cd backend
source .venv/bin/activate
python -m uvicorn app:app --reload

# Frontend (nueva terminal)
cd frontend
. ~/.asdf/asdf.sh
npm run dev

# IoT Simulator (nueva terminal)
cd iot-sim
source ../backend/.venv/bin/activate
python run_demo.py
```

---

## 📝 Logs y Debugging

### **Ver Logs de Backend:**

En la terminal "Backend" verás:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [66755]
INFO:     Started server process [67233]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### **Ver Logs de Frontend:**

En la terminal "Frontend" verás:

```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
info  - Linting and checking validity of types...
```

### **Ver Logs de IoT Simulator:**

En la terminal "Simulador IoT" verás mensajes de datos publicados a MQTT.

---

## 🐛 Troubleshooting

### **Puerto 8000 ocupado:**

```bash
# Ver qué proceso está usando el puerto
lsof -ti:8000

# Matar el proceso
kill -9 $(lsof -ti:8000)
```

### **Puerto 3000 ocupado:**

```bash
# Ver qué proceso está usando el puerto
lsof -ti:3000

# Matar el proceso
kill -9 $(lsof -ti:3000)
```

### **Database connection error:**

```bash
# Verificar que PostgreSQL está corriendo
psql -h localhost -U aurumai -d aurumai_dev -c "SELECT 1;"

# Si no está corriendo, iniciarlo
brew services start postgresql@15
```

### **MQTT connection error:**

```bash
# Verificar que Mosquitto está corriendo
brew services list | grep mosquitto

# Si no está corriendo, iniciarlo
brew services start mosquitto
```

---

## ✅ Checklist de Servicios

- [x] Backend API corriendo en :8000
- [x] Frontend corriendo en :3000
- [x] Health check exitoso
- [x] Navegador simple abierto
- [ ] PostgreSQL corriendo (verificar si hay errores)
- [ ] MQTT Broker corriendo (verificar si hay errores)
- [ ] IoT Simulator publicando datos (verificar logs)

---

## 🎉 Estado Actual

**Sistema:** 🟢 OPERACIONAL  
**Backend:** ✅ Healthy  
**Frontend:** ✅ Corriendo  
**API Docs:** ✅ Disponible

**Próximo paso:** Explorar la aplicación en http://localhost:3000

---

**Última verificación:** 16 de noviembre de 2025 - 02:00 AM  
**Uptime:** Recién iniciado  
**Modo:** Development (hot reload activo)
