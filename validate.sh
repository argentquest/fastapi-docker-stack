#!/bin/bash

# Argentquest Development Suite - Docker Stack Validation Script
# This script validates that all 20 services are running correctly

echo "========================================="
echo "   Argentquest Development Suite"
echo "   Docker Stack Validation (20 Services)"
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

echo "🔍 Checking Container Status (20 containers)..."
echo "----------------------------------------"
docker-compose ps --filter "name=aq-devsuite-"
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

# Check each service (all 20 containers)
echo "Core Services:"
check_service "NPM (Nginx Proxy Manager)" "aq-devsuite-npm"
check_service "FastAPI Production" "aq-devsuite-app-prod"
check_service "FastAPI Development" "aq-devsuite-app-dev"
echo ""

echo "Databases:"
check_service "PostgreSQL" "aq-devsuite-postgres"
check_service "MongoDB" "aq-devsuite-mongodb"
check_service "Redis" "aq-devsuite-redis"
check_service "MinIO" "aq-devsuite-minio"
echo ""

echo "Database Management:"
check_service "pgAdmin" "aq-devsuite-pgadmin"
check_service "MongoDB Express" "aq-devsuite-mongo-express"
check_service "Redis Commander" "aq-devsuite-redis-commander"
echo ""

echo "Development Tools:"
check_service "VS Code Server" "aq-devsuite-vscode"
check_service "MCP Inspector" "aq-devsuite-mcp-inspector"
check_service "n8n Workflows" "aq-devsuite-n8n"
check_service "Jupyter Lab" "aq-devsuite-jupyter"
echo ""

echo "Infrastructure & Monitoring:"
check_service "Portainer" "aq-devsuite-portainer"
check_service "Heimdall" "aq-devsuite-heimdall"
check_service "System Monitor" "aq-devsuite-system-monitor"
check_service "Monitor API" "aq-devsuite-monitor-api"
check_service "Beszel Hub" "aq-devsuite-beszel"
check_service "Beszel Agent" "aq-devsuite-beszel-agent"
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
echo "API Endpoints:"
test_endpoint "FastAPI Production" "http://localhost:8000/health"
test_endpoint "FastAPI Development" "http://localhost:8001/health"
test_endpoint "API Documentation" "http://localhost:8000/docs"
echo ""

echo "Management UIs:"
test_endpoint "NPM Admin" "http://localhost:81"
test_endpoint "pgAdmin" "http://localhost:5050"
test_endpoint "MinIO Console" "http://localhost:9001"
test_endpoint "Portainer" "https://localhost:9443" "200,302"
echo ""

echo "Development Tools:"
test_endpoint "VS Code Server" "http://localhost:8080"
test_endpoint "MCP Inspector" "http://localhost:5173"
test_endpoint "n8n Workflows" "http://localhost:5678"
test_endpoint "Jupyter Lab" "http://localhost:8888"
echo ""

echo "Monitoring:"
test_endpoint "System Monitor" "http://localhost:80"
test_endpoint "Beszel Hub" "http://localhost:8090"
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
    if docker exec aq-devsuite-postgres psql -U pocuser -d poc_db -c "SELECT 1" &>/dev/null; then
        echo -e "${GREEN}✓${NC} PostgreSQL: Connection successful (via docker)"
    else
        echo -e "${RED}✗${NC} PostgreSQL: Connection failed"
    fi
fi

# Test MongoDB connection
if docker exec aq-devsuite-mongodb mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
    echo -e "${GREEN}✓${NC} MongoDB: Connection successful"
else
    echo -e "${RED}✗${NC} MongoDB: Connection failed"
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
    if docker exec aq-devsuite-redis redis-cli ping &>/dev/null; then
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

if grep -q "MongoDB starting" "${LOG_FILE}" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} MongoDB: Database started"
else
    echo -e "${YELLOW}⚠${NC} MongoDB: Startup message not found"
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

echo "📝 Container Summary..."
echo "----------------------------------------"
TOTAL_CONTAINERS=$(docker ps --filter "name=aq-devsuite-" --format "{{.Names}}" | wc -l)
RUNNING_CONTAINERS=$(docker ps --filter "name=aq-devsuite-" --filter "status=running" --format "{{.Names}}" | wc -l)

echo "Total containers: $TOTAL_CONTAINERS"
echo "Running containers: $RUNNING_CONTAINERS"

if [ "$RUNNING_CONTAINERS" -eq 20 ]; then
    echo -e "${GREEN}✓ All 20 containers are running${NC}"
else
    echo -e "${YELLOW}⚠ Only $RUNNING_CONTAINERS/20 containers running${NC}"
    echo ""
    echo "Not running:"
    docker ps -a --filter "name=aq-devsuite-" --filter "status=exited" --format "table {{.Names}}\t{{.Status}}"
fi
echo ""

echo "========================================="
echo "   Validation Complete"
echo "========================================="
echo ""
echo "📄 Detailed logs saved to: ${LOG_FILE}"
echo ""
echo "Quick Commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Restart all:      docker-compose restart"
echo "  Check specific:   docker-compose logs [service-name]"
echo "  Health check:     python health-check.py"
echo ""
echo "Access Points:"
echo "  Main Dashboard:   http://pocmaster.argentquest.com"
echo "  NPM Admin:        http://pocmaster.argentquest.com:81"
echo "  API Docs:         http://api.pocmaster.argentquest.com/docs"
echo ""