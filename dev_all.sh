#!/bin/zsh
# Script para levantar Backend, Frontend y Simulador IoT en 3 terminales (macOS)
# Ejecuta: ./dev_all.sh

# Backend
osascript -e 'tell application "Terminal"
    do script "cd ~/Projects/GitHub/MOCKUPs/aurumai-mockup/backend && source .venv/bin/activate && python -m uvicorn app:app --reload"
end tell'

# Frontend
osascript -e 'tell application "Terminal"
    do script "cd ~/Projects/GitHub/MOCKUPs/aurumai-mockup/frontend && . ~/.asdf/asdf.sh && npm run dev"
end tell'

# Simulador IoT
osascript -e 'tell application "Terminal"
    do script "cd ~/Projects/GitHub/MOCKUPs/aurumai-mockup/iot-sim && source ../backend/.venv/bin/activate && python run_demo.py"
end tell'

# Mensaje final
sleep 2
echo "✅ Entorno de desarrollo levantado: Backend (8000), Frontend (3001), Simulador IoT. Abre http://localhost:3001 en tu navegador."
