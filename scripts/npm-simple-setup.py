#!/usr/bin/env python3
"""
Universal NPM Auto-Setup Script
Automatically configures NPM proxy hosts.
Works both inside Docker (npm-setup container) and on Host (setup.sh).
"""

import requests
import json
import time
import sys

def get_npm_url():
    """Determine the correct NPM URL (container or host)."""
    urls = [
        "http://aq-devsuite-npm:81",  # Internal Docker Network
        "http://localhost:81"         # Host Machine
    ]

    print("Detecting NPM URL...")
    for url in urls:
        try:
            print(f"Trying {url}...")
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"✓ Found NPM at {url}")
                return url
        except requests.exceptions.RequestException:
            continue

    print("❌ Could not connect to NPM on any known URL")
    return None

def login_npm(base_url):
    """Login to NPM and get token."""
    try:
        response = requests.post(
            f"{base_url}/api/tokens",
            json={
                "identity": "admin@example.com",
                "secret": "changeme"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ NPM login successful")
            return data.get('token')
        else:
            print(f"❌ NPM login failed: {response.status_code} Body: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ NPM login error: {e}")
        return None

def delete_all_hosts(base_url, token):
    """Delete existing proxy hosts to ensure clean state."""
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        response = requests.get(f"{base_url}/api/nginx/proxy-hosts", headers=headers)

        if response.status_code == 200:
            hosts = response.json()
            if not hosts:
                print("No existing hosts to delete.")
                return

            print(f"Found {len(hosts)} existing hosts. Cleaning up...")
            for host in hosts:
                hid = host['id']
                del_resp = requests.delete(f"{base_url}/api/nginx/proxy-hosts/{hid}", headers=headers)
                if del_resp.status_code == 200:
                    print(f"  Deleted host ID {hid}")
                else:
                    print(f"  Failed to delete host ID {hid}")
        else:
            print("Failed to list existing hosts")
    except Exception as e:
        print(f"Error deleting hosts: {e}")

def create_proxy_host(base_url, token, config):
    """Create proxy host in NPM."""
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        domain = config["domain_names"][0]

        # Default Config
        payload = {
            "domain_names": config["domain_names"],
            "forward_host": config["forward_host"],
            "forward_port": config["forward_port"],
            "access_list_id": 0,
            "certificate_id": 0,
            "ssl_forced": False,
            "caching_enabled": False,
            "block_exploits": True,
            "allow_websocket_upgrade": config.get("websocket", True),
            "http2_support": True,
            "forward_scheme": config.get("forward_scheme", "http"),
            "enabled": True,
            "advanced_config": config.get("advanced_config", "")
        }
        
        response = requests.post(
            f"{base_url}/api/nginx/proxy-hosts",
            json=payload,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 201:
            print(f"✓ Created: {domain} -> {config['forward_host']}:{config['forward_port']}")
            return True
        else:
            print(f"❌ Failed {domain}: {response.status_code} {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating {config.get('domain_names', 'unknown')}: {e}")
        return False

def main():
    print("="*50)
    print("Starting Universal NPM Auto-Setup")
    print("="*50)
    
    # 1. Wait/Detect NPM
    base_url = None
    for i in range(30):
        base_url = get_npm_url()
        if base_url:
            break
        print(f"Waiting for NPM... ({i+1}/30)")
        time.sleep(5)

    if not base_url:
        print("❌ Timeout waiting for NPM")
        sys.exit(1)
    
    # 2. Login
    token = login_npm(base_url)
    if not token:
        sys.exit(1)
    
    # 3. Cleanup
    delete_all_hosts(base_url, token)

    # 4. Define Services
    # Using service names (resolvable in Docker network)
    # Note: If running on HOST, 'aq-devsuite-app-prod' might not resolve if checking strictly,
    # but NPM is inside the container network, so it WILL resolve these forward_hosts relative to itself.
    # The 'forward_host' is used by NPM container, not this script.

    services = [
        # FastAPI Production
        {
            "domain_names": ["api.pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-app-prod",
            "forward_port": 8000
        },
        # FastAPI Development
        {
            "domain_names": ["api-dev.pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-app-dev",
            "forward_port": 8000
        },
        # System Monitor (Root Domain)
        {
            "domain_names": ["pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-system-monitor",
            "forward_port": 80
        },
        # Portainer (HTTPS)
        {
            "domain_names": ["portainer.pocmaster.argentquest.com"],
            "forward_scheme": "https",
            "forward_host": "portainer",
            "forward_port": 9443,
            "advanced_config": "proxy_ssl_verify off;"
        },
        # pgAdmin
        {
            "domain_names": ["pgadmin.pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-pgadmin",
            "forward_port": 80
        },
        # MongoDB Express
        {
            "domain_names": ["mongo.pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-mongo-express",
            "forward_port": 8081
        },
        # Redis Commander
        {
            "domain_names": ["redis.pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-redis-commander",
            "forward_port": 8081
        },
        # MinIO Console
        {
            "domain_names": ["minio.pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-minio",
            "forward_port": 9001,
            "advanced_config": "client_max_body_size 100M;"
        },
        # VS Code Server
        {
            "domain_names": ["code.pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-vscode",
            "forward_port": 8080,
            "advanced_config": "proxy_connect_timeout 120s; proxy_send_timeout 120s; proxy_read_timeout 120s;"
        },
        # n8n
        {
            "domain_names": ["n8n.pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-n8n",
            "forward_port": 5678
        },
        # Jupyter
        {
            "domain_names": ["jupyter.pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-jupyter",
            "forward_port": 8888
        },
        # Beszel
        {
            "domain_names": ["beszel.pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-beszel",
            "forward_port": 8090
        },
        # Heimdall
        {
            "domain_names": ["heimdall.pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-heimdall",
            "forward_port": 80
        },
        # Monitor API
        {
            "domain_names": ["monitor-api.pocmaster.argentquest.com"],
            "forward_host": "aq-devsuite-monitor-api",
            "forward_port": 8083
        }
    ]
    
    # 5. Create Hosts
    success = 0
    for config in services:
        if create_proxy_host(base_url, token, config):
            success += 1
        time.sleep(1)
    
    print("="*50)
    print(f"Setup complete: {success}/{len(services)} hosts configured")
    
    # 6. Run Heimdall Setup
    print("="*50)
    print("Running Heimdall Auto-Configuration...")
    try:
        import subprocess
        subprocess.run(["python3", "heimdall-auto-setup.py"], check=False)
    except Exception as e:
        print(f"Failed to run Heimdall setup: {e}")
        
    print("="*50)

if __name__ == "__main__":
    main()
