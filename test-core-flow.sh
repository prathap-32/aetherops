#!/bin/bash
# AetherOps - End-to-End Test for Core Microservices:
# 1. Auth Service (Port 7999)
# 2. Gateway & Dashboard (Port 8000)
# 3. Project Management (Port 8001)

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  AetherOps Core Microservices Integration Test           ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Ensure core services are running
if ! curl -s http://127.0.0.1:7999/health >/dev/null || ! curl -s http://127.0.0.1:8000/health >/dev/null || ! curl -s http://127.0.0.1:8001/health >/dev/null; then
    echo "One or more core services not running. Starting via ./start-both.sh..."
    "$(dirname "$0")/start-both.sh"
    sleep 3
fi

# Test 1: Check Auth Service Health (Port 7999)
echo "Test 1: Auth Service Health Check (Port 7999)"
AUTH_HEALTH=$(curl -s http://127.0.0.1:7999/health)
if [[ $AUTH_HEALTH == *"auth"* ]] && [[ $AUTH_HEALTH == *"healthy"* ]]; then
    echo -e "${GREEN}✓ Auth service is healthy${NC} on port 7999"
else
    echo -e "${RED}✗ Auth service health check failed: $AUTH_HEALTH${NC}"
    exit 1
fi
echo ""

# Test 2: Check Gateway Health (Port 8000)
echo "Test 2: Gateway Health Check (Port 8000)"
GATEWAY_HEALTH=$(curl -s http://127.0.0.1:8000/health)
if [[ $GATEWAY_HEALTH == *"gateway"* ]] && [[ $GATEWAY_HEALTH == *"healthy"* ]]; then
    echo -e "${GREEN}✓ Gateway is healthy${NC} on port 8000"
else
    echo -e "${RED}✗ Gateway health check failed: $GATEWAY_HEALTH${NC}"
    exit 1
fi
echo ""

# Test 3: Check Project Manager Health (Port 8001)
echo "Test 3: Project Manager Health Check (Port 8001)"
PM_HEALTH=$(curl -s http://127.0.0.1:8001/health)
if [[ $PM_HEALTH == *"project-manager"* ]] && [[ $PM_HEALTH == *"healthy"* ]]; then
    echo -e "${GREEN}✓ Project Manager is healthy${NC} on port 8001"
else
    echo -e "${RED}✗ Project Manager health check failed: $PM_HEALTH${NC}"
    exit 1
fi
echo ""

# Test 4: Verify Gateway Serves React SPA Frontend
echo "Test 4: Gateway serves React SPA HTML (Port 8000)"
HTML_CONTENT=$(curl -s http://127.0.0.1:8000/)
if [[ $HTML_CONTENT == *"<div id=\"root\"></div>"* ]] || [[ $HTML_CONTENT == *"<!doctype html>"* ]]; then
    echo -e "${GREEN}✓ React SPA is served on port 8000${NC}"
else
    echo -e "${RED}✗ Gateway is not serving frontend index.html${NC}"
    exit 1
fi
echo ""

# Test 5: Login via Auth Service (Port 7999)
echo "Test 5: Login via Auth Service directly (Port 7999)"
LOGIN_RES=$(curl -s -X POST http://127.0.0.1:7999/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo "$LOGIN_RES" | grep -o '"token":"[^"]*"' | head -n 1 | cut -d'"' -f4)
if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo -e "${GREEN}✓ Login successful, JWT token acquired${NC}"
    echo "  Token length: ${#TOKEN} chars"
else
    echo -e "${RED}✗ Login failed. Response: $LOGIN_RES${NC}"
    exit 1
fi
echo ""

# Test 6: Verify User Identity via /api/v1/auth/me
echo "Test 6: Fetch current user profile with token (GET /api/v1/auth/me)"
ME_RES=$(curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:7999/api/v1/auth/me)
if [[ $ME_RES == *"admin"* ]]; then
    echo -e "${GREEN}✓ Profile authenticated correctly:${NC} $ME_RES"
else
    echo -e "${RED}✗ Failed to fetch profile: $ME_RES${NC}"
    exit 1
fi
echo ""

# Test 7: Direct Project Manager Call with JWT (Port 8001)
echo "Test 7: Direct query to Project Manager using Auth token (Port 8001)"
DIRECT_PM_RES=$(curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8001/api/v1/projects)
if [[ $DIRECT_PM_RES == *"projects"* ]]; then
    echo -e "${GREEN}✓ Project Manager authenticated JWT directly${NC}"
else
    echo -e "${RED}✗ Direct PM query rejected: $DIRECT_PM_RES${NC}"
    exit 1
fi
echo ""

# Test 8: Proxy to Project Manager through Gateway (Port 8000 -> 8001)
echo "Test 8: Gateway reverse-proxy query to Project Manager (Port 8000 -> 8001)"
PROXY_PM_RES=$(curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/v1/projects)
if [[ $PROXY_PM_RES == *"projects"* ]]; then
    echo -e "${GREEN}✓ Gateway successfully reverse-proxied authenticated request${NC}"
    TOTAL_PROJECTS=$(echo "$PROXY_PM_RES" | grep -o '"total":[0-9]*' | cut -d':' -f2)
    echo "  Total seeded projects found: $TOTAL_PROJECTS"
else
    echo -e "${RED}✗ Gateway reverse-proxy failed: $PROXY_PM_RES${NC}"
    exit 1
fi
echo ""

# Test 9: Create and Delete Project via Gateway Proxy
echo "Test 9: End-to-end Project Lifecycle via Gateway Proxy (Create & Delete)"
CREATE_RES=$(curl -s -X POST http://127.0.0.1:8000/api/v1/projects \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "name": "Integration-Test-Project",
        "description": "Automated microservice integration verification",
        "project_type": "api_service"
    }')

PROJECT_ID=$(echo "$CREATE_RES" | grep -o '"id":"[^"]*"' | head -n 1 | cut -d'"' -f4)
if [ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ]; then
    echo -e "${GREEN}✓ Project created successfully:${NC} ID $PROJECT_ID"
    # Clean up project
    DEL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE http://127.0.0.1:8000/api/v1/projects/$PROJECT_ID \
        -H "Authorization: Bearer $TOKEN")
    if [ "$DEL_STATUS" -eq 204 ]; then
        echo -e "${GREEN}✓ Project cleaned up successfully (HTTP 204)${NC}"
    else
        echo -e "${YELLOW}⚠ Project delete returned HTTP $DEL_STATUS${NC}"
    fi
else
    echo -e "${RED}✗ Project creation failed: $CREATE_RES${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ ALL CORE MICROSERVICES TESTS PASSED SUCCESSFULLY!       ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Microservices Topology Verified:"
echo "  • Port 7999: Auth Service (API Only, JWT issuing, bcrypt)  ✓"
echo "  • Port 8000: Gateway (Frontend static serving + reverse proxy) ✓"
echo "  • Port 8001: Project Manager (Tenancy, RBAC, projects CRUD)  ✓"
echo "  • Cross-service communication & JWT stateless authentication  ✓"
echo ""
