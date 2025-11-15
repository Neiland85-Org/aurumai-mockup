#!/bin/bash
# Script para levantar Backend, Frontend y Simulador IoT en 3 terminales (Linux)
# Ejecuta: ./dev_all_linux.sh

# Backend
nohup gnome-terminal -- bash -c 'cd ~/Projects/GitHub/MOCKUPs/aurumai-mockup/backend && source .venv/bin/activate && python -m uvicorn app:app --reload; exec bash' &

# Frontend
nohup gnome-terminal -- bash -c 'cd ~/Projects/GitHub/MOCKUPs/aurumai-mockup/frontend && source ~/.asdf/asdf.sh && npm run dev; exec bash' &

# Simulador IoT
nohup gnome-terminal -- bash -c 'cd ~/Projects/GitHub/MOCKUPs/aurumai-mockup/iot-sim && source ../backend/.venv/bin/activate && python run_demo.py; exec bash' &

sleep 2
echo "✅ Entorno de desarrollo levantado: Backend (8000), Frontend (3001), Simulador IoT. Abre http://localhost:3001 en tu navegador."
