#!/bin/bash

# V2 POC Docker Stack Validation Script
# This script validates that all services are running correctly

echo "========================================="
echo "   V2 POC Docker Stack Validation"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
mkdir -p logs

# Generate timestamp for log file
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/validation_${TIMESTAMP}.log"

echo "📝 Capturing current logs to ${LOG_FILE}..."
docker-compose logs > "${LOG_FILE}" 2>&1
echo ""

echo "🔍 Checking Container Status..."
echo "----------------------------------------"
docker-compose ps
echo ""

echo "💡 Service Health Checks..."
echo "----------------------------------------"

# Function to check service health
check_service() {
    local service=$1
    local container=$2
    local health=$(docker inspect $container --format='{{.State.Health.Status}}' 2>/dev/null)
    
    if [ "$health" = "healthy" ]; then
        echo -e "${GREEN}✓${NC} $service: Healthy"
        return 0
    elif [ "$health" = "starting" ]; then
        echo -e "${YELLOW}⏳${NC} $service: Starting..."
        return 1
    elif [ "$health" = "unhealthy" ]; then
        echo -e "${RED}✗${NC} $service: Unhealthy"
        return 1
    else
        # No health check defined, check if running
        local running=$(docker inspect $container --format='{{.State.Running}}' 2>/dev/null)
        if [ "$running" = "true" ]; then
            echo -e "${GREEN}✓${NC} $service: Running (no health check)"
            return 0
        else
            echo -e "${RED}✗${NC} $service: Not running"
            return 1
        fi
    fi
}

# Check each service
check_service "PostgreSQL" "v2-poc-postgres"
check_service "Redis" "v2-poc-redis"
check_service "MinIO" "v2-poc-minio"
check_service "FastAPI App" "v2-poc-app"
check_service "Nginx Proxy" "v2-poc-npm"
check_service "pgAdmin" "v2-poc-pgadmin"
check_service "Redis Commander" "v2-poc-redis-commander"
check_service "Dashboard" "v2-poc-dashboard"
echo ""

echo "🌐 Testing Service Endpoints..."
echo "----------------------------------------"

# Function to test HTTP endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    if command -v curl &> /dev/null; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
        if [ "$response" = "$expected_code" ]; then
            echo -e "${GREEN}✓${NC} $name: Accessible ($url)"
            return 0
        else
            echo -e "${RED}✗${NC} $name: Not accessible (HTTP $response)"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠${NC} curl not found, skipping $name"
        return 1
    fi
}

# Test main endpoints
test_endpoint "FastAPI App" "http://localhost:8000/health"
test_endpoint "FastAPI Docs" "http://localhost:8000/docs"
test_endpoint "MinIO Console" "http://localhost:9001"
test_endpoint "pgAdmin" "http://localhost:5050"
test_endpoint "Redis Commander" "http://localhost:8081"
test_endpoint "Dashboard" "http://localhost:8082"
test_endpoint "Nginx Proxy Manager" "http://localhost:81"
echo ""

echo "🔧 Testing Service Connectivity..."
echo "----------------------------------------"

# Test PostgreSQL connection
if command -v psql &> /dev/null; then
    if PGPASSWORD=pocpass psql -h localhost -U pocuser -d poc_db -c "SELECT 1" &>/dev/null; then
        echo -e "${GREEN}✓${NC} PostgreSQL: Connection successful"
    else
        echo -e "${RED}✗${NC} PostgreSQL: Connection failed"
    fi
else
    # Try using docker exec instead
    if docker exec v2-poc-postgres psql -U pocuser -d poc_db -c "SELECT 1" &>/dev/null; then
        echo -e "${GREEN}✓${NC} PostgreSQL: Connection successful (via docker)"
    else
        echo -e "${RED}✗${NC} PostgreSQL: Connection failed"
    fi
fi

# Test Redis connection
if command -v redis-cli &> /dev/null; then
    if redis-cli -h localhost ping &>/dev/null; then
        echo -e "${GREEN}✓${NC} Redis: Connection successful"
    else
        echo -e "${RED}✗${NC} Redis: Connection failed"
    fi
else
    # Try using docker exec instead
    if docker exec v2-poc-redis redis-cli ping &>/dev/null; then
        echo -e "${GREEN}✓${NC} Redis: Connection successful (via docker)"
    else
        echo -e "${RED}✗${NC} Redis: Connection failed"
    fi
fi
echo ""

echo "📊 Log Analysis..."
echo "----------------------------------------"

# Count log levels
ERROR_COUNT=$(grep -c "ERROR" "${LOG_FILE}" 2>/dev/null || echo "0")
WARNING_COUNT=$(grep -c "WARNING" "${LOG_FILE}" 2>/dev/null || echo "0")
INFO_COUNT=$(grep -c "INFO" "${LOG_FILE}" 2>/dev/null || echo "0")

echo "Errors found: $ERROR_COUNT"
echo "Warnings found: $WARNING_COUNT"
echo "Info messages: $INFO_COUNT"

# Check for specific startup messages
echo ""
echo "Startup Status:"
if grep -q "Application startup complete" "${LOG_FILE}" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} FastAPI: Application startup complete"
else
    echo -e "${YELLOW}⚠${NC} FastAPI: Startup message not found"
fi

if grep -q "database system is ready to accept connections" "${LOG_FILE}" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} PostgreSQL: Ready to accept connections"
else
    echo -e "${YELLOW}⚠${NC} PostgreSQL: Ready message not found"
fi

if grep -q "Ready to accept connections" "${LOG_FILE}" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Redis: Ready to accept connections"
else
    echo -e "${YELLOW}⚠${NC} Redis: Ready message not found"
fi
echo ""

echo "🔍 Recent Errors (if any)..."
echo "----------------------------------------"
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "Last 5 errors from logs:"
    grep "ERROR" "${LOG_FILE}" | tail -5
else
    echo -e "${GREEN}No errors found in logs${NC}"
fi
echo ""

echo "📝 Full Health Check via API..."
echo "----------------------------------------"
if command -v curl &> /dev/null; then
    health_response=$(curl -s http://localhost:8000/health 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "Health check response:"
        if command -v jq &> /dev/null; then
            echo "$health_response" | jq '.'
        else
            echo "$health_response"
        fi
    else
        echo -e "${RED}Failed to get health check response${NC}"
    fi
else
    echo -e "${YELLOW}curl not found, skipping API health check${NC}"
fi
echo ""

echo "========================================="
echo "   Validation Complete"
echo "========================================="
echo ""
echo "📄 Detailed logs saved to: ${LOG_FILE}"
echo ""
echo "To view logs in real-time, run:"
echo "  docker-compose logs -f"
echo ""
echo "To check specific service logs:"
echo "  docker-compose logs app"
echo "  docker-compose logs postgres"
echo "  docker-compose logs redis"
echo ""