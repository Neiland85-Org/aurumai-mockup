# 🚀 Iniciar Backend AurumAI

## Inicio Rápido (2 minutos)

### Opción 1: Con script (Recomendado)

```bash
cd /Users/estudio/Projects/GitHub/MOCKUPs/aurumai-mockup/backend
chmod +x start_backend.sh
./start_backend.sh
```

### Opción 2: Comando directo

```bash
cd /Users/estudio/Projects/GitHub/MOCKUPs/aurumai-mockup/backend
source .venv/bin/activate
python -m uvicorn app:app --reload --host 0.0.0.0
```

## Verificación

Una vez iniciado, deberías ver:

```
INFO:     Will watch for changes in these directories: ['/Users/estudio/Projects/GitHub/MOCKUPs/aurumai-mockup/backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Probar el Backend

### 1. API Docs (Swagger)

Abre en tu navegador: **http://localhost:8000/docs**

### 2. Test con curl

```bash

## VS Code: resolver imports (Pylance)

Si ves "Import could not be resolved":

1. Selecciona el intérprete: Command Palette → `Python: Select Interpreter` → `${workspaceFolder}/backend/.venv/bin/python`.
2. Recarga la ventana: Command Palette → `Developer: Reload Window`.
3. La configuración del workspace ya está creada en `.vscode/settings.json` y el `.env` añade `PYTHONPATH`.
4. Si quieres menos ruido temporalmente: en `.vscode/settings.json` puedes cambiar `python.analysis.diagnosticMode` a `openFilesOnly`.
# Ver máquinas disponibles
curl http://localhost:8000/machines/

# Ver métricas de TRUCK-21
curl http://localhost:8000/machines/TRUCK-21/metrics

# Test endpoint /ingest/raw
curl -X POST http://localhost:8000/ingest/raw \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "TRUCK-21",
    "timestamp": "2024-01-15T10:30:00",
    "metrics": {
      "temperature": 85.5,
      "vibration": 2.3,
      "pressure": 120.5,
      "rpm": 1500
    }
  }'
```

### 3. Test con script Python

```bash
python3 test_endpoints.py
```

## Endpoints Disponibles

- `GET /` - Health check
- `GET /machines/` - Lista todas las máquinas
- `GET /machines/{machine_id}/metrics` - Métricas de una máquina
- `POST /ingest/raw` - Ingerir telemetría raw
- `POST /ingest/features` - Ingerir features procesados
- `POST /predict` - Obtener predicción
- `GET /esg/current` - Datos ESG actuales
- `GET /esg/summary` - Resumen ESG

## Estado del Frontend

Una vez el backend esté corriendo en **http://localhost:8000**, el frontend en **http://localhost:3001** debería conectarse automáticamente y mostrar los datos.

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'uvicorn'"

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

### Error: "Port 8000 is already in use"

```bash
# Encontrar el proceso usando el puerto 8000
lsof -i :8000

# Matar el proceso (reemplazar PID con el número obtenido)
kill -9 <PID>
```

### Error: Database locked

```bash
# Verificar que no hay otros procesos usando la DB
lsof backend/aurumai.db

# Si es necesario, matar el proceso
kill -9 <PID>
```

## Parar el Backend

Presiona `CTRL+C` en la terminal donde está corriendo uvicorn.

## Demo Completo

Para el flujo completo **IoT → Edge → Backend → Frontend**, ver:

- `RESUMEN_FINAL_SESION.md` - Instrucciones completas del demo
- `INSTRUCCIONES_TEST.md` - Testing detallado
