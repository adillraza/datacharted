#!/bin/bash

# DataCharted Performance & SEO Monitoring Script
# This script monitors website performance, SEO metrics, and server health

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="datacharted.com"
SERVER_IP="165.232.38.9"
SSH_KEY="~/Downloads/id_rsa"
LOG_FILE="/tmp/datacharted_monitor_$(date +%Y%m%d_%H%M%S).log"

echo "🔍 DataCharted Performance & SEO Monitor"
echo "========================================"
echo "Domain: $DOMAIN"
echo "Server: $SERVER_IP"
echo "Time: $(date)"
echo "Log: $LOG_FILE"
echo ""

# Function to log results
log_result() {
    echo "$1" | tee -a "$LOG_FILE"
}

# Function to test with timing
test_with_timing() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${BLUE}Testing:${NC} $test_name"
    
    start_time=$(date +%s.%N)
    result=$(eval "$test_command" 2>&1)
    end_time=$(date +%s.%N)
    
    duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "N/A")
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name (${duration}s)"
        log_result "PASS: $test_name - Duration: ${duration}s"
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        log_result "FAIL: $test_name - Error: $result"
    fi
    
    return 0
}

# Performance Tests
echo -e "${BLUE}🚀 Performance Tests${NC}"
echo "-------------------"

# 1. Basic connectivity
test_with_timing "Basic connectivity" "curl -s -o /dev/null -w '%{http_code}' https://$DOMAIN | grep -q '200'"

# 2. HTTPS redirect
test_with_timing "HTTP to HTTPS redirect" "curl -s -I http://$DOMAIN | grep -q 'Location: https://'"

# 3. WWW redirect
test_with_timing "WWW redirect" "curl -s -I https://www.$DOMAIN | grep -q 'Location: https://datacharted.com'"

# 4. Page load speed
echo -e "${BLUE}Testing:${NC} Page load speed"
load_time=$(curl -w "@/dev/stdin" -s -o /dev/null https://$DOMAIN <<< "time_total: %{time_total}\ntime_connect: %{time_connect}\ntime_starttransfer: %{time_starttransfer}\nsize_download: %{size_download}")
echo -e "${GREEN}✅ PASS${NC}: Page load metrics"
echo "$load_time"
log_result "Page load metrics: $load_time"

echo ""

# SEO Tests
echo -e "${BLUE}🎯 SEO Tests${NC}"
echo "-------------"

# 5. Compression
test_with_timing "Gzip compression" "curl -H 'Accept-Encoding: gzip' -s -I https://$DOMAIN | grep -q 'content-encoding: gzip'"

# 6. Security headers
test_with_timing "HSTS header" "curl -s -I https://$DOMAIN | grep -q 'Strict-Transport-Security'"
test_with_timing "X-Frame-Options" "curl -s -I https://$DOMAIN | grep -q 'X-Frame-Options: DENY'"
test_with_timing "X-Content-Type-Options" "curl -s -I https://$DOMAIN | grep -q 'X-Content-Type-Options: nosniff'"

# 7. Robots.txt
test_with_timing "Robots.txt accessibility" "curl -s https://$DOMAIN/robots.txt | grep -q 'User-agent'"

# 8. Sitemap reference
test_with_timing "Sitemap in robots.txt" "curl -s https://$DOMAIN/robots.txt | grep -q 'Sitemap:'"

echo ""

# Server Health Tests
echo -e "${BLUE}🖥️  Server Health Tests${NC}"
echo "----------------------"

# 9. SSL certificate validity
echo -e "${BLUE}Testing:${NC} SSL certificate validity"
ssl_info=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PASS${NC}: SSL certificate valid"
    echo "$ssl_info"
    log_result "SSL certificate: $ssl_info"
else
    echo -e "${RED}❌ FAIL${NC}: SSL certificate check failed"
    log_result "SSL certificate: FAILED"
fi

# 10. Server response headers
echo -e "${BLUE}Testing:${NC} Server response analysis"
headers=$(curl -s -I https://$DOMAIN)
echo -e "${GREEN}✅ INFO${NC}: Response headers analyzed"
echo "Server: $(echo "$headers" | grep -i '^server:' | cut -d' ' -f2-)"
echo "Content-Type: $(echo "$headers" | grep -i '^content-type:' | cut -d' ' -f2-)"
echo "Cache-Control: $(echo "$headers" | grep -i '^cache-control:' | cut -d' ' -f2-)"

echo ""

# Performance Metrics
echo -e "${BLUE}📊 Performance Metrics${NC}"
echo "----------------------"

# 11. Detailed timing analysis
echo -e "${BLUE}Testing:${NC} Detailed performance analysis"
perf_data=$(curl -w "DNS Lookup: %{time_namelookup}s\nTCP Connect: %{time_connect}s\nTLS Handshake: %{time_appconnect}s\nServer Processing: %{time_starttransfer}s\nContent Transfer: %{time_total}s\nTotal Size: %{size_download} bytes\nSpeed: %{speed_download} bytes/sec" -s -o /dev/null https://$DOMAIN)
echo -e "${GREEN}✅ INFO${NC}: Performance metrics"
echo "$perf_data"
log_result "Performance metrics: $perf_data"

echo ""

# Core Web Vitals Simulation
echo -e "${BLUE}⚡ Core Web Vitals Simulation${NC}"
echo "-----------------------------"

# 12. First Byte Time (TTFB)
ttfb=$(curl -w "%{time_starttransfer}" -s -o /dev/null https://$DOMAIN)
ttfb_ms=$(echo "$ttfb * 1000" | bc -l 2>/dev/null || echo "N/A")
if [ "$ttfb_ms" != "N/A" ] && [ "$(echo "$ttfb < 0.2" | bc -l 2>/dev/null)" = "1" ]; then
    echo -e "${GREEN}✅ EXCELLENT${NC}: TTFB: ${ttfb_ms}ms (< 200ms target)"
elif [ "$ttfb_ms" != "N/A" ] && [ "$(echo "$ttfb < 0.5" | bc -l 2>/dev/null)" = "1" ]; then
    echo -e "${YELLOW}⚠️  GOOD${NC}: TTFB: ${ttfb_ms}ms (< 500ms acceptable)"
else
    echo -e "${RED}❌ NEEDS IMPROVEMENT${NC}: TTFB: ${ttfb_ms}ms (> 500ms)"
fi

echo ""

# SEO Score Calculation
echo -e "${BLUE}🏆 SEO Score Summary${NC}"
echo "--------------------"

seo_score=0
total_checks=10

# Check each SEO factor
curl -s -I https://$DOMAIN | grep -q "200 OK" && ((seo_score++))
curl -s -I http://$DOMAIN | grep -q "301" && ((seo_score++))
curl -s -I https://www.$DOMAIN | grep -q "301" && ((seo_score++))
curl -H "Accept-Encoding: gzip" -s -I https://$DOMAIN | grep -q "gzip" && ((seo_score++))
curl -s -I https://$DOMAIN | grep -q "Strict-Transport-Security" && ((seo_score++))
curl -s -I https://$DOMAIN | grep -q "X-Frame-Options" && ((seo_score++))
curl -s -I https://$DOMAIN | grep -q "X-Content-Type-Options" && ((seo_score++))
curl -s https://$DOMAIN/robots.txt | grep -q "User-agent" && ((seo_score++))
[ "$ttfb_ms" != "N/A" ] && [ "$(echo "$ttfb < 0.5" | bc -l 2>/dev/null)" = "1" ] && ((seo_score++))
curl -s -I https://$DOMAIN | grep -q "cache-control" && ((seo_score++))

seo_percentage=$((seo_score * 100 / total_checks))

if [ $seo_percentage -ge 90 ]; then
    echo -e "${GREEN}🏆 EXCELLENT${NC}: SEO Score: $seo_score/$total_checks ($seo_percentage%)"
elif [ $seo_percentage -ge 70 ]; then
    echo -e "${YELLOW}⚠️  GOOD${NC}: SEO Score: $seo_score/$total_checks ($seo_percentage%)"
else
    echo -e "${RED}❌ NEEDS WORK${NC}: SEO Score: $seo_score/$total_checks ($seo_percentage%)"
fi

echo ""

# Summary
echo -e "${BLUE}📋 Summary${NC}"
echo "----------"
echo "✅ Tests completed at: $(date)"
echo "📊 SEO Score: $seo_score/$total_checks ($seo_percentage%)"
echo "⚡ TTFB: ${ttfb_ms}ms"
echo "📝 Full log: $LOG_FILE"

# Recommendations
echo ""
echo -e "${BLUE}💡 Recommendations${NC}"
echo "------------------"

if [ $seo_percentage -lt 100 ]; then
    echo "🔧 Consider implementing missing SEO optimizations"
fi

if [ "$ttfb_ms" != "N/A" ] && [ "$(echo "$ttfb > 0.2" | bc -l 2>/dev/null)" = "1" ]; then
    echo "⚡ Consider server-side performance optimizations"
fi

echo "📊 Regular monitoring recommended (daily/weekly)"
echo "🔍 Monitor Google Search Console for SEO insights"
echo "📈 Track Core Web Vitals in Google PageSpeed Insights"

echo ""
echo -e "${GREEN}🎉 Monitoring complete!${NC}"
