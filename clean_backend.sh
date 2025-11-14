#!/bin/bash
# Script para limpiar caché Python y formatear el backend

set -e

# Limpiar __pycache__ y archivos .pyc
find backend -type d -name "__pycache__" -exec rm -rf {} +
find backend -type f -name "*.pyc" -delete

# Formatear con black
.venv/bin/black backend

# Limpiar con ruff
.venv/bin/ruff check backend --fix

# Mensaje final
echo "✔️ Backend limpio y formateado. Puedes reiniciar el servidor."
