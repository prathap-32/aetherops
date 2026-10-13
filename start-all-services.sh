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
    .venv/bin/pip install -q fastapi uvicorn httpx pydantic rich pyjwt bcrypt
fi

PYTHON=".venv/bin/python"

# 1. Auth Service - Port 7999
echo -e "${GREEN}[1/14]${NC} Starting Auth Service (Port 7999)..."
cd services/auth_service
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 7999 > /tmp/aether-auth.log 2>&1 &
cd ../..
sleep 1

# 2. Gateway - Port 8000
echo -e "${GREEN}[2/14]${NC} Starting Gateway & Dashboard (Port 8000)..."
cd services/gateway
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/aether-gateway.log 2>&1 &
cd ../..
sleep 2

# 3. Project & Environment Management - Port 8001
echo -e "${GREEN}[3/14]${NC} Starting Project Management (Port 8001)..."
cd services/project_and_environment_management
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8001 > /tmp/aether-projects.log 2>&1 &
cd ../..
sleep 1

# 4. Source & Cloud Connection - Port 8002
echo -e "${GREEN}[4/14]${NC} Starting Source Connection (Port 8002)..."
cd services/source_and_cloud_connection
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8002 > /tmp/aether-source.log 2>&1 &
cd ../..
sleep 1

# 5. Repo Analyzer - Port 8003
echo -e "${GREEN}[5/14]${NC} Starting Repo Analyzer (Port 8003)..."
cd services/repo_analyzer_service
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8003 > /tmp/aether-analyzer.log 2>&1 &
cd ../..
sleep 1

# 6. Requirement Analysis - Port 8004
echo -e "${GREEN}[6/14]${NC} Starting Requirement Analysis (Port 8004)..."
cd services/requirement_analysis
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8004 > /tmp/aether-requirements.log 2>&1 &
cd ../..
sleep 1

# 7. Architecture Generator - Port 8005
echo -e "${GREEN}[7/14]${NC} Starting Architecture Generator (Port 8005)..."
cd services/architecture_generator
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8005 > /tmp/aether-architecture.log 2>&1 &
cd ../..
sleep 1

# 8. IaC Generator - Port 8006
echo -e "${GREEN}[8/14]${NC} Starting IaC Generator (Port 8006)..."
cd services/iac_generator
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8006 > /tmp/aether-iac.log 2>&1 &
cd ../..
sleep 1

# 9. FinOps Optimizer - Port 8007
echo -e "${GREEN}[9/14]${NC} Starting FinOps Optimizer (Port 8007)..."
cd services/finops_optimizer
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8007 > /tmp/aether-finops.log 2>&1 &
cd ../..
sleep 1

# 10. Security Scanner - Port 8008
echo -e "${GREEN}[10/14]${NC} Starting Security Scanner (Port 8008)..."
cd services/security_scanner
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8008 > /tmp/aether-security.log 2>&1 &
cd ../..
sleep 1

# 11. CI/CD Pipeline - Port 8009
echo -e "${GREEN}[11/14]${NC} Starting CI/CD Pipeline (Port 8009)..."
cd services/cicd_pipeline
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8009 > /tmp/aether-cicd.log 2>&1 &
cd ../..
sleep 1

# 12. Observability Setup - Port 8010
echo -e "${GREEN}[12/14]${NC} Starting Observability Setup (Port 8010)..."
cd services/observability_setup
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8010 > /tmp/aether-observability.log 2>&1 &
cd ../..
sleep 1

# 13. Cloud Deployer - Port 8011
echo -e "${GREEN}[13/14]${NC} Starting Cloud Deployer (Port 8011)..."
cd services/cloud_deployer
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8011 > /tmp/aether-deployer.log 2>&1 &
cd ../..
sleep 1

# 14. Admin Console - Port 8012
echo -e "${GREEN}[14/14]${NC} Starting Admin Console (Port 8012)..."
cd services/admin_console
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8012 > /tmp/aether-admin.log 2>&1 &
cd ../..
sleep 2

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
echo -e "${YELLOW}To stop all services, run: pkill -f 'uvicorn app.main:app'${NC}"
