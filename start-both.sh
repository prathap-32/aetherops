#!/bin/bash
# Start Auth (7999) and Dashboard (8000) only

cd "$(dirname "$0")"

echo "Starting Auth Service on port 7999..."
.venv/bin/python -m uvicorn services.auth_service.app.main:app --host 0.0.0.0 --port 7999 > /tmp/auth.log 2>&1 &
AUTH_PID=$!

sleep 2

echo "Starting Dashboard on port 8000..."
.venv/bin/python -m uvicorn services.gateway.app.main:app --host 0.0.0.0 --port 8000 > /tmp/dashboard.log 2>&1 &
DASH_PID=$!

sleep 3

echo ""
echo "✓ Services started!"
echo ""
echo "  Auth:      http://localhost:7999 (PID: $AUTH_PID)"
echo "  Dashboard: http://localhost:8000 (PID: $DASH_PID)"
echo ""
echo "  Login: admin / admin123"
echo ""
echo "To stop: pkill -f 'uvicorn.*app.main:app'"
echo "Logs: /tmp/auth.log and /tmp/dashboard.log"
