#!/bin/bash
#
# SmartAmazon Health Check Script
# Monitors all services and sends alerts if any are unhealthy
#
# Usage: ./health-check.sh [--send-alerts]
#

set -euo pipefail

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

SEND_ALERTS=false
WEBHOOK_URL="${WEBHOOK_URL:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --send-alerts)
            SEND_ALERTS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_failure() {
    echo -e "${RED}✗${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

send_alert() {
    local service=$1
    local message=$2

    if [[ "$SEND_ALERTS" == true && -n "$WEBHOOK_URL" ]]; then
        curl -X POST "$WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d "{\"text\": \"🚨 ALERT: $service - $message\"}" \
            > /dev/null 2>&1 || true
    fi
}

check_api_health() {
    echo -n "Checking API health... "

    if response=$(curl -sf "${API_URL}/health" -m 5); then
        if echo "$response" | grep -q '"status":"healthy"'; then
            log_success "API is healthy"
            return 0
        else
            log_failure "API returned unhealthy status"
            send_alert "API" "Unhealthy status"
            return 1
        fi
    else
        log_failure "API is unreachable"
        send_alert "API" "Service unreachable"
        return 1
    fi
}

check_frontend() {
    echo -n "Checking Frontend... "

    if curl -sf "$FRONTEND_URL" -m 5 > /dev/null; then
        log_success "Frontend is accessible"
        return 0
    else
        log_failure "Frontend is unreachable"
        send_alert "Frontend" "Service unreachable"
        return 1
    fi
}

check_postgres() {
    echo -n "Checking PostgreSQL... "

    if command -v pg_isready &> /dev/null; then
        if pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -q; then
            log_success "PostgreSQL is accepting connections"
            return 0
        else
            log_failure "PostgreSQL is not accepting connections"
            send_alert "PostgreSQL" "Not accepting connections"
            return 1
        fi
    else
        log_warning "pg_isready not found, skipping check"
        return 0
    fi
}

check_redis() {
    echo -n "Checking Redis... "

    if command -v redis-cli &> /dev/null; then
        if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping | grep -q "PONG"; then
            log_success "Redis is responding"
            return 0
        else
            log_failure "Redis is not responding"
            send_alert "Redis" "Not responding"
            return 1
        fi
    else
        log_warning "redis-cli not found, skipping check"
        return 0
    fi
}

check_disk_space() {
    echo -n "Checking disk space... "

    USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

    if [[ $USAGE -lt 80 ]]; then
        log_success "Disk usage: ${USAGE}%"
        return 0
    elif [[ $USAGE -lt 90 ]]; then
        log_warning "Disk usage: ${USAGE}% (Warning threshold)"
        return 0
    else
        log_failure "Disk usage: ${USAGE}% (Critical threshold)"
        send_alert "Disk Space" "Critical: ${USAGE}% used"
        return 1
    fi
}

check_memory() {
    echo -n "Checking memory... "

    if command -v free &> /dev/null; then
        USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')

        if [[ $USAGE -lt 85 ]]; then
            log_success "Memory usage: ${USAGE}%"
            return 0
        elif [[ $USAGE -lt 95 ]]; then
            log_warning "Memory usage: ${USAGE}% (Warning threshold)"
            return 0
        else
            log_failure "Memory usage: ${USAGE}% (Critical threshold)"
            send_alert "Memory" "Critical: ${USAGE}% used"
            return 1
        fi
    else
        log_warning "free command not found, skipping check"
        return 0
    fi
}

check_api_performance() {
    echo -n "Checking API response time... "

    START_TIME=$(date +%s%3N)
    if curl -sf "${API_URL}/health" -m 5 > /dev/null; then
        END_TIME=$(date +%s%3N)
        RESPONSE_TIME=$((END_TIME - START_TIME))

        if [[ $RESPONSE_TIME -lt 500 ]]; then
            log_success "API response time: ${RESPONSE_TIME}ms"
            return 0
        elif [[ $RESPONSE_TIME -lt 2000 ]]; then
            log_warning "API response time: ${RESPONSE_TIME}ms (Slow)"
            return 0
        else
            log_failure "API response time: ${RESPONSE_TIME}ms (Very slow)"
            send_alert "API Performance" "Slow response: ${RESPONSE_TIME}ms"
            return 1
        fi
    else
        log_failure "API check failed"
        return 1
    fi
}

# Main execution
main() {
    echo "========================================="
    echo "SmartAmazon Health Check"
    echo "========================================="
    echo "Timestamp: $(date)"
    echo ""

    FAILED=0

    check_api_health || ((FAILED++))
    check_frontend || ((FAILED++))
    check_postgres || ((FAILED++))
    check_redis || ((FAILED++))
    check_disk_space || ((FAILED++))
    check_memory || ((FAILED++))
    check_api_performance || ((FAILED++))

    echo ""
    echo "========================================="

    if [[ $FAILED -eq 0 ]]; then
        echo -e "${GREEN}All checks passed!${NC}"
        exit 0
    else
        echo -e "${RED}$FAILED check(s) failed!${NC}"
        exit 1
    fi
}

main
