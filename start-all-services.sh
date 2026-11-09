#!/bin/bash
# AetherOps - Start All Core Microservices (Ports 7999 to 8010)
# This script starts the 12 core user-flow microservices

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AetherOps Core Microservices Startup  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Ensure venv exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    .venv/bin/pip install -q --upgrade pip
    .venv/bin/pip install -q -r requirements.txt || uv pip install --python .venv/bin/python -r requirements.txt
fi

PYTHON="$SCRIPT_DIR/.venv/bin/python"
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi
export PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/shared:${PYTHONPATH:-}"
export AWS_REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-ap-south-1}}"
export AWS_SECRET_ID="${AWS_SECRET_ID:-${AETHER_SECRET_ID:-aetherops/platform}}"
GATEWAY_HOST="${GATEWAY_HOST:-${HOST:-0.0.0.0}}"
AUTH_HOST="${AUTH_HOST:-${HOST:-0.0.0.0}}"

# 1. Auth Service - Port 7999
echo -e "${GREEN}[1/12]${NC} Starting Auth Service (Port 7999)..."
cd services/auth_service
nohup setsid $PYTHON -m uvicorn app.main:app --host "$AUTH_HOST" --port 7999 </dev/null > /tmp/aether-auth.log 2>&1 &
cd ../..
sleep 1

# 2. API Gateway & Dashboard - Port 8000
echo -e "${GREEN}[2/12]${NC} Starting API Gateway & Dashboard (Port 8000)..."
cd services/gateway
nohup setsid $PYTHON -m uvicorn app.main:app --host "$GATEWAY_HOST" --port 8000 </dev/null > /tmp/aether-gateway.log 2>&1 &
cd ../..
sleep 1

# 3. Project and Environment Management - Port 8001
echo -e "${GREEN}[3/12]${NC} Starting Project & Environment (Port 8001)..."
cd services/project_and_environment_management
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8001 </dev/null > /tmp/aether-projects.log 2>&1 &
cd ../..
sleep 1

# 4. Connect Cloud and Git - Port 8002
echo -e "${GREEN}[4/12]${NC} Starting Connect Cloud & Git (Port 8002)..."
cd services/source_and_cloud_connection
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8002 </dev/null > /tmp/aether-source.log 2>&1 &
cd ../..
sleep 1

# 5. Source Code Analyzer - Port 8003
echo -e "${GREEN}[5/12]${NC} Starting Source Code Analyzer (Port 8003)..."
cd services/repo_analyzer_service
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8003 </dev/null > /tmp/aether-analyzer.log 2>&1 &
cd ../..
sleep 1

# 6. AI AWS Architecture Planning - Port 8004
echo -e "${GREEN}[6/12]${NC} Starting AI AWS Architecture (Port 8004)..."
cd services/architecture_generator
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8004 </dev/null > /tmp/aether-architecture.log 2>&1 &
cd ../..
sleep 1

# 7. IaC Generator - Port 8005
echo -e "${GREEN}[7/12]${NC} Starting IaC Generator (Port 8005)..."
cd services/iac_generator
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8005 </dev/null > /tmp/aether-iac.log 2>&1 &
cd ../..
sleep 1

# 8. Dry-Run & Approval Gate - Port 8006
echo -e "${GREEN}[8/12]${NC} Starting Dry-Run & Approval Gate (Port 8006)..."
cd services/cloud_deployer
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8006 </dev/null > /tmp/aether-approval.log 2>&1 &
cd ../..
sleep 1

# 9. Cloud Deployer - Port 8007
echo -e "${GREEN}[9/12]${NC} Starting Cloud Deployer (Port 8007)..."
cd services/cloud_deployer
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8007 </dev/null > /tmp/aether-deployer.log 2>&1 &
cd ../..
sleep 1

# 10. Observability the Infrastructure - Port 8008
echo -e "${GREEN}[10/12]${NC} Starting Observability (Port 8008)..."
cd services/observability_setup
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8008 </dev/null > /tmp/aether-observability.log 2>&1 &
cd ../..
sleep 1

# 11. User & Credential Settings - Port 8009
echo -e "${GREEN}[11/12]${NC} Starting User & Credential Settings (Port 8009)..."
cd services/cicd_pipeline
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8009 </dev/null > /tmp/aether-settings.log 2>&1 &
cd ../..
sleep 1

# 12. Admin Console (Restricted) - Port 8010
echo -e "${GREEN}[12/12]${NC} Starting Admin Console (Port 8010)..."
cd services/admin_console
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8010 </dev/null > /tmp/aether-admin.log 2>&1 &
cd ../..
sleep 1

disown -a 2>/dev/null || true

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ All 12 Core Services Started!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Service URLs (Ports 7999–8010):"
echo "  Auth Service:         http://localhost:7999"
echo "  API Gateway / UI:     http://localhost:8000"
echo "  Project & Env:        http://localhost:8001"
echo "  Connect Cloud & Git:  http://localhost:8002"
echo "  Source Code Analyzer: http://localhost:8003"
echo "  AI AWS Architecture:  http://localhost:8004"
echo "  IaC Generator:        http://localhost:8005"
echo "  Dry-Run & Approval:   http://localhost:8006"
echo "  Cloud Deployer:       http://localhost:8007"
echo "  Observability:        http://localhost:8008"
echo "  User & Credentials:   http://localhost:8009"
echo "  Admin Console:        http://localhost:8010 (Admin Only)"
echo ""
echo "Logs are in /tmp/aether-*.log"
echo ""
echo -e "${YELLOW}To stop all services, run: ./stop-all-services.sh${NC}"

if [ "$1" == "--daemon" ] || [ "$1" == "-d" ] || [ "$DAEMON" == "1" ]; then
    echo -e "${GREEN}✓ All services running in background.${NC}"
    exit 0
fi

wait
