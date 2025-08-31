#!/bin/bash

# DataCharted Domain Redirect Testing Script
# This script tests that the redirect from datacharted.com to app.datacharted.com is working correctly

echo "🧪 DataCharted Domain Redirect Testing"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    echo -e "${BLUE}Testing:${NC} $test_name"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Run the command and capture output
    output=$(eval "$test_command" 2>&1)
    exit_code=$?
    
    # Check if the expected pattern is found
    if echo "$output" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        echo -e "${YELLOW}Expected:${NC} $expected_pattern"
        echo -e "${YELLOW}Got:${NC} $output"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Function to test DNS resolution
test_dns() {
    echo -e "${BLUE}🌐 DNS Resolution Tests${NC}"
    echo "------------------------"
    
    run_test "DNS resolution for datacharted.com" \
        "nslookup datacharted.com | grep 'Address:' | tail -1" \
        "165.232.38.9"
    
    run_test "DNS resolution for www.datacharted.com" \
        "nslookup www.datacharted.com | grep 'Address:' | tail -1" \
        "165.232.38.9"
    
    run_test "DNS resolution for app.datacharted.com (should remain unchanged)" \
        "nslookup app.datacharted.com | grep 'Address:' | tail -1" \
        "165.232.38.9"
    
    echo ""
}

# Function to test HTTP redirects
test_http_redirects() {
    echo -e "${BLUE}🔄 HTTP Redirect Tests${NC}"
    echo "----------------------"
    
    run_test "HTTP redirect from datacharted.com" \
        "curl -s -I http://datacharted.com" \
        "301.*https://app.datacharted.com"
    
    run_test "HTTP redirect from www.datacharted.com" \
        "curl -s -I http://www.datacharted.com" \
        "301.*https://app.datacharted.com"
    
    run_test "Path preservation test" \
        "curl -s -I http://datacharted.com/test/path" \
        "https://app.datacharted.com/test/path"
    
    run_test "Query parameter preservation test" \
        "curl -s -I 'http://datacharted.com/page?param=value'" \
        "https://app.datacharted.com/page?param=value"
    
    echo ""
}

# Function to test HTTPS redirects (if SSL is configured)
test_https_redirects() {
    echo -e "${BLUE}🔒 HTTPS Redirect Tests${NC}"
    echo "-----------------------"
    
    # Test if HTTPS is configured
    if curl -s -I https://datacharted.com >/dev/null 2>&1; then
        echo "HTTPS is configured, testing HTTPS redirects..."
        
        run_test "HTTPS redirect from datacharted.com" \
            "curl -s -I https://datacharted.com" \
            "301.*https://app.datacharted.com"
        
        run_test "HTTPS redirect from www.datacharted.com" \
            "curl -s -I https://www.datacharted.com" \
            "301.*https://app.datacharted.com"
    else
        echo -e "${YELLOW}⚠️  HTTPS not configured - skipping HTTPS tests${NC}"
        echo "To set up HTTPS, run: certbot --nginx -d datacharted.com -d www.datacharted.com"
    fi
    
    echo ""
}

# Function to test app.datacharted.com still works
test_app_functionality() {
    echo -e "${BLUE}🎯 App Functionality Tests${NC}"
    echo "--------------------------"
    
    run_test "app.datacharted.com is accessible" \
        "curl -s -I https://app.datacharted.com" \
        "200 OK"
    
    run_test "app.datacharted.com serves content" \
        "curl -s https://app.datacharted.com | head -10" \
        "DataCharted\|html\|<!DOCTYPE"
    
    echo ""
}

# Function to check server logs
check_server_logs() {
    echo -e "${BLUE}📋 Server Log Check${NC}"
    echo "-------------------"
    
    if ssh -o ConnectTimeout=5 root@165.232.38.9 "test -f /var/log/nginx/datacharted-redirect.access.log" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} Nginx redirect logs are being created"
        
        # Show recent redirect activity
        echo "Recent redirect activity:"
        ssh root@165.232.38.9 "tail -5 /var/log/nginx/datacharted-redirect.access.log 2>/dev/null || echo 'No recent activity'"
    else
        echo -e "${YELLOW}⚠️${NC}  Cannot access server logs (SSH required)"
        echo "To check logs manually: ssh root@165.232.38.9 'tail -f /var/log/nginx/datacharted-redirect.access.log'"
    fi
    
    echo ""
}

# Function to test from multiple DNS servers
test_dns_propagation() {
    echo -e "${BLUE}🌍 DNS Propagation Tests${NC}"
    echo "-------------------------"
    
    # Test against different DNS servers
    dns_servers=("8.8.8.8" "1.1.1.1" "208.67.222.222")
    
    for dns in "${dns_servers[@]}"; do
        run_test "DNS propagation check via $dns" \
            "nslookup datacharted.com $dns | grep 'Address:' | tail -1" \
            "165.232.38.9"
    done
    
    echo ""
}

# Function to show summary
show_summary() {
    echo -e "${BLUE}📊 Test Summary${NC}"
    echo "==============="
    echo "Total Tests: $TOTAL_TESTS"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed! Your domain redirect is working perfectly.${NC}"
        echo ""
        echo "✅ Users can now access your app via:"
        echo "   • https://datacharted.com"
        echo "   • https://www.datacharted.com"  
        echo "   • https://app.datacharted.com"
        echo ""
        echo "🔗 All URLs redirect to: https://app.datacharted.com"
    else
        echo -e "${RED}❌ Some tests failed. Please check the issues above.${NC}"
        echo ""
        echo "🔧 Common fixes:"
        echo "   • Wait for DNS propagation (up to 60 minutes)"
        echo "   • Check nginx configuration: nginx -t"
        echo "   • Restart nginx: systemctl restart nginx"
        echo "   • Verify DNS records in your registrar"
    fi
}

# Main execution
main() {
    echo "Starting comprehensive redirect testing..."
    echo "This will test DNS resolution, HTTP redirects, and functionality."
    echo ""
    
    # Run all test suites
    test_dns
    test_dns_propagation
    test_http_redirects
    test_https_redirects
    test_app_functionality
    check_server_logs
    
    # Show final summary
    show_summary
}

# Check if required tools are available
check_requirements() {
    local missing_tools=()
    
    for tool in curl nslookup; do
        if ! command -v $tool >/dev/null 2>&1; then
            missing_tools+=($tool)
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing required tools: ${missing_tools[*]}${NC}"
        echo "Please install missing tools and try again."
        exit 1
    fi
}

# Run the tests
check_requirements
main
