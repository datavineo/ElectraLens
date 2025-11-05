#!/usr/bin/env python3
"""
Vercel Deployment Tester
Tests if your Vercel deployment is working correctly
"""

import sys
import json

try:
    import requests
except ImportError:
    print("❌ 'requests' module not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test_endpoint(base_url, endpoint, description):
    """Test a single endpoint"""
    url = f"{base_url}{endpoint}"
    print(f"\n{YELLOW}Testing: {description}{RESET}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        status = response.status_code
        
        if status == 200:
            print(f"{GREEN}✅ PASS - Status: {status}{RESET}")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)[:500]}")
            except:
                print(f"Response: {response.text[:200]}")
            return True
        else:
            print(f"{RED}❌ FAIL - Status: {status}{RESET}")
            print(f"Response: {response.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{RED}❌ FAIL - Cannot connect to URL{RESET}")
        print("Check if the URL is correct and deployment is running")
        return False
    except requests.exceptions.Timeout:
        print(f"{RED}❌ FAIL - Request timeout{RESET}")
        return False
    except Exception as e:
        print(f"{RED}❌ FAIL - Error: {str(e)}{RESET}")
        return False

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🔍 Vercel Deployment Checker{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Get URL from user or command line
    if len(sys.argv) > 1:
        vercel_url = sys.argv[1]
    else:
        print("📝 Please provide your Vercel deployment URL")
        print("   Example: https://electra-lens.vercel.app")
        print("   Or: https://electra-lens-xxxxx.vercel.app\n")
        vercel_url = input("Enter your Vercel URL: ").strip()
    
    # Clean up URL
    vercel_url = vercel_url.rstrip('/')
    
    if not vercel_url:
        print(f"{RED}❌ No URL provided{RESET}")
        sys.exit(1)
    
    if not vercel_url.startswith('http'):
        vercel_url = f"https://{vercel_url}"
    
    print(f"\n🧪 Testing deployment at: {vercel_url}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    # Test endpoints
    results = []
    
    tests = [
        ("/health", "Health Check Endpoint"),
        ("/", "API Root Endpoint"),
        ("/voters", "List Voters Endpoint"),
        ("/voters/summary", "Voters Summary Endpoint"),
        ("/status", "Status Endpoint"),
    ]
    
    for endpoint, description in tests:
        result = test_endpoint(vercel_url, endpoint, description)
        results.append((description, result))
        print(f"{'-'*60}")
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}📊 Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for description, result in results:
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"  {status} - {description}")
    
    print(f"\n{BLUE}Results: {passed}/{total} tests passed{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}🎉 SUCCESS! Your deployment is working perfectly!{RESET}\n")
        print("Next steps:")
        print(f"  1. Visit {vercel_url}/docs for API documentation")
        print(f"  2. Try the API endpoints in your browser")
        print(f"  3. Integrate with your frontend application")
    else:
        print(f"{RED}⚠️  Some tests failed. Troubleshooting steps:{RESET}\n")
        print("  1. Check Vercel Dashboard: https://vercel.com/dashboard")
        print("  2. View deployment logs in Vercel")
        print("  3. Check 'Function Logs' tab for errors")
        print(f"  4. Verify {vercel_url} is the correct URL")
    
    print("")

if __name__ == "__main__":
    main()
