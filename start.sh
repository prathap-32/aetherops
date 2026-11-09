#!/bin/bash
# AetherOps - Unified Microservices Startup Script
#
# Usage:
#   ./start.sh          - Starts all 14 microservices in background, verifies health, and displays URLs
#   ./start.sh --watch  - Starts live interactive Rich telemetry watchdog (main.py)
#   ./start.sh --core   - Starts core microservices only (ports 7999-8005)
#   ./start.sh --stop   - Gracefully stops all AetherOps microservices

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi
export PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/shared:${PYTHONPATH:-}"
export AWS_REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-ap-south-1}}"
export AWS_SECRET_ID="${AWS_SECRET_ID:-${AETHER_SECRET_ID:-aetherops/platform}}"


# Activate virtual environment
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
else
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$SCRIPT_DIR/.venv"
    source "$SCRIPT_DIR/.venv/bin/activate"
    pip install -q --upgrade pip
    pip install -q fastapi uvicorn httpx pydantic rich pyjwt bcrypt
fi

PYTHON="$SCRIPT_DIR/.venv/bin/python"

# Handle CLI flags
if [ "$1" == "--stop" ]; then
    "$SCRIPT_DIR/stop-all-services.sh"
    exit 0
fi

if [ "$1" == "--watch" ] || [ "$1" == "-w" ]; then
    echo -e "${CYAN}Starting AetherOps Fleet Supervisor with Live Telemetry Watchdog...${NC}"
    exec $PYTHON "$SCRIPT_DIR/main.py"
fi

if [ "$1" == "--core" ]; then
    echo -e "${CYAN}Starting Core Microservices (Ports 7999-8005)...${NC}"
    exec "$SCRIPT_DIR/start-both.sh"
fi

# Default: Start all 14 services in background mode
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Starting AetherOps Cloud Platform     ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

"$SCRIPT_DIR/start-all-services.sh" --daemon

echo ""
echo -e "${GREEN}Verifying service health...${NC}"
sleep 2

PORTS=(7999 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009 8010)
NAMES=(
    "Auth Service"
    "Gateway & UI"
    "Project & Env"
    "Connect Cloud & Git"
    "Source Code Analyzer"
    "AI AWS Architecture"
    "IaC Generator"
    "Dry-Run & Approval"
    "Cloud Deployer"
    "Observability Infra"
    "User & Credentials"
    "Admin Console (Admin)"
)

ALL_HEALTHY=true
for i in "${!PORTS[@]}"; do
    port="${PORTS[$i]}"
    name="${NAMES[$i]}"
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${port}/health" 2>/dev/null || echo "000")
    if [ "$status_code" == "200" ]; then
        echo -e "  [${GREEN}ONLINE${NC}] Port ${port}: ${name}"
    else
        echo -e "  [${YELLOW}CHECKING${NC}] Port ${port}: ${name} (status: ${status_code})"
        ALL_HEALTHY=false
    fi
done

echo ""
echo -e "${GREEN}✓ AetherOps Platform is ready!${NC}"
echo -e "  Unified Web Dashboard: ${CYAN}http://localhost:8000${NC}"
echo -e "  API Documentation:     ${CYAN}http://localhost:8000/docs${NC}"
echo -e "  Default Credentials:   admin / admin123"
echo ""
echo -e "To view logs: ${YELLOW}tail -f /tmp/aether-*.log${NC}"
echo -e "To stop services: ${YELLOW}./start.sh --stop${NC}"
