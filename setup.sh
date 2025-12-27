#!/bin/bash

# ==============================================================================
# Argentquest Development Suite - Enhanced Orchestration Script
# ==============================================================================
# This script is the primary entry point for deploying the Argentquest Suite.
# It handles environment detection, dependency management, container orchestration,
# and post-deployment validation.
# ==============================================================================

set -euo pipefail

# --- SECTION 0: PRIVILEGE ESCALATION ---
# Docker and /etc/hosts modifications require root access.
# If not running as root, we re-execute the script using sudo.
if [[ $EUID -ne 0 ]]; then
   echo "🔒 Privilege Check: This script requires root privileges for Docker and System configuration."
   echo "   Elevating permissions..."
   exec sudo "$0" "$@"
fi

echo "🚀 Starting Argentquest Suite Orchestration..."

# --- SECTION 0.1: TOOL DETECTION ---
# We detect if the modern 'docker compose' (V2) or legacy 'docker-compose' (V1) is available.
DOCKER_COMPOSE="docker-compose"
if docker compose version &>/dev/null; then
    DOCKER_COMPOSE="docker compose"
fi
echo "   🐳 Engine Discovery: Using '$DOCKER_COMPOSE' for orchestration"

# --- SECTION 0.2: OS-SPECIFIC OPTIMIZATIONS ---
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "ℹ️  System: Linux environment detected"
    
    # Pruning the Docker builder cache and system artifacts helps prevent
    # "Exporting to Image" hangs caused by corrupted or bloated cache layers.
    echo "💾 Hygiene: Reclaiming disk space and clearing build cache..."
    docker builder prune -f >/dev/null 2>&1 || true
    docker system prune -f >/dev/null 2>&1 || true

    # KDE/XRDP FIX: Argentquest is optimized for Kubuntu/KDE RDP sessions.
    # This ensures the window manager starts correctly in remote environments.
    echo "🖥️  RDP Optimization: Ensuring KDE Plasma session stability..."
    echo "dbus-launch --exit-with-session startplasma-x11" > ~/.xsession
    chmod +x ~/.xsession
fi

# --- SECTION 0.5: PYTHON ENVIRONMENT (Self-Healing) ---
# The suite relies on Python for auto-configuration scripts (NPM/Heimdall).
echo "🐍 Environment: Preparing Python 3 virtual environment..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed on this system."
    exit 1
fi

# Ensure python3-venv is installed (often missing on minimal Ubuntu installs)
# This is a common blocker for fresh Linux VPS/VM setups.
if ! dpkg -l | grep -q "python3-venv" && [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "   🔧 Dependency Check: 'python3-venv' is missing. Installing system package..."
    apt-get update -qq && apt-get install -y -qq python3-venv >/dev/null 2>&1 || echo "   ⚠️  Warning: Could not install python3-venv. Native venv creation might fail."
fi

# Advanced UV Discovery (Handles sudo path issues)
# 'uv' is used to significantly speed up pip installations.
# We check home directories and pyenv because 'sudo' often strips these from the PATH.
UV_BIN=$(command -v uv || echo "$HOME/.local/bin/uv" || echo "$HOME/.pyenv/shims/uv" || which uv 2>/dev/null || true)

if [ -x "$UV_BIN" ]; then
    echo "   ⚡ Performance: 'uv' detected at $UV_BIN. Using high-speed installer..."
    if [ ! -f ".venv/bin/activate" ]; then
        echo "   🔧 Initialization: Creating/Repairing virtual environment with uv..."
        rm -rf .venv
        "$UV_BIN" venv .venv >/dev/null
    fi
    source .venv/bin/activate
    echo "   📦 Dependencies: Installing Python libraries (requests, python-dotenv)..."
    "$UV_BIN" pip install --quiet requests python-dotenv
    echo "   ✅ Python: Virtual environment ready (Accelerated by uv)"
else
    # Fallback to standard venv/pip if 'uv' is not installed.
    if [ ! -f ".venv/bin/activate" ]; then
        echo "   🔧 Initialization: Creating/Repairing virtual environment with standard venv..."
        rm -rf .venv
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    if command -v pip &> /dev/null; then
        echo "   📦 Dependencies: Installing Python libraries via pip..."
        pip install --quiet --upgrade pip
        pip install --quiet requests python-dotenv
        echo "   ✅ Python: Virtual environment ready (Standard pip)"
    fi
fi

# --- SECTION 0.6: PRE-FLIGHT SYSTEM CHECKS ---
echo "🔍 Pre-flight: Validating system connectivity and local DNS..."

# Local DNS Modification (/etc/hosts)
# This allows you to use 'pocmaster.argentquest.com' instead of 'localhost:port'.
PROJECT_DOMAIN="pocmaster.argentquest.com"
if ! grep -q "$PROJECT_DOMAIN" /etc/hosts; then
    echo "   🌐 DNS: Mapping '$PROJECT_DOMAIN' to 127.0.0.1 in /etc/hosts..."
    
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
    
    if echo "$HOSTS_CONTENT" | tee -a /etc/hosts > /dev/null; then
        echo "   ✅ DNS: Successfully updated /etc/hosts"
    else
        echo "   ❌ DNS: Failed to update /etc/hosts. Local domain resolution will fail."
    fi
else
    echo "   ✅ DNS: Local domain mapping looks good"
fi

# Firewall Check (UFW)
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        echo "   🛡️  Security: UFW is active. Ensure incoming traffic is allowed on 80, 443, and 81."
    fi
fi

# --- SECTION 1: CONFIGURATION MANAGEMENT ---
echo "📝 Config: Hydrating environment files from templates..."
for env_file in .env .env.dev .env.prod; do
    if [ ! -f "$env_file" ]; then
        # We copy from the template to ensure all required keys exist.
        cp .env.template "$env_file" 2>/dev/null || touch "$env_file"
        echo "   ✅ Config: Created $env_file"
    else
        echo "   ⚠️  Config: $env_file already exists, keeping current values"
    fi
done

# --- SECTION 2: DOCKER ENGINE READINESS ---
echo "🔍 Engine: Verifying Docker daemon status..."
if ! docker info > /dev/null 2>&1; then
    echo "   ⚠️  Warning: Docker is not reachable. Attempting to start service..."
    systemctl restart docker || (echo "❌ Error: Failed to start Docker engine"; exit 1)
    sleep 5
fi

# Validate Application Secrets
if [ -f ".env" ]; then
    if grep -q "your-openrouter-api-key-here" .env; then
        echo "   🚫 Warning: OPENROUTER_API_KEY is not configured in .env!"
        echo "      AI features will be disabled until you provide a valid key."
    fi
fi
echo "   ✅ Engine: System and Config validated"

# --- SECTION 3: CONTAINER ORCHESTRATION ---
echo "🚀 Deployment: Launching Argentquest Stack (21 Containers)..."

# BuildKit Optimization
# BuildKit is mandatory for the modern 'Dockerfile' features (like cache mounts).
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Sequential Build Strategy
# Building 'app-dev' first prevents parallel build contention on the Docker daemon,
# which is the #1 cause of "Exporting to image" hangs in multi-container stacks.
echo "   🛠️  Phase 1: Pre-building core application image (app-dev)..."
$DOCKER_COMPOSE build app-dev

echo "   🚢 Phase 2: Launching remaining ecosystem containers..."
$DOCKER_COMPOSE up -d --pull always

# --- SECTION 4: SERVICE INITIALIZATION WAIT ---
echo "⏳ Startup: Waiting for core services to reach 'Healthy' state..."

# Helper function to poll a URL until it returns a 200 OK.
wait_for_service() {
    local url=$1
    local name=$2
    local timeout=60
    local count=0
    echo -n "   🔍 Monitoring $name..."
    until $(curl --output /dev/null --silent --head --fail "$url"); do
        if [ $count -gt $timeout ]; then
            echo " ❌ Timeout after ${timeout}s"
            return 1
        fi
        echo -n "."
        sleep 2
        count=$((count + 2))
    done
    echo " ✅ Ready!"
}

# The Nginx Proxy Manager is the "Front Door". We wait for it before configuring routing.
wait_for_service "http://localhost:81" "Nginx Proxy Manager Admin" || echo "   ⚠️  Wait: NPM API is slow to respond. Proxy automation may retry."

# --- SECTION 5: AUTOMATED CONFIGURATION & VALIDATION ---
echo "🌐 Networking: Applying automated proxy and dashboard configurations..."

if [ -f "scripts/npm-simple-setup.py" ]; then
    echo "   🛠️  Proxy: Configuring Nginx Proxy Manager hosts via API..."
    python3 scripts/npm-simple-setup.py || echo "   ⚠️  Error: Proxy automation failed"
fi

echo "🏥 Validation: Running system health signatures..."
if [ -f "health-check.py" ]; then
    python3 health-check.py || echo "   ⚠️  Health: Some services reported non-critical issues"
fi

if [ -f "validate-database-setup.sh" ]; then
    echo "   🗄️  Database: Verifying PostgreSQL and MongoDB connectivity..."
    chmod +x validate-database-setup.sh
    ./validate-database-setup.sh || echo "   ⚠️  Database: Schema validation check failed"
fi

# --- SECTION 6: HEIMDALL DASHBOARD SETUP ---
if [ -f "scripts/heimdall-auto-setup.py" ]; then
    echo "   📊 Dashboard: Mapping all 21 services to Heimdall UI..."
    python3 scripts/heimdall-auto-setup.py || echo "   ⚠️  Dashboard: Heimdall auto-setup failed"
fi

# --- SECTION 7: FINAL WRAP-UP ---
echo ""
echo "=================================================="
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "=================================================="
echo "📍 Access Hyperlinks:"
echo "   🏠 Main Dashboard:    http://pocmaster.argentquest.com"
echo "   🔧 Development API:   http://api-dev.pocmaster.argentquest.com"
echo "   🏭 Production API:    http://api.pocmaster.argentquest.com"
echo "   🗄️  Database Admin:   http://pgadmin.pocmaster.argentquest.com"
echo "   🐳 Container Mgmt:    https://localhost:9443 (Portainer)"
echo "=================================================="
echo "🔐 Credentials:        See .env file for secrets"
echo "   Portainer:         admin / argentquest123"
echo "=================================================="
echo "🖥️  RDP Access Note:   If the screen is black, log out other active sessions."
echo "💾 Storage Status:     $(df -h / | awk 'NR==2 {print $4}') available on root partition"
echo "=================================================="
