#!/bin/bash
# NPM Proxy Host Auto-Setup Script
# Automatically creates all proxy hosts via NPM API

set -e

echo "Starting NPM Auto-Setup..."

# Wait for NPM to be ready
echo "Waiting for NPM..."
for i in {1..30}; do
    if curl -f http://localhost:81 >/dev/null 2>&1; then
        echo "NPM is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "NPM not ready after 150 seconds"
        exit 1
    fi
    sleep 5
done

# Login and get token
echo "Getting NPM token..."
TOKEN=$(curl -s -X POST http://localhost:81/api/tokens \
    -H "Content-Type: application/json" \
    -d '{"identity":"admin@example.com","secret":"changeme"}' | \
    grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "Failed to get NPM token"
    exit 1
fi

echo "Token obtained, creating proxy hosts..."

# Function to create proxy host
create_host() {
    local domain=$1
    local target=$2
    local port=$3
    
    echo "Creating: $domain -> $target:$port"
    
    curl -s -X POST http://localhost:81/api/nginx/proxy-hosts \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "domain_names":["'$domain'"],
            "forward_host":"'$target'",
            "forward_port":'$port',
            "access_list_id":0,
            "certificate_id":0,
            "ssl_forced":false,
            "caching_enabled":false,
            "block_exploits":true,
            "allow_websocket_upgrade":true,
            "http2_support":true,
            "forward_scheme":"http",
            "enabled":true
        }' >/dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "  ✓ $domain configured"
    else
        echo "  ✗ $domain failed"
    fi
    
    sleep 1
}

# Create all proxy hosts
create_host "api.pocmaster.argentquest.com" "aq-devsuite-app-prod" 8000
create_host "api-dev.pocmaster.argentquest.com" "aq-devsuite-app-dev" 8000
create_host "jupyter.pocmaster.argentquest.com" "aq-devsuite-jupyter" 8888
create_host "mcp.pocmaster.argentquest.com" "aq-devsuite-mcp-inspector" 5173

echo "NPM Auto-Setup Complete!"
echo "Test with: curl -I http://api.pocmaster.argentquest.com"