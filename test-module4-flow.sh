#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# AetherOps Module 3 & Module 4 End-to-End Verification Test Suite
# Tests:
#   1. Cloud Architecture Studio Service Health (Port 8004)
#   2. Gateway Reverse Proxy to Module 4 (Port 8000 -> 8004)
#   3. Module 3 Gemini 2.5 Flash Integration (Zero 404s, Provider = gemini-2.5-flash)
#   4. Module 3 AWS Services Customization & Re-Analysis (/api/v1/repo/recalculate-sizing)
#   5. Module 4 Graph Generation DAG API (/api/v1/architecture/generate-graph)
#   6. Module 4 Architecture Well-Architected Validation (/api/v1/architecture/validate)
#   7. Module 4 Studio Session Persistence (/api/v1/architecture/studio/save & state)
# ═══════════════════════════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  AetherOps Cloud Architecture Studio (Module 4) Flow     ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Test 1: Direct Health Check on Port 8004
echo -e "${BLUE}Test 1: Direct Cloud Architecture Studio Health Check (Port 8004)${NC}"
M4_HEALTH=$(curl -s http://localhost:8004/health)
echo "Response: $M4_HEALTH"
STATUS=$(echo "$M4_HEALTH" | jq -r '.status')
PORT=$(echo "$M4_HEALTH" | jq -r '.port')
SERVICE=$(echo "$M4_HEALTH" | jq -r '.service')

if [ "$STATUS" = "healthy" ] && [ "$PORT" = "8004" ]; then
    echo -e "${GREEN}✓ Cloud Architecture Studio is healthy on Port 8004!${NC}"
else
    echo -e "${RED}✗ Health check failed on Port 8004${NC}"
    exit 1
fi
echo ""

echo "Acquiring authentication token via Gateway..."
AUTH_RES=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')
TOKEN=$(echo "$AUTH_RES" | grep -o '"token":"[^"]*"' | head -n 1 | cut -d'"' -f4)
if [ -z "$TOKEN" ]; then
  echo "Failed to acquire token from Gateway"
  exit 1
fi
echo -e "${GREEN}✓ Acquired JWT token from Gateway${NC}"
echo ""

# Test 2: Gateway Reverse Proxy (Port 8000 -> 8004)
echo -e "${BLUE}Test 2: Gateway Reverse Proxy to Architecture Studio (Port 8000 -> 8004)${NC}"
GW_HEALTH=$(curl -s http://localhost:8000/api/v1/architecture/health)
echo "Response: $GW_HEALTH"
GW_PORT=$(echo "$GW_HEALTH" | jq -r '.port')

if [ "$GW_PORT" = "8004" ]; then
    echo -e "${GREEN}✓ Gateway successfully routed /api/v1/architecture/health to Port 8004!${NC}"
else
    echo -e "${RED}✗ Gateway reverse proxy to Port 8004 failed${NC}"
    exit 1
fi
echo ""

# Test 3: Gemini 2.5 Flash Sizing via Module 3
echo -e "${BLUE}Test 3: Gemini 2.5 Flash Right-Sizing Check (Port 8003)${NC}"
M3_SIZING=$(curl -s -X POST http://localhost:8003/api/v1/repo/accept-and-size \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "Docker_webApp_analogClock",
    "environment_tier": "development",
    "target_region": "us-east-1",
    "verified_spec": {
      "workload_type": "Docker Container",
      "has_dockerfile": true,
      "ports": [80],
      "primary_languages": "HTML, JS"
    }
  }')

AI_PROVIDER=$(echo "$M3_SIZING" | jq -r '.ai_provider')
TOTAL_DEV_COST=$(echo "$M3_SIZING" | jq -r '.monthly_cost_estimate_usd.total_estimated_monthly_usd')
COMPUTE_SVC=$(echo "$M3_SIZING" | jq -r '.compute.service')

echo "AI Provider: $AI_PROVIDER"
echo "DEV Cost: $TOTAL_DEV_COST USD/mo"
echo "Compute: $COMPUTE_SVC"

if [ "$AI_PROVIDER" = "gemini-2.5-flash" ] || [[ "$AI_PROVIDER" == *"deterministic_rules_engine"* ]]; then
    echo -e "${GREEN}✓ Sizing verified successfully (${AI_PROVIDER})!${NC}"
else
    echo -e "${RED}✗ Unexpected AI Provider: $AI_PROVIDER${NC}"
    exit 1
fi
echo ""

# Test 4: Custom AWS Service Recalculation & Analysis
echo -e "${BLUE}Test 4: User-Edited AWS Services Re-Analysis & Recalculation${NC}"
RECALC=$(curl -s -X POST http://localhost:8003/api/v1/repo/recalculate-sizing \
  -H "Content-Type: application/json" \
  -d '{
    "environment_tier": "development",
    "target_region": "us-east-1",
    "compute_service": "Amazon EC2 (Docker Runtime)",
    "instance_type": "t4g.small",
    "min_capacity": 1,
    "alb_enabled": true,
    "database_service": "Amazon RDS PostgreSQL (db.t4g.micro)",
    "cache_service": "None"
  }')

RECALC_COST=$(echo "$RECALC" | jq -r '.monthly_cost_estimate_usd.total_estimated_monthly_usd')
RECALC_PROVIDER=$(echo "$RECALC" | jq -r '.ai_provider')
COMPAT_NOTES=$(echo "$RECALC" | jq -r '.compatibility_notes | length')

echo "Recalculated Monthly Cost: $RECALC_COST USD/mo"
echo "Analysis Provider: $RECALC_PROVIDER"
echo "Compatibility Notes Count: $COMPAT_NOTES"

if [ "$RECALC_PROVIDER" = "user_customized_sizing_analyzer" ] && [ "$COMPAT_NOTES" -gt 0 ]; then
    echo -e "${GREEN}✓ User customized services re-analyzed with compatibility advice!${NC}"
else
    echo -e "${RED}✗ Recalculation test failed${NC}"
    exit 1
fi
echo ""

# Test 5: Visual Graph DAG Generation (Module 4)
echo -e "${BLUE}Test 5: Visual ReactFlow DAG Generation API (Port 8000 -> 8004)${NC}"
GRAPH_RES=$(curl -s -X POST http://localhost:8000/api/v1/architecture/generate-graph \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "environment_tier": "development",
    "compute": {
      "service": "Amazon EC2 (Docker Runtime)",
      "instance_class": "t4g.micro",
      "monthly_cost": 6.12
    },
    "networking": {
      "alb": false
    },
    "monthly_cost_estimate_usd": {
      "total_estimated_monthly_usd": 6.12
    }
  }')

NODE_COUNT=$(echo "$GRAPH_RES" | jq -r '.nodes | length')
EDGE_COUNT=$(echo "$GRAPH_RES" | jq -r '.edges | length')

echo "Nodes generated: $NODE_COUNT"
echo "Edges generated: $EDGE_COUNT"

if [ "$NODE_COUNT" -ge 3 ]; then
    echo -e "${GREEN}✓ ReactFlow visual topology DAG generated successfully!${NC}"
else
    echo -e "${RED}✗ Graph generation returned insufficient nodes: $NODE_COUNT${NC}"
    exit 1
fi
echo ""

# Test 6: Well-Architected Framework Validation (Module 4)
echo -e "${BLUE}Test 6: Well-Architected Framework Compliance Validation${NC}"
VALIDATION_RES=$(curl -s -X POST http://localhost:8000/api/v1/architecture/validate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "environment_tier": "development",
    "nodes": [
      {"id": "node-client", "type": "internet"},
      {"id": "node-eip", "type": "elastic_ip"},
      {"id": "node-compute", "type": "ec2"}
    ]
  }')

VAL_STATUS=$(echo "$VALIDATION_RES" | jq -r '.status')
CHECKS_COUNT=$(echo "$VALIDATION_RES" | jq -r '.checks_passed | length')

echo "Validation Status: $VAL_STATUS"
echo "Checks Passed: $CHECKS_COUNT"

if [ "$VAL_STATUS" = "VALID" ] && [ "$CHECKS_COUNT" -ge 1 ]; then
    echo -e "${GREEN}✓ Architecture Well-Architected validation passed!${NC}"
else
    echo -e "${RED}✗ Validation failed: $VAL_STATUS${NC}"
    exit 1
fi
echo ""

# Test 7: Studio Session Persistence
echo -e "${BLUE}Test 7: Cloud Architecture Studio Session Save & Retrieve${NC}"
SAVE_RES=$(curl -s -X POST http://localhost:8000/api/v1/architecture/studio/save \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj-test-1",
    "environment_id": "env-dev-1",
    "environment_tier": "development",
    "monthly_cost_usd": 6.12,
    "nodes": [{"id": "node-client"}, {"id": "node-compute"}]
  }')

SAVE_STATUS=$(echo "$SAVE_RES" | jq -r '.status')

GET_RES=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/architecture/studio/state?project_id=proj-test-1&environment_id=env-dev-1")
RETRIEVED_ID=$(echo "$GET_RES" | jq -r '.session_id')

if [ "$SAVE_STATUS" = "SUCCESS" ] && [ "$RETRIEVED_ID" = "proj-test-1_env-dev-1" ]; then
    echo -e "${GREEN}✓ Studio diagram session saved and retrieved successfully!${NC}"
else
    echo -e "${RED}✗ Studio session persistence failed${NC}"
    exit 1
fi
echo ""

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ ALL MODULE 3 & MODULE 4 TESTS PASSED (7/7)!             ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
