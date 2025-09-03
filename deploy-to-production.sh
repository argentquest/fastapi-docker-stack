#!/bin/bash

# Production Deployment Script for pocmaster.argentquest.com
# This script deploys the V2 POC to production server

set -e  # Exit on error

echo "================================================"
echo "   PRODUCTION DEPLOYMENT TO POCMASTER"
echo "   pocmaster.argentquest.com"
echo "================================================"
echo ""

# Configuration
DEPLOY_DIR="/opt/fastapi-docker-stack"
GITHUB_REPO="https://github.com/argentquest/fastapi-docker-stack.git"
BRANCH="main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if running with appropriate permissions
if [[ $EUID -ne 0 ]]; then
   print_warning "This script should be run with sudo for production deployment"
   echo "Example: sudo ./deploy-to-production.sh"
   echo ""
fi

# Step 1: Check Docker installation
print_status "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    echo "Please install Docker first:"
    echo "curl -fsSL https://get.docker.com | sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed!"
    echo "Please install Docker Compose first"
    exit 1
fi
print_success "Docker and Docker Compose are installed"

# Step 2: Navigate to deployment directory
print_status "Setting up deployment directory..."
if [ ! -d "$DEPLOY_DIR" ]; then
    print_status "Creating deployment directory..."
    mkdir -p "$DEPLOY_DIR"
fi
cd "$DEPLOY_DIR"
print_success "Working directory: $DEPLOY_DIR"

# Step 3: Clone or update repository
if [ -d ".git" ]; then
    print_status "Updating existing repository..."
    git fetch origin
    git pull origin $BRANCH
    print_success "Repository updated to latest version"
else
    print_status "Cloning repository..."
    git clone $GITHUB_REPO .
    git checkout $BRANCH
    print_success "Repository cloned successfully"
fi

# Show current commit
CURRENT_COMMIT=$(git rev-parse --short HEAD)
print_status "Current commit: $CURRENT_COMMIT"

# Step 4: Check for .env.prod file
print_status "Checking environment configuration..."
if [ ! -f ".env.prod" ]; then
    print_warning ".env.prod not found!"
    
    if [ -f ".env.template" ]; then
        print_status "Creating .env.prod from template..."
        cp .env.template .env.prod
        print_warning "Please edit .env.prod with your production values:"
        echo ""
        echo "Required configurations:"
        echo "  - OPENROUTER_API_KEY"
        echo "  - OPENROUTER_SITE_URL=https://pocmaster.argentquest.com"
        echo "  - OPENROUTER_APP_NAME=V2-POC-Production"
        echo "  - GOOGLE_API_KEY (if using Google AI)"
        echo ""
        echo "Edit the file with: nano .env.prod"
        echo "Then run this script again"
        exit 1
    else
        print_error ".env.template not found!"
        exit 1
    fi
fi
print_success ".env.prod found"

# Step 5: Stop existing containers
print_status "Stopping existing containers..."
if docker-compose -f docker-compose.prod.yml ps --quiet | grep -q .; then
    docker-compose -f docker-compose.prod.yml down --remove-orphans
    print_success "Existing containers stopped"
else
    print_status "No existing containers to stop"
fi

# Step 6: Pull latest images
print_status "Pulling latest Docker images..."
docker-compose -f docker-compose.prod.yml pull
print_success "Images updated"

# Step 7: Build custom images
print_status "Building application images..."
docker-compose -f docker-compose.prod.yml build --no-cache
print_success "Application images built"

# Step 8: Start production services
print_status "Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
print_status "Waiting for services to initialize..."
sleep 15

# Step 9: Check service health
print_status "Checking service health..."
echo ""

# Function to check container health
check_health() {
    local container=$1
    local display_name=$2
    
    if docker ps --format "{{.Names}}" | grep -q "$container"; then
        local status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-health-check")
        
        case $status in
            healthy)
                print_success "$display_name is healthy"
                ;;
            unhealthy)
                print_error "$display_name is unhealthy"
                ;;
            starting)
                print_warning "$display_name is starting..."
                ;;
            no-health-check)
                print_status "$display_name is running (no health check)"
                ;;
            *)
                print_error "$display_name status unknown: $status"
                ;;
        esac
    else
        print_error "$display_name is not running"
    fi
}

# Check each service
check_health "v2-poc-postgres" "PostgreSQL"
check_health "v2-poc-redis" "Redis"
check_health "v2-poc-minio" "MinIO"
check_health "v2-poc-app" "FastAPI Application"
check_health "v2-poc-nginx" "Nginx Proxy"

# Step 10: Display service URLs
echo ""
echo "================================================"
echo "   DEPLOYMENT COMPLETE"
echo "================================================"
echo ""
print_success "Services are running at:"
echo ""
echo "  🌐 Main Application:"
echo "     https://pocmaster.argentquest.com"
echo ""
echo "  📚 API Documentation:"
echo "     https://pocmaster.argentquest.com/docs"
echo ""
echo "  🏠 Frontend Claude:"
echo "     https://pocmaster.argentquest.com/claude/"
echo ""
echo "  ❤️ Health Check:"
echo "     https://pocmaster.argentquest.com/health"
echo ""
echo "================================================"
echo ""

# Step 11: Show logs command
print_status "To view logs, use:"
echo "  docker-compose -f docker-compose.prod.yml logs -f app"
echo ""
print_status "To check all containers:"
echo "  docker-compose -f docker-compose.prod.yml ps"
echo ""

# Step 12: Quick health check via curl
print_status "Testing health endpoint..."
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "Health check passed (HTTP $HTTP_CODE)"
    elif [ "$HTTP_CODE" = "000" ]; then
        print_warning "Could not connect to health endpoint"
    else
        print_warning "Health check returned HTTP $HTTP_CODE"
    fi
else
    print_warning "curl not installed, skipping health check"
fi

echo ""
print_success "Deployment completed successfully!"
echo ""

# Optional: Show recent logs
read -p "Would you like to see recent application logs? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose.prod.yml logs --tail=50 app
fi