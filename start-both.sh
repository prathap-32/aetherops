#!/bin/bash
# AetherOps - Start Core Microservices: Auth (7999), Dashboard (8000), Project Management (8001)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

PYTHON="$SCRIPT_DIR/.venv/bin/python"
HOST="${HOST:-127.0.0.1}"

echo "Starting Auth Service on port 7999..."
cd "$SCRIPT_DIR/services/auth_service"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 7999 </dev/null > /tmp/aether-auth.log 2>&1 &
AUTH_PID=$!
cd "$SCRIPT_DIR"

sleep 1

echo "Starting Dashboard & Gateway on port 8000..."
cd "$SCRIPT_DIR/services/gateway"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8000 </dev/null > /tmp/aether-gateway.log 2>&1 &
DASH_PID=$!
cd "$SCRIPT_DIR"

sleep 1

echo "Starting Project Management on port 8001..."
cd "$SCRIPT_DIR/services/project_and_environment_management"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8001 </dev/null > /tmp/aether-projects.log 2>&1 &
PM_PID=$!
cd "$SCRIPT_DIR"

sleep 1

echo "Starting Source & Cloud Connection on port 8002..."
cd "$SCRIPT_DIR/services/source_and_cloud_connection"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8002 </dev/null > /tmp/aether-source.log 2>&1 &
SC_PID=$!
cd "$SCRIPT_DIR"

sleep 1

echo "Starting Repo Analyzer Service on port 8003..."
cd "$SCRIPT_DIR/services/repo_analyzer_service"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8003 </dev/null > /tmp/aether-repo.log 2>&1 &
REPO_PID=$!
cd "$SCRIPT_DIR"

sleep 1

echo "Starting Cloud Architecture Studio on port 8004..."
cd "$SCRIPT_DIR/services/architecture_generator"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8004 </dev/null > /tmp/aether-architecture.log 2>&1 &
ARCH_PID=$!
cd "$SCRIPT_DIR"

disown -a 2>/dev/null || true
sleep 2

echo ""
echo "✓ Core Microservices started independently!"
echo ""
echo "  Auth Service:       http://localhost:7999 (PID: $AUTH_PID)"
echo "  Dashboard Gateway:  http://localhost:8000 (PID: $DASH_PID)"
echo "  Project Manager:    http://localhost:8001 (PID: $PM_PID)"
echo "  Source Connection:  http://localhost:8002 (PID: $SC_PID)"
echo "  Repo Analyzer (M3): http://localhost:8003 (PID: $REPO_PID)"
echo "  Architecture Studio: http://localhost:8004 (PID: $ARCH_PID)"
echo ""
echo "  Default Login: admin / admin123"
echo ""
echo "To test: ./test-core-flow.sh"
echo "To stop: ./stop-all-services.sh"
echo "Logs: /tmp/aether-auth.log, /tmp/aether-gateway.log, /tmp/aether-projects.log, /tmp/aether-source.log, /tmp/aether-repo.log, /tmp/aether-architecture.log"

