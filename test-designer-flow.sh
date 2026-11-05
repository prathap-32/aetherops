#!/usr/bin/env bash
# test-designer-flow.sh — Architecture Designer Canvas Integration Test

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  AetherOps Architecture Designer (Interactive Canvas) Flow ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Test 1: Gateway SPA route for /architecture-designer
echo -e "\n${BLUE}Test 1: Gateway serves React SPA for /architecture-designer${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/architecture-designer)
if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Clean URL /architecture-designer returns HTTP 200 OK!${NC}"
else
    echo -e "${RED}✗ Failed: Expected 200, got $HTTP_CODE${NC}"
    exit 1
fi

# Test 2: Architecture Studio Service Health Check on Port 8005
echo -e "\n${BLUE}Test 2: Direct Cloud Architecture Studio Health Check (Port 8005)${NC}"
STUDIO_HEALTH=$(curl -s http://127.0.0.1:8005/health)
echo "Response: $STUDIO_HEALTH"
if echo "$STUDIO_HEALTH" | grep -q "cloud-architecture-studio"; then
    echo -e "${GREEN}✓ Cloud Architecture Studio is healthy on Port 8005!${NC}"
else
    echo -e "${RED}✗ Cloud Architecture Studio health check failed.${NC}"
    exit 1
fi

echo -e "\n${BLUE}Acquiring authentication token via Gateway...${NC}"
AUTH_RES=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')
TOKEN=$(echo "$AUTH_RES" | grep -o '"token":"[^"]*"' | head -n 1 | cut -d'"' -f4)
if [ -z "$TOKEN" ]; then
  echo -e "${RED}✗ Failed to acquire token from Gateway${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Acquired JWT token from Gateway${NC}"

# Test 3: Save Canvas State to Architecture Studio (Port 8000 -> 8004)
echo -e "\n${BLUE}Test 3: Save Canvas Topology State via Gateway (Port 8000 -> 8004)${NC}"
SAVE_RES=$(curl -s -X POST http://127.0.0.1:8000/api/v1/architecture/studio/save \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test-canvas-proj",
    "environment_tier": "development",
    "target_region": "us-east-1",
    "monthly_cost_usd": 6.12,
    "nodes": [
      {"id": "vpc_1", "serviceType": "vpc", "name": "VPC: 10.0.0.0/16", "isContainer": true, "cost": 0},
      {"id": "ec2_1", "serviceType": "ec2", "name": "EC2 Docker Host", "isContainer": false, "cost": 6.12}
    ],
    "edges": [
      {"id": "e1", "source": "vpc_1", "target": "ec2_1", "label": "TCP:8080"}
    ]
  }')
echo "Response: $SAVE_RES"
if echo "$SAVE_RES" | grep -q "saved"; then
    echo -e "${GREEN}✓ Canvas topology saved successfully!${NC}"
else
    echo -e "${RED}✗ Failed to save canvas topology.${NC}"
    exit 1
fi

# Test 4: Retrieve Canvas State
echo -e "\n${BLUE}Test 4: Retrieve Canvas State (Port 8000 -> 8004)${NC}"
GET_RES=$(curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8000/api/v1/architecture/studio/state?project_id=test-canvas-proj&environment_id=")
echo "Response: $GET_RES"
if echo "$GET_RES" | grep -q "test-canvas-proj"; then
    echo -e "${GREEN}✓ Canvas topology retrieved successfully!${NC}"
else
    echo -e "${RED}✗ Failed to retrieve canvas state.${NC}"
    exit 1
fi

# Test 5: Validate Topology Compliance
echo -e "\n${BLUE}Test 5: Well-Architected Framework Compliance Validation${NC}"
VAL_RES=$(curl -s -X POST http://127.0.0.1:8000/api/v1/architecture/validate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "environment_tier": "development",
    "nodes": [
      {"id": "ingress", "data": {"type": "ingress"}},
      {"id": "compute", "data": {"type": "compute", "monthly_cost": 6.12}}
    ],
    "edges": [
      {"id": "e1", "source": "ingress", "target": "compute"}
    ]
  }')
echo "Response: $VAL_RES"
if echo "$VAL_RES" | grep -E -q "VALID|PASS"; then
    echo -e "${GREEN}✓ Canvas topology passed Well-Architected validation!${NC}"
else
    echo -e "${RED}✗ Topology validation failed.${NC}"
    exit 1
fi

echo -e "\n${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ ALL ARCHITECTURE DESIGNER TESTS PASSED (5/5)!           ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
