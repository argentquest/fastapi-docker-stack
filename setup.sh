#!/bin/bash

# Argentquest Development Suite - Quick Setup Script
# This script provides one-command setup for new contributors

set -e  # Exit on any error

echo "🚀 Setting up Argentquest Development Suite..."
echo "   22-Container Development Environment"
echo ""

# Check if running on Windows (Git Bash/WSL)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "ℹ️  Windows environment detected"
    SETUP_CMD="setup.bat"
elif [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    echo "ℹ️  Unix-like environment detected"
    SETUP_CMD="./setup.sh"
else
    echo "ℹ️  Unknown environment, proceeding with Unix-like setup"
    SETUP_CMD="./setup.sh"
fi

echo ""
echo "📋 Setup Steps:"
echo "   1. Creating environment files"
echo "   2. Starting Docker containers"
echo "   3. Waiting for initialization"
echo "   4. Setting up proxy hosts"
echo "   5. Validating deployment"
echo ""

# Step 1: Create environment files
echo "📝 Step 1: Creating environment files..."
if [ ! -f .env ]; then
    cp .env.template .env
    echo "   ✅ Created .env from template"
else
    echo "   ⚠️  .env already exists, skipping"
fi

if [ ! -f .env.dev ]; then
    cp .env.template .env.dev
    echo "   ✅ Created .env.dev from template"
else
    echo "   ⚠️  .env.dev already exists, skipping"
fi

if [ ! -f .env.prod ]; then
    cp .env.template .env.prod
    echo "   ✅ Created .env.prod from template"
else
    echo "   ⚠️  .env.prod already exists, skipping"
fi

# Check if Docker is running
echo ""
echo "🐳 Step 2: Checking Docker..."
if ! docker --version > /dev/null 2>&1; then
    echo "   ❌ Docker is not installed or not in PATH"
    echo "   Please install Docker Desktop and try again"
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo "   ❌ Docker is not running"
    echo "   Please start Docker Desktop and try again"
    exit 1
fi

echo "   ✅ Docker is running"

# Step 2: Start containers
echo ""
echo "🚀 Step 3: Starting all 22 containers..."
echo "   This may take several minutes on first run..."
docker-compose up -d

# Step 3: Wait for initialization
echo ""
echo "⏳ Step 4: Waiting for container initialization..."
echo "   Waiting 60 seconds for services to start up..."
sleep 60

# Step 4: Set up NPM proxy (if script exists)
echo ""
echo "🌐 Step 5: Setting up proxy hosts..."
if [ -f "scripts/npm-simple-setup.py" ]; then
    python scripts/npm-simple-setup.py || echo "   ⚠️  Proxy setup failed, you may need to run this manually"
else
    echo "   ⚠️  NPM setup script not found, skipping proxy configuration"
fi

# Step 5: Validate deployment
echo ""
echo "✅ Step 6: Validating deployment..."
if [ -f "health-check.py" ]; then
    echo "   Running health check..."
    python health-check.py || echo "   ⚠️  Some services may still be starting"
else
    echo "   ⚠️  Health check script not found"
fi

if [ -f "validate-database-setup.sh" ]; then
    echo "   Validating database setup..."
    chmod +x validate-database-setup.sh
    ./validate-database-setup.sh || echo "   ⚠️  Database validation failed, may need more time"
else
    echo "   ⚠️  Database validation script not found"
fi

# Final status
echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📍 Access Points:"
echo "   🏠 Main Dashboard:    http://pocmaster.argentquest.com"
echo "   🔧 Development API:   http://api-dev.pocmaster.argentquest.com"
echo "   🏭 Production API:    http://api.pocmaster.argentquest.com"
echo "   🗄️  Database Admin:   http://pgadmin.pocmaster.argentquest.com"
echo "   🐳 Container Mgmt:    http://localhost:9443"
echo ""
echo "📚 Next Steps:"
echo "   1. Check http://pocmaster.argentquest.com for service dashboard"
echo "   2. Review CONTRIBUTING.md for development workflow"
echo "   3. Look at 'good first issue' labels in GitHub Issues"
echo "   4. Join our community discussions on GitHub"
echo ""
echo "❓ Need Help?"
echo "   - Check DEBUG_SETUP.md for troubleshooting"
echo "   - Run: docker-compose ps (to check container status)"
echo "   - Run: python health-check.py (to validate services)"
echo "   - Create an issue on GitHub if problems persist"
echo ""
echo "⚠️  Note: This is a development environment with default credentials."
echo "   See SECURITY.md before any production use."