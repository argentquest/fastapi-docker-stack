#!/usr/bin/env python3
"""
Simple NPM Auto-Setup Script
Automatically configures NPM proxy hosts.
"""

import requests
import json
import time
import sys

def login_npm():
    """Login to NPM and get token."""
    try:
        response = requests.post(
            "http://aq-devsuite-npm:81/api/tokens",
            json={
                "identity": "admin@example.com",
                "secret": "changeme"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("NPM login successful")
            return data.get('token')
        else:
            print(f"NPM login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"NPM login error: {e}")
        return None

def create_proxy_host(token, domain, target_host, target_port):
    """Create proxy host in NPM."""
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        payload = {
            "domain_names": [domain],
            "forward_host": target_host,
            "forward_port": target_port,
            "access_list_id": 0,
            "certificate_id": 0,
            "ssl_forced": False,
            "caching_enabled": False,
            "block_exploits": True,
            "allow_websocket_upgrade": True,
            "http2_support": True,
            "forward_scheme": "http",
            "enabled": True
        }
        
        response = requests.post(
            "http://aq-devsuite-npm:81/api/nginx/proxy-hosts",
            json=payload,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 201:
            print(f"Created: {domain} -> {target_host}:{target_port}")
            return True
        else:
            print(f"Failed {domain}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error creating {domain}: {e}")
        return False

def main():
    print("Starting NPM Auto-Setup...")
    
    # Wait for NPM
    print("Waiting for NPM...")
    for i in range(30):
        try:
            response = requests.get("http://aq-devsuite-npm:81", timeout=5)
            if response.status_code == 200:
                print("NPM is ready")
                break
        except:
            pass
        time.sleep(5)
    else:
        print("NPM not ready after 150 seconds")
        sys.exit(1)
    
    # Login
    token = login_npm()
    if not token:
        print("Could not login to NPM")
        sys.exit(1)
    
    # Services to configure
    services = [
        ("api.pocmaster.argentquest.com", "aq-devsuite-app-prod", 8000),
        ("api-dev.pocmaster.argentquest.com", "aq-devsuite-app-dev", 8000),
        ("n8n.pocmaster.argentquest.com", "aq-devsuite-n8n", 5678),
        ("jupyter.pocmaster.argentquest.com", "aq-devsuite-jupyter", 8888),
        ("mcp.pocmaster.argentquest.com", "aq-devsuite-mcp-inspector", 5173),
        ("beszel.pocmaster.argentquest.com", "aq-devsuite-beszel", 8090)
    ]
    
    # Create proxy hosts
    success = 0
    for domain, target, port in services:
        if create_proxy_host(token, domain, target, port):
            success += 1
        time.sleep(2)
    
    print(f"Setup complete: {success}/{len(services)} hosts configured")

if __name__ == "__main__":
    main()