#!/bin/bash
# AetherOps - Start All 15 Microservices (Ports 7999 to 8013)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AetherOps Full Fleet Startup (15 Svcs) ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

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
SERVICE_HOST="${SERVICE_HOST:-${HOST:-0.0.0.0}}"

# 1. Auth Service - Port 7999
echo -e "${GREEN}[1/15]${NC} Starting Auth Service (Port 7999)..."
cd services/auth_service
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 7999 </dev/null > /tmp/aether-auth.log 2>&1 &
cd ../..
sleep 1

# 2. API Gateway & Dashboard - Port 8000
echo -e "${GREEN}[2/15]${NC} Starting API Gateway & Dashboard (Port 8000)..."
cd services/gateway
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8000 </dev/null > /tmp/aether-gateway.log 2>&1 &
cd ../..
sleep 1

# 3. Project & Environment Management - Port 8001
echo -e "${GREEN}[3/15]${NC} Starting Project & Environment (Port 8001)..."
cd services/project_environment_service
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8001 </dev/null > /tmp/aether-projects.log 2>&1 &
cd ../..
sleep 1

# 4. Source, Cloud & Git Connection - Port 8002
echo -e "${GREEN}[4/15]${NC} Starting Source, Cloud & Git (Port 8002)..."
cd services/source_cloud_git_service
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8002 </dev/null > /tmp/aether-source.log 2>&1 &
cd ../..
sleep 1

# 5. Source Code Analyzer - Port 8003
echo -e "${GREEN}[5/15]${NC} Starting Source Code Analyzer (Port 8003)..."
cd services/source_code_analyzer
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8003 </dev/null > /tmp/aether-analyzer.log 2>&1 &
cd ../..
sleep 1

# 6. AI Architecture Engine - Port 8004
echo -e "${GREEN}[6/15]${NC} Starting AI Architecture Engine (Port 8004)..."
cd services/ai_architecture_engine
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8004 </dev/null > /tmp/aether-ai-arch.log 2>&1 &
cd ../..
sleep 1

# 7. Architecture Designer - Port 8005
echo -e "${GREEN}[7/15]${NC} Starting Architecture Designer (Port 8005)..."
cd services/architecture_designer
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8005 </dev/null > /tmp/aether-designer.log 2>&1 &
cd ../..
sleep 1

# 8. Architecture Validation - Port 8006
echo -e "${GREEN}[8/15]${NC} Starting Architecture Validation (Port 8006)..."
cd services/architecture_validation
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8006 </dev/null > /tmp/aether-validation.log 2>&1 &
cd ../..
sleep 1

# 9. Pre-Deployment Risk Engine - Port 8007
echo -e "${GREEN}[9/15]${NC} Starting Pre-Deployment Risk Engine (Port 8007)..."
cd services/pre_deployment_risk_engine
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8007 </dev/null > /tmp/aether-risk.log 2>&1 &
cd ../..
sleep 1

# 10. Terraform / IaC Generator - Port 8008
echo -e "${GREEN}[10/15]${NC} Starting Terraform / IaC Generator (Port 8008)..."
cd services/terraform_iac_generator
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8008 </dev/null > /tmp/aether-iac.log 2>&1 &
cd ../..
sleep 1

# 11. Approval & Execution - Port 8009
echo -e "${GREEN}[11/15]${NC} Starting Approval & Execution (Port 8009)..."
cd services/approval_execution_service
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8009 </dev/null > /tmp/aether-approval.log 2>&1 &
cd ../..
sleep 1

# 12. Application Deployment - Port 8010
echo -e "${GREEN}[12/15]${NC} Starting Application Deployment (Port 8010)..."
cd services/application_deployment_service
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8010 </dev/null > /tmp/aether-deploy.log 2>&1 &
cd ../..
sleep 1

# 13. Monitoring - Port 8011
echo -e "${GREEN}[13/15]${NC} Starting Monitoring Service (Port 8011)..."
cd services/monitoring_service
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8011 </dev/null > /tmp/aether-monitoring.log 2>&1 &
cd ../..
sleep 1

# 14. Audit & History - Port 8012
echo -e "${GREEN}[14/15]${NC} Starting Audit & History Service (Port 8012)..."
cd services/audit_history_service
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8012 </dev/null > /tmp/aether-audit.log 2>&1 &
cd ../..
sleep 1

# 15. Admin Console - Port 8013
echo -e "${GREEN}[15/15]${NC} Starting Admin Console (Port 8013)..."
cd services/admin_console
nohup setsid $PYTHON -m uvicorn app.main:app --host "$SERVICE_HOST" --port 8013 </dev/null > /tmp/aether-admin.log 2>&1 &
cd ../..
sleep 1

disown -a 2>/dev/null || true

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ All 15 AetherOps Services Started!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Service Ports & Endpoints (7999–8013):"
echo "  Auth Service:               http://localhost:7999"
echo "  API Gateway & Dashboard:    http://localhost:8000"
echo "  Project & Environment:      http://localhost:8001"
echo "  Source, Cloud & Git:        http://localhost:8002"
echo "  Source Code Analyzer:       http://localhost:8003"
echo "  AI Architecture Engine:     http://localhost:8004"
echo "  Architecture Designer:      http://localhost:8005"
echo "  Architecture Validation:    http://localhost:8006"
echo "  Pre-Deployment Risk Engine: http://localhost:8007"
echo "  Terraform / IaC Generator:  http://localhost:8008"
echo "  Approval & Execution:       http://localhost:8009"
echo "  Application Deployment:     http://localhost:8010"
echo "  Monitoring Service:         http://localhost:8011"
echo "  Audit & History Service:    http://localhost:8012"
echo "  Admin Console:              http://localhost:8013"
echo ""
echo "Logs are in /tmp/aether-*.log"
echo ""
echo -e "${YELLOW}To stop all services, run: ./stop-all-services.sh${NC}"

if [ "$1" == "--daemon" ] || [ "$1" == "-d" ] || [ "$DAEMON" == "1" ]; then
    echo -e "${GREEN}✓ All services running in background.${NC}"
    exit 0
fi

wait
