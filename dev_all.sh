#!/bin/zsh
# Script para levantar Backend, Frontend y Simulador IoT en 3 terminales (macOS)
# Ejecuta: ./dev_all.sh


# Set project root directory (can be overridden by environment variable)
PROJECT_ROOT="${AURUMAI_MOCKUP_ROOT:-$PWD}"
# Backend
osascript -e 'tell application "Terminal"
    do script "cd '"$PROJECT_ROOT"'/backend && source .venv/bin/activate && python -m uvicorn app:app --reload"
end tell'
# Frontend
osascript -e 'tell application "Terminal"
    do script "cd '"$PROJECT_ROOT"'/frontend && . ~/.asdf/asdf.sh && npm run dev"
end tell'
# Simulador IoT
osascript -e 'tell application "Terminal"
    do script "cd '"$PROJECT_ROOT"'/iot-sim && source ../backend/.venv/bin/activate && python run_demo.py"
end tell'

# Mensaje final
sleep 2
echo "✅ Entorno de desarrollo levantado: Backend (8000), Frontend (3001), Simulador IoT. Abre http://localhost:3001 en tu navegador."
