#!/bin/bash

echo "🔍 AurumAI Mockup - Verificación de Setup"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Backend
echo "1. Backend..."
cd backend
if python3 -c "from infrastructure.db.database import init_db; init_db()" 2>/dev/null; then
    echo "   ✅ Database inicializada"
else
    echo "   ❌ Error en database"
fi

if python3 -c "from services.ml_engine import run_prediction; print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "   ✅ ML Engine OK"
else
    echo "   ❌ Error en ML Engine"
fi

if python3 -c "from services.esg_engine import compute_esg_metrics; print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "   ✅ ESG Engine OK"
else
    echo "   ❌ Error en ESG Engine"
fi
cd ..

# IoT Simulator
echo ""
echo "2. IoT Simulator..."
cd iot-sim
if python3 -c "from config import MACHINES; print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "   ✅ Config OK"
else
    echo "   ❌ Error en config"
fi

if python3 -c "from anomalies import generate_normal_metrics; print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "   ✅ Anomalies OK"
else
    echo "   ❌ Error en anomalies"
fi
cd ..

# Edge Simulator
echo ""
echo "3. Edge Simulator..."
cd edge-sim
if python3 -c "from config import BACKEND_BASE_URL; print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "   ✅ Config OK"
else
    echo "   ❌ Error en config"
fi

if python3 -c "from features import compute_features_from_metrics; print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "   ✅ Features OK"
else
    echo "   ❌ Error en features"
fi
cd ..

# Frontend
echo ""
echo "4. Frontend..."
cd frontend
if [ -f "package.json" ]; then
    echo "   ✅ package.json existe"
    if [ -s "package.json" ]; then
        echo "   ✅ package.json no está vacío"
    else
        echo "   ❌ package.json está vacío"
    fi
else
    echo "   ❌ package.json no existe"
fi

if [ -f "tsconfig.json" ]; then
    echo "   ✅ tsconfig.json existe"
else
    echo "   ❌ tsconfig.json no existe"
fi
cd ..

echo ""
echo "=========================================="
echo "✅ Verificación completa"
echo ""
echo "Para arrancar: ./START.sh o docker compose up --build"
