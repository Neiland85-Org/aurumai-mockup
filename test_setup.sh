#!/bin/bash

echo "🧪 AurumAI Mockup - Test Setup"
echo "=============================="
echo ""

# Test backend
echo "1️⃣ Testing Backend..."
cd backend
python3 -c "from infrastructure.db.database import init_db; init_db(); print('✅ Database initialized')"
cd ..

# Test iot-sim dependencies
echo ""
echo "2️⃣ Testing IoT Simulator config..."
python3 -c "import sys; sys.path.append('iot-sim'); from config import MACHINES; print(f'✅ IoT Sim configured for: {MACHINES}')"

# Test edge-sim dependencies
echo ""
echo "3️⃣ Testing Edge Simulator config..."
python3 -c "import sys; sys.path.append('edge-sim'); from config import BACKEND_BASE_URL; print(f'✅ Edge Sim configured for: {BACKEND_BASE_URL}')"

# Test frontend dependencies
echo ""
echo "4️⃣ Testing Frontend..."
if [ -f "frontend/package.json" ]; then
    echo "✅ Frontend package.json found"
else
    echo "⚠️  Frontend package.json not found"
fi

echo ""
echo "=============================="
echo "✅ Basic setup tests completed"
echo ""
echo "Next steps:"
echo "  - Run: docker compose up --build"
echo "  - Or see SETUP.md for manual setup"
