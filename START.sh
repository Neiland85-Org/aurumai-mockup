#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       🏭 AurumAI Mockup - Inicio Rápido                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "📋 Verificando estructura del proyecto..."
echo ""

# Verificar directorios principales
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Directorio backend no encontrado${NC}"
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Directorio frontend no encontrado${NC}"
    exit 1
fi

if [ ! -d "iot-sim" ]; then
    echo -e "${RED}❌ Directorio iot-sim no encontrado${NC}"
    exit 1
fi

if [ ! -d "edge-sim" ]; then
    echo -e "${RED}❌ Directorio edge-sim no encontrado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Estructura de directorios correcta${NC}"
echo ""

# Verificar Python
echo "🐍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no encontrado${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ ${PYTHON_VERSION}${NC}"
echo ""

# Verificar Node.js
echo "📦 Verificando Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js no encontrado${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js ${NODE_VERSION}${NC}"
echo ""

# Verificar Docker
echo "🐳 Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker no encontrado (necesario para docker compose up)${NC}"
else
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✅ ${DOCKER_VERSION}${NC}"
fi
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "  Opciones de Arranque"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1️⃣  Docker Compose (Recomendado)"
echo "   → docker compose up --build"
echo ""
echo "2️⃣  Manual (Desarrollo)"
echo "   Terminal 1: cd backend && uvicorn app:app --reload --port 8000"
echo "   Terminal 2: cd edge-sim && python main.py"
echo "   Terminal 3: cd iot-sim && python generator.py"
echo "   Terminal 4: cd frontend && npm run dev"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

read -p "¿Arrancar con Docker Compose? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Arrancando con Docker Compose..."
    echo ""
    docker compose up --build
else
    echo ""
    echo "ℹ️  Para arranque manual, sigue las instrucciones en SETUP.md"
    echo ""
fi
