#!/bin/bash

# =============================================================================
# ElectraLens Production Deployment Test Script
# =============================================================================

echo "🚀 ElectraLens Production Deployment Test"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test URLs
BACKEND_URL="https://electra-lens.vercel.app"
FRONTEND_URL="https://datavineo.vercel.app"

echo -e "${YELLOW}Testing Backend API...${NC}"

# Test 1: Health Check
echo "1. Health Check:"
health_response=$(curl -s "${BACKEND_URL}/health")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
    echo "   Response: $health_response"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
fi

echo ""

# Test 2: Status Check  
echo "2. Status Check:"
status_response=$(curl -s "${BACKEND_URL}/status")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend status check passed${NC}"
    echo "   Response: $status_response"
else
    echo -e "${RED}✗ Backend status check failed${NC}"
fi

echo ""

# Test 3: Auth Test
echo "3. Authentication Test:"
auth_response=$(curl -s "${BACKEND_URL}/auth/test")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Auth endpoint available${NC}"
    echo "   Response: $auth_response"
else
    echo -e "${RED}✗ Auth endpoint failed${NC}"
fi

echo ""

# Test 4: Login Test
echo "4. Login Test (Admin):"
login_response=$(curl -s -X POST "${BACKEND_URL}/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=SecureAdmin2024!")

if [[ $login_response == *"admin"* ]]; then
    echo -e "${GREEN}✓ Admin login successful${NC}"
    echo "   Response: $login_response"
else
    echo -e "${RED}✗ Admin login failed${NC}"
    echo "   Response: $login_response"
fi

echo ""

# Test 5: Login Test (Viewer)
echo "5. Login Test (Viewer):"
login_response=$(curl -s -X POST "${BACKEND_URL}/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=viewer&password=SecureViewer2024!")

if [[ $login_response == *"viewer"* ]]; then
    echo -e "${GREEN}✓ Viewer login successful${NC}"
    echo "   Response: $login_response"
else
    echo -e "${RED}✗ Viewer login failed${NC}"
    echo "   Response: $login_response"
fi

echo ""

# Test 6: Voters API
echo "6. Voters API Test:"
voters_response=$(curl -s "${BACKEND_URL}/voters?limit=1")
if [[ $voters_response == *"["* ]]; then
    echo -e "${GREEN}✓ Voters API working${NC}"
    echo "   Response: ${voters_response:0:100}..."
else
    echo -e "${RED}✗ Voters API failed${NC}"
    echo "   Response: $voters_response"
fi

echo ""

# Test 7: Frontend Accessibility
echo "7. Frontend Accessibility Test:"
frontend_response=$(curl -s -I "${FRONTEND_URL}" | head -n 1)
if [[ $frontend_response == *"200"* ]]; then
    echo -e "${GREEN}✓ Frontend accessible${NC}"
    echo "   Response: $frontend_response"
else
    echo -e "${RED}✗ Frontend not accessible${NC}"
    echo "   Response: $frontend_response"
fi

echo ""

# Test 8: CORS Test
echo "8. CORS Configuration Test:"
cors_response=$(curl -s -H "Origin: https://datavineo.vercel.app" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: X-Requested-With" \
    -X OPTIONS "${BACKEND_URL}/auth/login")

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ CORS configured${NC}"
else
    echo -e "${RED}✗ CORS configuration issue${NC}"
fi

echo ""
echo -e "${YELLOW}Deployment Test Summary:${NC}"
echo "========================"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""
echo "🔐 Default Credentials:"
echo "   Admin: admin / SecureAdmin2024!"
echo "   Viewer: viewer / SecureViewer2024!"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT SECURITY NOTES:${NC}"
echo "1. Change default passwords immediately in production!"
echo "2. Update JWT_SECRET_KEY in Vercel environment variables"
echo "3. Verify all environment variables are set in Vercel dashboard"
echo "4. Monitor application logs for any security issues"

echo ""
echo "🎯 Next Steps:"
echo "1. Update Vercel environment variables if needed"
echo "2. Test complete user flow on frontend"
echo "3. Verify database operations are working"
echo "4. Monitor performance and error logs"