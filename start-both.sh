#!/bin/bash
# AetherOps - Start Core Microservices (Ports 7999 to 8010)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi
export PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/shared:${PYTHONPATH:-}"
export AWS_REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-ap-south-1}}"
export AWS_SECRET_ID="${AWS_SECRET_ID:-${AETHER_SECRET_ID:-aetherops/platform}}"

PYTHON="$SCRIPT_DIR/.venv/bin/python"
HOST="${HOST:-0.0.0.0}"

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

echo "Starting Connect Cloud & Git on port 8002..."
cd "$SCRIPT_DIR/services/source_and_cloud_connection"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8002 </dev/null > /tmp/aether-source.log 2>&1 &
SC_PID=$!
cd "$SCRIPT_DIR"
sleep 1

echo "Starting Source Code Analyzer on port 8003..."
cd "$SCRIPT_DIR/services/repo_analyzer_service"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8003 </dev/null > /tmp/aether-repo.log 2>&1 &
REPO_PID=$!
cd "$SCRIPT_DIR"
sleep 1

echo "Starting AI AWS Architecture Planning on port 8004..."
cd "$SCRIPT_DIR/services/architecture_generator"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8004 </dev/null > /tmp/aether-architecture.log 2>&1 &
ARCH_PID=$!
cd "$SCRIPT_DIR"
sleep 1

echo "Starting IaC Generator on port 8005..."
cd "$SCRIPT_DIR/services/iac_generator"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8005 </dev/null > /tmp/aether-iac.log 2>&1 &
IAC_PID=$!
cd "$SCRIPT_DIR"
sleep 1

echo "Starting Dry-Run & Approval Gate on port 8006..."
cd "$SCRIPT_DIR/services/cloud_deployer"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8006 </dev/null > /tmp/aether-approval.log 2>&1 &
APP_PID=$!
cd "$SCRIPT_DIR"
sleep 1

echo "Starting Cloud Deployer on port 8007..."
cd "$SCRIPT_DIR/services/cloud_deployer"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8007 </dev/null > /tmp/aether-deployer.log 2>&1 &
DEP_PID=$!
cd "$SCRIPT_DIR"
sleep 1

echo "Starting Observability on port 8008..."
cd "$SCRIPT_DIR/services/observability_setup"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8008 </dev/null > /tmp/aether-observability.log 2>&1 &
OBS_PID=$!
cd "$SCRIPT_DIR"
sleep 1

echo "Starting User & Credential Settings on port 8009..."
cd "$SCRIPT_DIR/services/auth_service"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8009 </dev/null > /tmp/aether-settings.log 2>&1 &
SET_PID=$!
cd "$SCRIPT_DIR"
sleep 1

echo "Starting Admin Console on port 8010..."
cd "$SCRIPT_DIR/services/admin_console"
nohup setsid $PYTHON -m uvicorn app.main:app --host "$HOST" --port 8010 </dev/null > /tmp/aether-admin.log 2>&1 &
ADM_PID=$!
cd "$SCRIPT_DIR"
sleep 2

disown -a 2>/dev/null || true

echo ""
echo "✓ All Core Microservices (Ports 7999–8010) started successfully!"
echo ""
echo "  Auth Service:         http://localhost:7999 (PID: $AUTH_PID)"
echo "  Dashboard Gateway:    http://localhost:8000 (PID: $DASH_PID)"
echo "  Project Manager:      http://localhost:8001 (PID: $PM_PID)"
echo "  Connect Cloud & Git:  http://localhost:8002 (PID: $SC_PID)"
echo "  Source Code Analyzer: http://localhost:8003 (PID: $REPO_PID)"
echo "  AI AWS Architecture:  http://localhost:8004 (PID: $ARCH_PID)"
echo "  IaC Generator:        http://localhost:8005 (PID: $IAC_PID)"
echo "  Dry-Run & Approval:   http://localhost:8006 (PID: $APP_PID)"
echo "  Cloud Deployer:       http://localhost:8007 (PID: $DEP_PID)"
echo "  Observability:        http://localhost:8008 (PID: $OBS_PID)"
echo "  User & Credentials:   http://localhost:8009 (PID: $SET_PID)"
echo "  Admin Console:        http://localhost:8010 (PID: $ADM_PID)"
echo ""
echo "  Default Login: admin / admin123"
echo ""
echo "To stop all services: ./stop-all-services.sh"
