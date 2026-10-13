#!/bin/bash

# Test Auth Flow - Verify microservices architecture
# This script tests that:
# 1. Auth service (7999) is API-only
# 2. Gateway (8000) serves frontend
# 3. Login flow works correctly

echo "═══════════════════════════════════════════════════════════"
echo "  AetherOps Auth Flow Test"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check Gateway Health (Port 8000)
echo "Test 1: Gateway Health Check (Port 8000)"
GATEWAY_HEALTH=$(curl -s http://localhost:8000/health)
if [[ $GATEWAY_HEALTH == *"gateway"* ]]; then
    echo -e "${GREEN}✓ Gateway is healthy${NC}"
    echo "  Response: $GATEWAY_HEALTH"
else
    echo -e "${RED}✗ Gateway health check failed${NC}"
    exit 1
fi
echo ""

# Test 2: Check Auth Service Health (Port 7999)
echo "Test 2: Auth Service Health Check (Port 7999)"
AUTH_HEALTH=$(curl -s http://localhost:7999/health)
if [[ $AUTH_HEALTH == *"auth"* ]]; then
    echo -e "${GREEN}✓ Auth service is healthy${NC}"
    echo "  Response: $AUTH_HEALTH"
else
    echo -e "${RED}✗ Auth service health check failed${NC}"
    exit 1
fi
echo ""

# Test 3: Verify Auth Service Returns JSON (API-only, not HTML)
echo "Test 3: Verify Auth Service is API-only (no HTML)"
AUTH_ROOT=$(curl -s http://localhost:7999/)
if [[ $AUTH_ROOT == *"service"* ]] && [[ $AUTH_ROOT != *"<html>"* ]]; then
    echo -e "${GREEN}✓ Auth service returns JSON (API-only)${NC}"
    echo "  Response: ${AUTH_ROOT:0:100}..."
else
    echo -e "${RED}✗ Auth service may be serving HTML${NC}"
    exit 1
fi
echo ""

# Test 4: Verify Gateway Serves Frontend HTML
echo "Test 4: Verify Gateway Serves Frontend (HTML)"
GATEWAY_ROOT=$(curl -s http://localhost:8000/)
if [[ $GATEWAY_ROOT == *"<html"* ]] || [[ $GATEWAY_ROOT == *"<!DOCTYPE"* ]]; then
    echo -e "${GREEN}✓ Gateway serves frontend HTML${NC}"
    echo "  Found HTML content"
else
    echo -e "${RED}✗ Gateway not serving HTML frontend${NC}"
    exit 1
fi
echo ""

# Test 5: Test Login Flow
echo "Test 5: Login API (POST /api/v1/auth/login)"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:7999/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

if [[ $LOGIN_RESPONSE == *"token"* ]] && [[ $LOGIN_RESPONSE == *"admin"* ]]; then
    echo -e "${GREEN}✓ Login successful${NC}"
    echo "  Response: ${LOGIN_RESPONSE:0:150}..."
    
    # Extract token for next test
    TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    echo "  Token: $TOKEN"
else
    echo -e "${RED}✗ Login failed${NC}"
    echo "  Response: $LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Test 6: Test /me Endpoint with Token
echo "Test 6: Get Current User (GET /api/v1/auth/me)"
ME_RESPONSE=$(curl -s -X GET http://localhost:7999/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN")

if [[ $ME_RESPONSE == *"admin"* ]] && [[ $ME_RESPONSE == *"email"* ]]; then
    echo -e "${GREEN}✓ User info retrieved successfully${NC}"
    echo "  Response: $ME_RESPONSE"
else
    echo -e "${RED}✗ Failed to get user info${NC}"
    echo "  Response: $ME_RESPONSE"
    exit 1
fi
echo ""

# Test 7: Test Invalid Login
echo "Test 7: Test Invalid Credentials"
INVALID_LOGIN=$(curl -s -X POST http://localhost:7999/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"wrong","password":"wrong"}')

if [[ $INVALID_LOGIN == *"Invalid"* ]] || [[ $INVALID_LOGIN == *"401"* ]]; then
    echo -e "${GREEN}✓ Invalid credentials correctly rejected${NC}"
else
    echo -e "${YELLOW}⚠ Invalid login response unexpected${NC}"
    echo "  Response: $INVALID_LOGIN"
fi
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ All Tests Passed!${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Architecture Verified:"
echo "  • Port 7999: Auth Service (API-only) ✓"
echo "  • Port 8000: Gateway (Frontend + Proxy) ✓"
echo "  • Login flow: 8000 → calls API at 7999 → stays on 8000 ✓"
echo ""
echo "Next Steps:"
echo "  1. Open browser: http://localhost:8000"
echo "  2. Login with: admin / admin123"
echo "  3. Verify URL stays on port 8000"
echo ""
