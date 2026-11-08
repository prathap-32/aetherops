#!/bin/bash
# AetherOps - Start All Services
# This script starts all microservices individually

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AetherOps Microservices Startup${NC}"
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


# 1. Auth Service - Port 7999
echo -e "${GREEN}[1/14]${NC} Starting Auth Service (Port 7999)..."
cd services/auth_service
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 7999 </dev/null > /tmp/aether-auth.log 2>&1 &
cd ../..
sleep 1

# 2. Gateway - Port 8000
echo -e "${GREEN}[2/14]${NC} Starting Gateway & Dashboard (Port 8000)..."
cd services/gateway
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8000 </dev/null > /tmp/aether-gateway.log 2>&1 &
cd ../..
sleep 1

# 3. Project & Environment Management - Port 8001
echo -e "${GREEN}[3/14]${NC} Starting Project Management (Port 8001)..."
cd services/project_and_environment_management
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8001 </dev/null > /tmp/aether-projects.log 2>&1 &
cd ../..
sleep 1

# 4. Source & Cloud Connection - Port 8002
echo -e "${GREEN}[4/14]${NC} Starting Source Connection (Port 8002)..."
cd services/source_and_cloud_connection
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8002 </dev/null > /tmp/aether-source.log 2>&1 &
cd ../..
sleep 1

# 5. Repo Analyzer - Port 8003
echo -e "${GREEN}[5/14]${NC} Starting Repo Analyzer (Port 8003)..."
cd services/repo_analyzer_service
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8003 </dev/null > /tmp/aether-analyzer.log 2>&1 &
cd ../..
sleep 1

# 6. Requirement Analysis - Port 8004 (Module 1)
echo -e "${GREEN}[6/14]${NC} Starting Requirement Analysis (Port 8004)..."
cd services/requirement_analysis
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8004 </dev/null > /tmp/aether-requirements.log 2>&1 &
cd ../..
sleep 1

# 7. Cloud Architecture Studio - Port 8005 (Module 4)
echo -e "${GREEN}[7/14]${NC} Starting Cloud Architecture Studio (Port 8005)..."
cd services/architecture_generator
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8005 </dev/null > /tmp/aether-architecture.log 2>&1 &
cd ../..
sleep 1

# 8. IaC Generator - Port 8006
echo -e "${GREEN}[8/14]${NC} Starting IaC Generator (Port 8006)..."
cd services/iac_generator
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8006 </dev/null > /tmp/aether-iac.log 2>&1 &
cd ../..
sleep 1

# 9. FinOps Optimizer - Port 8007
echo -e "${GREEN}[9/14]${NC} Starting FinOps Optimizer (Port 8007)..."
cd services/finops_optimizer
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8007 </dev/null > /tmp/aether-finops.log 2>&1 &
cd ../..
sleep 1

# 10. Security Scanner - Port 8008
echo -e "${GREEN}[10/14]${NC} Starting Security Scanner (Port 8008)..."
cd services/security_scanner
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8008 </dev/null > /tmp/aether-security.log 2>&1 &
cd ../..
sleep 1

# 11. CI/CD Pipeline - Port 8009
echo -e "${GREEN}[11/14]${NC} Starting CI/CD Pipeline (Port 8009)..."
cd services/cicd_pipeline
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8009 </dev/null > /tmp/aether-cicd.log 2>&1 &
cd ../..
sleep 1

# 12. Observability Setup - Port 8010
echo -e "${GREEN}[12/14]${NC} Starting Observability Setup (Port 8010)..."
cd services/observability_setup
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8010 </dev/null > /tmp/aether-observability.log 2>&1 &
cd ../..
sleep 1

# 13. Cloud Deployer - Port 8011
echo -e "${GREEN}[13/14]${NC} Starting Cloud Deployer (Port 8011)..."
cd services/cloud_deployer
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8011 </dev/null > /tmp/aether-deployer.log 2>&1 &
cd ../..
sleep 1

# 14. Admin Console - Port 8012
echo -e "${GREEN}[14/14]${NC} Starting Admin Console (Port 8012)..."
cd services/admin_console
nohup setsid $PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8012 </dev/null > /tmp/aether-admin.log 2>&1 &
cd ../..
sleep 1

disown -a 2>/dev/null || true

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ All services started!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Service URLs:"
echo "  Auth:          http://localhost:7999"
echo "  Dashboard:     http://localhost:8000"
echo "  Projects:      http://localhost:8001"
echo "  Source:        http://localhost:8002"
echo "  Analyzer:      http://localhost:8003"
echo "  Requirements:  http://localhost:8004"
echo "  Architecture:  http://localhost:8005"
echo "  IaC:           http://localhost:8006"
echo "  FinOps:        http://localhost:8007"
echo "  Security:      http://localhost:8008"
echo "  CI/CD:         http://localhost:8009"
echo "  Observability: http://localhost:8010"
echo "  Deployer:      http://localhost:8011"
echo "  Admin:         http://localhost:8012"
echo ""
echo "Logs are in /tmp/aether-*.log"
echo ""
echo -e "${YELLOW}To stop all services, run: ./stop-all-services.sh or pkill -f 'uvicorn.*app.main:app'${NC}"

if [ "$1" == "--daemon" ] || [ "$1" == "-d" ] || [ "$DAEMON" == "1" ]; then
    echo -e "${GREEN}✓ All services running in background.${NC}"
    exit 0
fi

wait

