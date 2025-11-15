#!/bin/bash

# AurumAI Mockup - Verification Script
# This script checks if the development environment is set up correctly.

# --- Colors ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Helper Functions ---
print_success() {
    echo -e "  ${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "  ${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "  ${RED}❌ $1${NC}"
}

check_dir() {
    [ -d "$1" ]
}

check_file() {
    [ -f "$1" ]
}

# --- Main Verification Logic ---
echo "🔍 AurumAI Mockup - Verificación de Entorno de Desarrollo"
echo "========================================================"
echo ""

# 1. Frontend Verification
echo "1. Verificando Frontend (frontend/)..."
if ! check_dir "frontend"; then
    print_error "Directorio 'frontend' no encontrado."
else
    cd frontend
    if ! check_file "package.json"; then
        print_error "'package.json' no encontrado."
    else
        print_success "'package.json' encontrado."
        if ! check_dir "node_modules"; then
            print_warning "'node_modules' no encontrado. Ejecuta 'npm install'."
        else
            print_success "'node_modules' encontrado. Dependencias parecen estar instaladas."
        fi
    fi
    if ! check_file "tsconfig.json"; then
        print_error "'tsconfig.json' no encontrado."
    else
        print_success "'tsconfig.json' encontrado."
    fi
    cd ..
fi
echo ""

# 2. Backend Verification
echo "2. Verificando Backend (backend/)..."
if ! check_dir "backend"; then
    print_error "Directorio 'backend' no encontrado."
else
    cd backend
    if ! check_file "requirements.txt"; then
        print_error "'requirements.txt' no encontrado."
    else
        print_success "'requirements.txt' encontrado."
        if [ -d ".venv" ] || [ -d "venv" ]; then
            print_success "Entorno virtual detectado."
        else
            print_warning "No se encontró un entorno virtual (.venv o venv). Asegúrate de que las dependencias estén instaladas."
        fi
    fi

    if ! check_file ".env"; then
        print_warning "Archivo '.env' no encontrado. Copia '.env.example' a '.env' y configura las variables."
    else
        print_success "Archivo '.env' encontrado."
        # Check for missing variables from .env.example
        if check_file ".env.example"; then
            missing_vars=$(grep -v '^#' .env.example | cut -d= -f1 | while read -r var; do grep -q "^$var=" .env || echo "$var"; done)
            if [ -n "$missing_vars" ]; then
                print_warning "Faltan las siguientes variables en tu .env:"
                for var in $missing_vars; do
                    echo -e "    - $var"
                done
            else
                print_success "Todas las variables de '.env.example' están en '.env'."
            fi
        fi
    fi
    cd ..
fi
echo ""

# 3. IoT Simulator Verification
echo "3. Verificando IoT Simulator (iot-sim/)..."
if ! check_dir "iot-sim"; then
    print_error "Directorio 'iot-sim' no encontrado."
else
    cd "iot-sim"
    if ! check_file "requirements.txt"; then
        print_error "'requirements.txt' no encontrado."
    else
        print_success "'requirements.txt' encontrado."
    fi
    cd ..
fi
echo ""

# 4. Edge Simulator Verification
echo "4. Verificando Edge Simulator (edge-sim/)..."
if ! check_dir "edge-sim"; then
    print_error "Directorio 'edge-sim' no encontrado."
else
    cd "edge-sim"
    if ! check_file "requirements.txt"; then
        print_error "'requirements.txt' no encontrado."
    else
        print_success "'requirements.txt' encontrado."
    fi
    cd ..
fi
echo ""

echo "========================================================"
echo "✅ Verificación completa."
echo "Si hay advertencias (⚠️), revisa los mensajes para asegurar una configuración correcta."
echo "Si hay errores (❌), debes solucionarlos para que la aplicación funcione."
echo ""