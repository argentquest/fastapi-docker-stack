#!/bin/bash

# Argentquest Development Suite - All-In-One Reset Script
# This script ensures it is running as root/sudo and performs a deep cleanup.

set -euo pipefail

# --- Sudo Enforcement ---
if [[ $EUID -ne 0 ]]; then
   echo "🔒 This script requires root privileges. Re-running with sudo..."
   exec sudo "$0" "$@"
fi

echo "🧨 Starting Full Environment Reset (with Root Privileges)..."

# --- 1. Handle Docker Snap AppArmor issues (Linux only) ---
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v snap &> /dev/null && snap list docker &> /dev/null; then
        echo "🔄 Restarting Docker Snap to clear AppArmor blocks..."
        snap restart docker
    fi
fi

# --- 2. Stop and remove all containers ---
echo "🗑️  Removing all Docker containers..."
# Only attempt Docker commands if the socket exists and the daemon is reachable
if [ -S /var/run/docker.sock ] && docker info >/dev/null 2>&1; then
    CONTAINERS=$(docker ps -aq 2>/dev/null) || CONTAINERS=""
    if [ -n "$CONTAINERS" ]; then
        docker rm -f $CONTAINERS || true
    else
        echo "   No containers found."
    fi
else
    echo "   ⚠️  Docker daemon unreachable or socket missing. Skipping container cleanup."
fi

# --- 3. Deep prune system ---
echo "🧹 Pruning system (images, volumes, networks)..."
if [ -S /var/run/docker.sock ] && docker info >/dev/null 2>&1; then
    docker system prune -a --volumes -f || true
fi

# --- 4. Clear build cache ---
echo "💾 Clearing build cache..."
if [ -S /var/run/docker.sock ] && docker info >/dev/null 2>&1; then
    docker builder prune -f || true
fi

# --- 5. Uninstall Docker ---
echo "🗑️  Uninstalling Docker (Engine & Snap)..."

# APT/Engine version
if command -v apt-get &> /dev/null; then
    echo "   Removing APT Docker packages..."
    apt-get purge -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras || true
    apt-get autoremove -y --purge || true
fi

# Snap version
if command -v snap &> /dev/null && snap list docker &> /dev/null; then
    echo "   Removing Docker Snap..."
    snap remove --purge docker || true
fi

# Clean up system Docker directories
echo "🧹 Cleaning up system Docker directories..."
rm -rf /var/lib/docker
rm -rf /var/lib/containerd
rm -rf /etc/docker
rm -rf /var/run/docker.sock
rm -rf /var/run/containerd
rm -rf ~/.docker

# --- 5.5 Deep Project Cleanup (USER REQUESTED) ---
echo "🧨 Performing Deep Project Cleanup..."
echo "   🗑️  Deleting environment files (.env, .env.dev, .env.prod)..."
rm -f .env .env.dev .env.prod

echo "   🗑️  Wiping persistent data directory (NPM, DB data)..."
rm -rf data/

echo "   🗑️  Wiping Python virtual environment (.venv)..."
rm -rf .venv

echo "   🗑️  Cleaning up build artifacts and logs..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
rm -f setup_log.txt

# --- 6. Reinstall Docker ---
echo "🛠️  Reinstalling Docker using get-docker.sh..."
if [ -f "./get-docker.sh" ]; then
    sh ./get-docker.sh
else
    echo "   ⚠️  get-docker.sh not found, downloading from official source..."
    curl -fsSL https://get.docker.com -o install-docker.sh
    sh install-docker.sh
    rm install-docker.sh
fi

# --- 7. Install Portainer (Standard Port) ---
echo "🐳 Installing Portainer CE with default credentials..."
echo "   User: admin"
echo "   Pass: argentquest123"

# Ensure network exists so NPM can find Portainer later
docker network create aq-devsuite-network 2>/dev/null || true
docker volume create portainer_data || true

# Using bcrypt hash for 'argentquest123'
docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart always \
    --network aq-devsuite-network \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v portainer_data:/data \
    portainer/portainer-ce:latest \
    --admin-password '$2b$10$LhkNv6R.vBf7df0JEqGkheq7zs4hkScHRDxY.Is/7kbYoI1FTiZUK' || echo "⚠️  Failed to start Portainer"

echo "✨ Reset and Reinstallation Complete!"
echo "📍 Portainer is available at: https://localhost:9443"
echo "🔐 Portainer Credentials: admin / argentquest123"
echo "🚀 You can now run ./setup.sh"
