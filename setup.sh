#!/bin/bash

# Argentquest Development Suite - Enhanced Setup Script
set -euo pipefail

# --- Sudo Enforcement ---
if [[ $EUID -ne 0 ]]; then
   echo "🔒 This script requires root privileges. Re-running with sudo..."
   exec sudo "$0" "$@"
fi

echo "🚀 Starting Argentquest Suite Setup..."

# Detect Docker Compose Command
DOCKER_COMPOSE="docker-compose"
if docker compose version &>/dev/null; then
    DOCKER_COMPOSE="docker compose"
fi
echo "   🐳 Using: $DOCKER_COMPOSE"

# --- STEP 0: ENVIRONMENT DETECTION & CLEANUP ---
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "ℹ️  Linux environment detected"
    # Reclaiming disk space from previous failed attempts
    echo "💾 Reclaiming disk space..."
    docker builder prune -f
    docker system prune -f

    # KDE/XRDP FIX: Ensure the desktop session doesn't black out
    echo "🖥️  Configuring KDE Plasma session for RDP..."
    echo "dbus-launch --exit-with-session startplasma-x11" > ~/.xsession
    chmod +x ~/.xsession
fi

# --- STEP 0.5: PYTHON ENVIRONMENT SETUP (Optimized with uv) ---
echo "🐍 Step 0.5: Setting up Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first."
    exit 1
fi

if command -v uv &> /dev/null; then
    echo "   ⚡ 'uv' detected! Accelerating setup..."
    if [ ! -d ".venv" ]; then
        uv venv .venv
    fi
    source .venv/bin/activate
    uv pip install --quiet requests python-dotenv
    echo "   ✅ Virtual environment and dependencies ready (via uv)"
else
    if [ ! -d ".venv" ]; then
        echo "   Creating virtual environment..."
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    if command -v pip &> /dev/null; then
        echo "   Installing dependencies..."
        pip install --quiet --upgrade pip
        pip install --quiet requests python-dotenv
        echo "   ✅ Dependencies ready"
    fi
fi

# --- STEP 0.6: SYSTEM CHECKS ---
echo "🔍 Step 0.6: Pre-flight System Checks..."

# Check /etc/hosts
PROJECT_DOMAIN="pocmaster.argentquest.com"
if ! grep -q "$PROJECT_DOMAIN" /etc/hosts; then
    echo "   ⚠️  '$PROJECT_DOMAIN' not found in /etc/hosts"
    echo "   🔧 Attempting to add entries automatically (requires sudo)..."
    
    HOSTS_CONTENT="
127.0.0.1    pocmaster.argentquest.com
127.0.0.1    api.pocmaster.argentquest.com
127.0.0.1    api-dev.pocmaster.argentquest.com
127.0.0.1    pgadmin.pocmaster.argentquest.com
127.0.0.1    mongo.pocmaster.argentquest.com
127.0.0.1    redis.pocmaster.argentquest.com
127.0.0.1    minio.pocmaster.argentquest.com
127.0.0.1    portainer.pocmaster.argentquest.com
127.0.0.1    heimdall.pocmaster.argentquest.com
127.0.0.1    code.pocmaster.argentquest.com
127.0.0.1    mcp.pocmaster.argentquest.com
127.0.0.1    n8n.pocmaster.argentquest.com
127.0.0.1    jupyter.pocmaster.argentquest.com
"
    
    if echo "$HOSTS_CONTENT" | sudo tee -a /etc/hosts > /dev/null; then
        echo "   ✅ Successfully updated /etc/hosts"
    else
        echo "   ❌ Failed to update /etc/hosts. Please try running with sudo or update manually."
    fi
else
    echo "   ✅ Hosts file looks good"
fi

# Firewall Warning (UFW)
if command -v ufw &> /dev/null; then
    if sudo ufw status | grep -q "Status: active"; then
        echo "   ℹ️  UFW Firewall is active. Ensure ports 80, 443, 81 are allowed."
    fi
fi

# --- STEP 1: CREATE ENVIRONMENT FILES ---
echo "📝 Step 1: Creating environment files..."
for env_file in .env .env.dev .env.prod; do
    if [ ! -f "$env_file" ]; then
        cp .env.template "$env_file" 2>/dev/null || touch "$env_file"
        echo "   ✅ Created $env_file"
    else
        echo "   ⚠️  $env_file already exists, skipping"
    fi
done

# --- STEP 2: DOCKER & CONFIG HEALTH CHECK ---
echo "🔍 Step 2: System & Config Checks..."
if ! docker info > /dev/null 2>&1; then
    echo "   ❌ Docker is not running. Attempting to start..."
    sudo systemctl restart docker || (echo "❌ Failed to start Docker"; exit 1)
    sleep 5
fi

# Validate Config
if [ -f ".env" ]; then
    if grep -q "your-openrouter-api-key-here" .env; then
        echo "   ⚠️  WARNING: OPENROUTER_API_KEY is not set in .env!"
        echo "      OpenRouter is required for AI features. Please update it later."
    fi
fi
echo "   ✅ System and Config look ready"

# --- STEP 3: START CONTAINERS ---
echo "🚀 Step 3: Starting all 22 containers..."
$DOCKER_COMPOSE up -d --build --pull always

# --- STEP 4: SMART INITIALIZATION ---
echo "⏳ Step 4: Waiting for services to initialize..."

wait_for_service() {
    local url=$1
    local name=$2
    local timeout=60
    local count=0
    echo -n "   Waiting for $name..."
    until $(curl --output /dev/null --silent --head --fail "$url"); do
        if [ $count -gt $timeout ]; then
            echo " ❌ Timeout"
            return 1
        fi
        echo -n "."
        sleep 2
        count=$((count + 2))
    done
    echo " ✅ Ready!"
}

# Wait for Nginx Proxy Manager Admin UI (local port 81)
wait_for_service "http://localhost:81" "Nginx Proxy Manager" || echo "   ⚠️  NPM taking longer than expected..."

# --- STEP 5: PROXY & DATABASE VALIDATION (From Original) ---
echo "🌐 Step 5: Setting up proxy and validating..."
if [ -f "scripts/npm-simple-setup.py" ]; then
    python3 scripts/npm-simple-setup.py || echo "   ⚠️  Proxy setup failed"
fi

if [ -f "health-check.py" ]; then
    python3 health-check.py || echo "   ⚠️  Health check flagged some issues"
fi

if [ -f "validate-database-setup.sh" ]; then
    chmod +x validate-database-setup.sh
    ./validate-database-setup.sh || echo "   ⚠️  Database validation failed"
fi

# --- STEP 6: FINAL STATUS ---
echo ""
echo "🎉 Setup Complete!"
echo "--------------------------------------------------"
echo "📍 Access Points:"
echo "   🏠 Main Dashboard:    http://pocmaster.argentquest.com"
echo "   🔧 Development API:   http://api-dev.pocmaster.argentquest.com"
echo "   🏭 Production API:    http://api.pocmaster.argentquest.com"
echo "   🗄️  Database Admin:   http://pgadmin.pocmaster.argentquest.com"
echo "   🐳 Container Mgmt:    https://localhost:9443 (Portainer)"
echo "--------------------------------------------------"
echo "🔐 Credentials:        See .env file or reset_all.sh output"
echo "--------------------------------------------------"
echo "🖥️  RDP Tip: If you see a black screen, log out of the physical console."
echo "💾 Disk Space Remaining: $(df -h / | awk 'NR==2 {print $4}')"
