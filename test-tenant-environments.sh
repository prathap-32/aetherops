#!/usr/bin/env bash
# ==============================================================================
# test-tenant-environments.sh
# End-to-end Verification for Module 1:
# 1. Verification of all 39 AWS regions metadata and 16 project types
# 2. Project creation with new project types
# 3. Environment creation with target project, name, tier type, and any AWS region
# 4. Strict tenant isolation between users (User A cannot see User B's projects/envs)
# 5. Static branding assets (aetherops_light.png) and favicon (logo.png)
# ==============================================================================

set -euo pipefail

BASE_URL="http://127.0.0.1:8000"
PASS=0
FAIL=0

green() { echo -e "\033[32m✔ $1\033[0m"; PASS=$((PASS+1)); }
red()   { echo -e "\033[31m✖ $1\033[0m"; FAIL=$((FAIL+1)); }
info()  { echo -e "\033[34mℹ $1\033[0m"; }

echo "================================================================="
echo "  AetherOps E2E Test: Multi-Tenant Environments & Branding       "
echo "================================================================="

# -----------------------------------------------------------------------------
# 1. Branding and Favicon
# -----------------------------------------------------------------------------
info "Test 1: Verifying Static Branding Assets and Favicon"
FAV_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/favicon.png")
if [ "$FAV_CODE" = "200" ]; then
    green "Favicon endpoint /favicon.png returned HTTP 200"
else
    red "Favicon endpoint returned HTTP $FAV_CODE"
fi

FAV_ICO_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/favicon.ico")
if [ "$FAV_ICO_CODE" = "200" ]; then
    green "Favicon endpoint /favicon.ico returned HTTP 200"
else
    red "Favicon /favicon.ico returned HTTP $FAV_ICO_CODE"
fi

LOGO_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/static/logo/aetherops_light.png")
if [ "$LOGO_CODE" = "200" ]; then
    green "Brand logo /static/logo/aetherops_light.png returned HTTP 200"
else
    red "Brand logo returned HTTP $LOGO_CODE"
fi

# -----------------------------------------------------------------------------
# 2. Metadata: 39 AWS Regions, 16 Project Types, 9 Tier Types
# -----------------------------------------------------------------------------
info "Test 2: Verifying Metadata Endpoints"
REGIONS_RES=$(curl -s "$BASE_URL/api/v1/meta/regions")
REGIONS_COUNT=$(echo "$REGIONS_RES" | jq -r '.total')
if [ "$REGIONS_COUNT" -eq 39 ]; then
    green "AWS Regions count is exactly 39 (includes mx-central-1, ap-south-2, etc.)"
else
    red "AWS Regions count expected 39, got: $REGIONS_COUNT"
fi

PROJ_TYPES_RES=$(curl -s "$BASE_URL/api/v1/meta/project-types")
PROJ_TYPES_COUNT=$(echo "$PROJ_TYPES_RES" | jq -r '.total')
if [ "$PROJ_TYPES_COUNT" -ge 16 ]; then
    green "Project types count is $PROJ_TYPES_COUNT (>= 16 project types supported)"
else
    red "Project types count expected >= 16, got: $PROJ_TYPES_COUNT"
fi

# -----------------------------------------------------------------------------
# 3. User A (admin) Login & Project/Environment Creation
# -----------------------------------------------------------------------------
info "Test 3: User 'admin' Login and Project/Environment Provisioning"
ADMIN_AUTH=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}')
ADMIN_TOKEN=$(echo "$ADMIN_AUTH" | jq -r '.token // .access_token // empty')

if [ -n "$ADMIN_TOKEN" ]; then
    green "Admin authenticated successfully"
else
    red "Admin authentication failed: $ADMIN_AUTH"
    exit 1
fi

ADMIN_PROJ_NAME="Admin-CloudBackend-$RANDOM"
ADMIN_PROJ_RES=$(curl -s -X POST "$BASE_URL/api/v1/projects" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"$ADMIN_PROJ_NAME\",
        \"description\": \"Serverless and event driven core\",
        \"project_type\": \"serverless_backend\"
    }")
ADMIN_PROJ_ID=$(echo "$ADMIN_PROJ_RES" | jq -r '.id // empty')

if [ -n "$ADMIN_PROJ_ID" ]; then
    green "Admin project created: '$ADMIN_PROJ_NAME' (id: $ADMIN_PROJ_ID, type: serverless_backend)"
else
    red "Failed to create Admin project: $ADMIN_PROJ_RES"
    exit 1
fi

# Create Environment for Admin in Mexico Central (mx-central-1) with Disaster Recovery tier
ADMIN_ENV_RES=$(curl -s -X POST "$BASE_URL/api/v1/projects/$ADMIN_PROJ_ID/environments" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Production-DR",
        "env_type": "disaster_recovery",
        "aws_region": "mx-central-1",
        "description": "Cross-region disaster recovery standby fleet"
    }')
ADMIN_ENV_ID=$(echo "$ADMIN_ENV_RES" | jq -r '.id // empty')

if [ -n "$ADMIN_ENV_ID" ]; then
    green "Admin environment created: 'Production-DR' in region 'mx-central-1' (tier: disaster_recovery)"
else
    red "Failed to create Admin environment: $ADMIN_ENV_RES"
fi

# -----------------------------------------------------------------------------
# 4. User B (tenant2) Registration & Tenant Isolation Verification
# -----------------------------------------------------------------------------
info "Test 4: User B (tenant isolation verification)"
USER_B="tenant_dev_$RANDOM"
REGISTER_RES=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"username\": \"$USER_B\",
        \"email\": \"$USER_B@example.com\",
        \"password\": \"password123\"
    }")
USER_B_TOKEN=$(echo "$REGISTER_RES" | jq -r '.token // .access_token // empty')

if [ -z "$USER_B_TOKEN" ]; then
    # Try login in case user already existed
    LOGIN_B=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$USER_B\",\"password\":\"password123\"}")
    USER_B_TOKEN=$(echo "$LOGIN_B" | jq -r '.token // .access_token // empty')
fi

if [ -n "$USER_B_TOKEN" ]; then
    green "User B ('$USER_B') registered/authenticated successfully"
else
    red "User B authentication failed: $REGISTER_RES"
    exit 1
fi

# Check that User B DOES NOT see Admin's project
USER_B_PROJS=$(curl -s "$BASE_URL/api/v1/projects" \
    -H "Authorization: Bearer $USER_B_TOKEN")
CONTAINS_ADMIN_PROJ=$(echo "$USER_B_PROJS" | jq -r --arg pid "$ADMIN_PROJ_ID" '.projects[]? | select(.id == $pid) | .name')

if [ -z "$CONTAINS_ADMIN_PROJ" ]; then
    green "Tenant Isolation Verified: User B CANNOT see Admin's project '$ADMIN_PROJ_NAME'"
else
    red "Tenant Isolation VIOLATION: User B can see Admin project '$CONTAINS_ADMIN_PROJ'"
fi

# User B creates their own project and environment
USER_B_PROJ_NAME="IoT-Telemetry-$RANDOM"
USER_B_PROJ_RES=$(curl -s -X POST "$BASE_URL/api/v1/projects" \
    -H "Authorization: Bearer $USER_B_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"$USER_B_PROJ_NAME\",
        \"description\": \"Edge telemetry ingest pipeline\",
        \"project_type\": \"iot_ingestion\"
    }")
USER_B_PROJ_ID=$(echo "$USER_B_PROJ_RES" | jq -r '.id // empty')

if [ -n "$USER_B_PROJ_ID" ]; then
    green "User B project created: '$USER_B_PROJ_NAME' (id: $USER_B_PROJ_ID, type: iot_ingestion)"
else
    red "Failed to create User B project: $USER_B_PROJ_RES"
fi

# User B creates an environment via the root /api/v1/environments endpoint
USER_B_ENV_RES=$(curl -s -X POST "$BASE_URL/api/v1/environments" \
    -H "Authorization: Bearer $USER_B_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"project_id\": \"$USER_B_PROJ_ID\",
        \"name\": \"Edge-Sandbox\",
        \"env_type\": \"sandbox\",
        \"aws_region\": \"ap-south-2\",
        \"description\": \"Hyderabad sandbox environment\"
    }")
USER_B_ENV_ID=$(echo "$USER_B_ENV_RES" | jq -r '.id // empty')

if [ -n "$USER_B_ENV_ID" ]; then
    green "User B environment created via /api/v1/environments: 'Edge-Sandbox' in 'ap-south-2' (tier: sandbox)"
else
    red "Failed to create User B environment: $USER_B_ENV_RES"
fi

# Check that Admin DOES NOT see User B's project
ADMIN_PROJS_AFTER=$(curl -s "$BASE_URL/api/v1/projects" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
CONTAINS_USER_B_PROJ=$(echo "$ADMIN_PROJS_AFTER" | jq -r --arg pid "$USER_B_PROJ_ID" '.projects[]? | select(.id == $pid) | .name')

if [ -z "$CONTAINS_USER_B_PROJ" ]; then
    green "Tenant Isolation Verified: Admin CANNOT see User B's project '$USER_B_PROJ_NAME'"
else
    red "Tenant Isolation VIOLATION: Admin can see User B's project '$CONTAINS_USER_B_PROJ'"
fi

# User B cannot access Admin's project directly (should return 404 or 403)
UNAUTH_ACCESS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/projects/$ADMIN_PROJ_ID" \
    -H "Authorization: Bearer $USER_B_TOKEN")
if [ "$UNAUTH_ACCESS_STATUS" = "404" ] || [ "$UNAUTH_ACCESS_STATUS" = "403" ]; then
    green "Direct unauthorized project access blocked with HTTP $UNAUTH_ACCESS_STATUS"
else
    red "Direct unauthorized project access expected 403/404, got: $UNAUTH_ACCESS_STATUS"
fi

echo "================================================================="
echo "  Test Summary: $PASS passed, $FAIL failed                       "
echo "================================================================="

if [ "$FAIL" -eq 0 ]; then
    exit 0
else
    exit 1
fi
