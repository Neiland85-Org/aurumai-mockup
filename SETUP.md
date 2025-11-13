# AurumAI Mockup - Setup Guide

## 🚀 Quick Start con Docker (Recomendado)

La forma más rápida de levantar toda la demo:

```bash
# Desde la raíz del proyecto
docker compose up --build
```

Esto levantará:
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
- **Edge Simulator**: [http://localhost:9000](http://localhost:9000)
- **IoT Simulator**: (background process)

## 📦 Setup Manual (Desarrollo)

### 1. Backend

```bash
cd backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos
python infrastructure/db/database.py

# Arrancar servidor
uvicorn app:app --reload --port 8000
```

Backend disponible en: [http://localhost:8000](http://localhost:8000)

### 2. Edge Simulator

```bash
cd edge-sim

# Activar el mismo venv o crear uno nuevo
source ../backend/venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Arrancar edge node
python main.py
```

Edge disponible en: [http://localhost:9000](http://localhost:9000)

### 3. IoT Simulator

```bash
cd iot-sim

# Activar venv
source ../backend/venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Arrancar simulador
python generator.py
```

Verás logs de telemetría siendo enviada al Edge.

### 4. Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Desarrollo
npm run dev

# O build para producción
npm run build
npm run start
```

Frontend disponible en: [http://localhost:3000](http://localhost:3000)

## 🔍 Verificación

Una vez todo arrancado, verifica que funciona:

1. **Health checks**:
   - Backend: [http://localhost:8000/health](http://localhost:8000/health)
   - Edge: [http://localhost:9000](http://localhost:9000)

2. **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

3. **Dashboard**: [http://localhost:3000](http://localhost:3000)
   - Deberías ver 3 máquinas: TRUCK-21, MILL-3, BOILER-7
   - Click en "Predictive Maintenance" para ver predicciones en tiempo real
   - Click en "ESG / Carbon" para ver emisiones

## 🐛 Troubleshooting

### Backend no arranca
- Verifica que el puerto 8000 esté libre: `lsof -i :8000`
- Revisa que todas las dependencias estén instaladas
- Chequea los logs de uvicorn

### Edge no se conecta al backend
- Verifica que el backend esté corriendo
- Revisa la variable `BACKEND_HOST` en `.env`
- En Docker, usa `backend` como host; en local usa `localhost`

### IoT no envía datos
- Verifica que Edge esté corriendo
- Revisa la variable `EDGE_HOST` en `.env`
- Chequea los logs del simulador

### Frontend no carga datos
- Verifica `NEXT_PUBLIC_API_BASE` en `.env`
- Abre la consola del navegador para ver errores
- Verifica CORS en el backend (ya está configurado)

## 🎯 Demo Flow

1. **Arrancar todo** con `docker compose up --build`

2. **Esperar ~30 segundos** para que:
   - Backend inicialice la DB
   - IoT Simulator empiece a enviar datos
   - Edge sincronice con backend

3. **Abrir Dashboard** en [http://localhost:3000](http://localhost:3000)

4. **Ver Overview**: 3 máquinas operacionales

5. **Ir a Predictive**:
   - Seleccionar una máquina
   - Ver el risk score actualizarse cada 5 segundos
   - Observar la gráfica de tendencia

6. **Ir a ESG**:
   - Ver emisiones instantáneas y acumuladas
   - Cambiar entre máquinas para ver diferentes perfiles

7. **Simular anomalía**:
   - Esperar ~150 ciclos (7-8 minutos)
   - El simulador entrará en fase "failure"
   - Verás picos de vibración/temperatura
   - El risk score subirá significativamente

## 📊 Datos de Demo

### Máquinas
- **TRUCK-21**: Haul truck de mina de cobre
- **MILL-3**: Grinding mill de planta de carbón (alto consumo eléctrico)
- **BOILER-7**: Boiler industrial de generación (alto consumo combustible)

### Fases de Simulación
1. **Normal** (50 ciclos): Operación estable
2. **Drift** (50 ciclos): Degradación gradual
3. **Failure** (continuo): Anomalías ocasionales (20% probabilidad)

### Métricas Simuladas
- RPM, temperature, vibration, pressure
- fuel_rate_lh, co2_ppm, kwh
- Más específicas según tipo de máquina

## 🔧 Configuración Avanzada

### Cambiar intervalo de simulación

Edita `.env`:
```
SIM_INTERVAL_SECONDS=5  # Aumentar para más lento
```

### Añadir más máquinas

Edita `.env`:
```
MACHINES=TRUCK-21,MILL-3,BOILER-7,TURBINE-5
```

Luego añade configuración en `iot-sim/config.py`.

### Cambiar factores ESG

Edita `backend/services/esg_engine.py`:
```python
FACTOR_FUEL_DIESEL = 2.68  # kg CO2/l
FACTOR_ELECTRICITY_LATAM = 0.45  # kg CO2/kWh
```

## 📝 Notas

- La base de datos es SQLite local (`aurumai.db`)
- En producción se usaría PostgreSQL + TimescaleDB
- Los modelos ML son "fake but credible" - parecen reales pero son heurísticas
- ESG usa factores IPCC simplificados
- Todo está preparado para escalar sin cambios arquitectónicos mayores

## 🎉 ¡Listo!

Ya tienes el mockup funcional completo. Puedes presentarlo a inversores, clientes o usarlo como base para el producto real.

**Para parar todo**:
```bash
docker compose down
```

**Para limpiar volúmenes**:
```bash
docker compose down -v
```
