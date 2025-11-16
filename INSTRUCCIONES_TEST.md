# 🚀 Instrucciones para Test de Endpoints

## Paso 1 Levantar Backend

Abre una **nueva terminal** y ejecuta:

```bash
cd /Users/estudio/Projects/GitHub/MOCKUPs/aurumai-mockup/backend
python3 -m uvicorn app:app --reload --port 8000
```

Deberías ver:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [XXXXX]
INFO:     Application startup complete.
```

---

## Paso 2 Verificar que el Backend está Activo

En **otra terminal**, ejecuta:

```bash
curl http://localhost:8000/
```

Deberías recibir una respuesta JSON del backend.

---

## Paso 3 Test de Endpoints

### Opción A Usando el script Python

```bash
cd /Users/estudio/Projects/GitHub/MOCKUPs/aurumai-mockup
python3 test_endpoints.py
```

### Opción B Usando curl manualmente

**Test /ingest/raw**:

```bash
curl -X POST http://localhost:8000/ingest/raw \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "TRUCK-21",
    "timestamp": "2025-11-15T10:00:00",
    "metrics": {
      "vibration": 3.5,
      "temperature": 75.2,
      "rpm": 1500,
      "co2_ppm": 400,
      "fuel_consumption": 25.5
    }
  }'
```

**Respuesta esperada**:

```json
{
  "status": "success",
  "message": "Raw measurement ingested for machine TRUCK-21",
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-15T10:00:00",
  "metrics_count": 5
}
```

**Test /ingest/features**:

```bash
curl -X POST http://localhost:8000/ingest/features \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "TRUCK-21",
    "timestamp": "2025-11-15T10:00:00",
    "features": {
      "vibration_sma": 3.2,
      "vibration_derivative": 0.1,
      "vibration_min": 2.5,
      "vibration_max": 4.0,
      "temperature_sma": 76.0,
      "temperature_derivative": 0.5,
      "temperature_min": 70.0,
      "temperature_max": 80.0,
      "rpm_sma": 1480.0,
      "rpm_derivative": 10.0,
      "rpm_min": 1400,
      "rpm_max": 1600
    }
  }'
```

**Respuesta esperada**:

```json
{
  "status": "success",
  "message": "Features ingested for machine TRUCK-21",
  "machine_id": "TRUCK-21",
  "timestamp": "2025-11-15T10:00:00",
  "features_count": 12
}
```

---

## Paso 4: Verificar Datos en DB

Después de enviar datos, verifica que se guardaron:

```bash
cd /Users/estudio/Projects/GitHub/MOCKUPs/aurumai-mockup

# Ver mediciones raw
sqlite3 backend/aurumai.db "SELECT COUNT(*) FROM measurements;"

# Ver feature vectors
sqlite3 backend/aurumai.db "SELECT COUNT(*) FROM feature_vectors;"

# Ver últimas mediciones
sqlite3 backend/aurumai.db "SELECT * FROM measurements ORDER BY timestamp DESC LIMIT 5;"
```

---

## Troubleshooting

### Si el backend no arranca

1. **Verificar puerto no está en uso**:

   ```bash
   lsof -i :8000
   ```

2. **Matar proceso si existe**:

   ```bash
   kill -9 $(lsof -t -i:8000)
   ```

3. **Verificar dependencias instaladas**:

   ```bash
   cd backend
   pip3 list | grep -i "fastapi\|uvicorn\|sqlalchemy"
   ```

### Si hay errores de import

```bash
cd /Users/estudio/Projects/GitHub/MOCKUPs/aurumai-mockup/backend
export PYTHONPATH=/Users/estudio/Projects/GitHub/MOCKUPs/aurumai-mockup/backend:$PYTHONPATH
python3 -m uvicorn app:app --reload
```

---

## Siguiente Paso Demo Completo

Una vez que los endpoints funcionen, ejecutar el demo integrado:

```bash
# Terminal 1: Backend (ya debería estar corriendo)

# Terminal 2: Demo IoT + Edge
cd /Users/estudio/Projects/GitHub/MOCKUPs/aurumai-mockup/iot-sim
python3 run_demo.py
```

---

**Nota**: Como no puedo mantener terminales en background de forma confiable,
estos pasos deben ejecutarse manualmente en tu terminal.
