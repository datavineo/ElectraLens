#!/bin/bash

# Test Vercel Deployment
# This script helps you verify if your Vercel deployment is working

echo "🔍 Vercel Deployment Checker"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📝 Please provide your Vercel deployment URL"
echo "   (e.g., https://electra-lens.vercel.app or https://electra-lens-xxxxx.vercel.app)"
echo ""
read -p "Enter your Vercel URL: " VERCEL_URL

# Remove trailing slash if present
VERCEL_URL=${VERCEL_URL%/}

if [ -z "$VERCEL_URL" ]; then
    echo -e "${RED}❌ No URL provided${NC}"
    exit 1
fi

echo ""
echo "🧪 Testing your deployment at: $VERCEL_URL"
echo "=========================================="
echo ""

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local description=$2
    
    echo -e "${YELLOW}Testing: $description${NC}"
    echo "URL: $VERCEL_URL$endpoint"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$VERCEL_URL$endpoint" 2>&1)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ PASS - Status: $response${NC}"
        # Show response body for successful requests
        curl -s "$VERCEL_URL$endpoint" | head -c 500
        echo ""
    elif [ "$response" = "000" ]; then
        echo -e "${RED}❌ FAIL - Cannot connect to URL${NC}"
    else
        echo -e "${RED}❌ FAIL - Status: $response${NC}"
    fi
    echo ""
    echo "---"
    echo ""
}

# Test endpoints
echo "1️⃣ Health Check Endpoint"
test_endpoint "/health" "Health Check"

echo "2️⃣ Root Endpoint"
test_endpoint "/" "API Root"

echo "3️⃣ Voters List Endpoint"
test_endpoint "/voters" "List Voters"

echo "4️⃣ API Documentation"
test_endpoint "/docs" "Swagger UI"

echo "5️⃣ Voters Summary"
test_endpoint "/voters/summary" "Voters Summary"

echo ""
echo "=============================="
echo "📊 Test Summary"
echo "=============================="
echo ""
echo "If all tests show ${GREEN}✅ PASS${NC}, your deployment is working!"
echo ""
echo "Next steps:"
echo "1. Visit $VERCEL_URL/docs for interactive API documentation"
echo "2. Check Vercel Dashboard for deployment logs"
echo "3. If you see errors, check: https://vercel.com/dashboard"
echo ""
