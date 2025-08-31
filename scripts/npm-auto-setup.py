#!/usr/bin/env python3
"""
NPM Auto-Setup Script
Automatically configures Nginx Proxy Manager proxy hosts based on Docker service labels.
"""

import requests
import json
import time
import sys
import os
from typing import Dict, List, Optional

class NPMAutoSetup:
    def __init__(self, npm_url: str = "http://localhost:81", 
                 username: str = "admin@example.com", 
                 password: str = "changeme"):
        self.npm_url = npm_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()
        
    def login(self) -> bool:
        """Login to NPM and get authentication token."""
        try:
            response = self.session.post(
                f"{self.npm_url}/api/tokens",
                json={
                    "identity": self.username,
                    "secret": self.password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                print(f"NPM login successful")
                return True
            else:
                print(f"NPM login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"NPM login error: {e}")
            return False
    
    def get_existing_hosts(self) -> List[Dict]:
        """Get list of existing proxy hosts."""
        try:
            response = self.session.get(f"{self.npm_url}/api/nginx/proxy-hosts")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"⚠️ Could not fetch existing hosts: {e}")
            return []
    
    def create_proxy_host(self, domain: str, target_host: str, target_port: int, 
                         websockets: bool = True) -> bool:
        """Create a new proxy host in NPM."""
        try:
            # Check if host already exists
            existing_hosts = self.get_existing_hosts()
            for host in existing_hosts:
                if domain in host.get('domain_names', []):
                    print(f"⏭️ Host {domain} already exists, skipping")
                    return True
            
            payload = {
                "domain_names": [domain],
                "forward_host": target_host,
                "forward_port": target_port,
                "access_list_id": 0,
                "certificate_id": 0,
                "ssl_forced": False,
                "caching_enabled": False,
                "block_exploits": True,
                "advanced_config": "",
                "meta": {
                    "letsencrypt_agree": False,
                    "dns_challenge": False
                },
                "allow_websocket_upgrade": websockets,
                "http2_support": True,
                "forward_scheme": "http",
                "enabled": True
            }
            
            response = self.session.post(
                f"{self.npm_url}/api/nginx/proxy-hosts",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 201:
                print(f"✅ Created proxy host: {domain} → {target_host}:{target_port}")
                return True
            else:
                print(f"❌ Failed to create {domain}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating proxy host {domain}: {e}")
            return False

def main():
    """Main function to set up all proxy hosts."""
    print("Starting NPM Auto-Setup...")
    
    # Service configurations
    services = [
        {
            "domain": "api.pocmaster.argentquest.com",
            "target": "aq-devsuite-app-prod",
            "port": 8000,
            "websockets": True
        },
        {
            "domain": "api-dev.pocmaster.argentquest.com", 
            "target": "aq-devsuite-app-dev",
            "port": 8000,
            "websockets": True
        },
        {
            "domain": "pgadmin.pocmaster.argentquest.com",
            "target": "aq-devsuite-pgadmin", 
            "port": 80,
            "websockets": False
        },
        {
            "domain": "mongo.pocmaster.argentquest.com",
            "target": "aq-devsuite-mongo-express",
            "port": 8081,
            "websockets": False
        },
        {
            "domain": "redis.pocmaster.argentquest.com",
            "target": "aq-devsuite-redis-commander",
            "port": 8081,
            "websockets": False
        },
        {
            "domain": "minio.pocmaster.argentquest.com",
            "target": "aq-devsuite-minio",
            "port": 9001,
            "websockets": False
        },
        {
            "domain": "portainer.pocmaster.argentquest.com",
            "target": "aq-devsuite-portainer",
            "port": 9000,
            "websockets": True
        },
        {
            "domain": "heimdall.pocmaster.argentquest.com",
            "target": "aq-devsuite-heimdall",
            "port": 80,
            "websockets": False
        },
        {
            "domain": "code.pocmaster.argentquest.com",
            "target": "aq-devsuite-vscode",
            "port": 8080,
            "websockets": True
        },
        {
            "domain": "mcp.pocmaster.argentquest.com",
            "target": "aq-devsuite-mcp-inspector",
            "port": 5173,
            "websockets": True
        },
        {
            "domain": "n8n.pocmaster.argentquest.com",
            "target": "aq-devsuite-n8n",
            "port": 5678,
            "websockets": True
        },
        {
            "domain": "jupyter.pocmaster.argentquest.com",
            "target": "aq-devsuite-jupyter",
            "port": 8888,
            "websockets": True
        }
    ]
    
    # Wait for NPM to be ready
    print("⏳ Waiting for NPM to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:81", timeout=5)
            if response.status_code == 200:
                print("✅ NPM is ready")
                break
        except:
            pass
        
        if i == max_retries - 1:
            print("❌ NPM not ready after 150 seconds")
            sys.exit(1)
            
        time.sleep(5)
    
    # Initialize NPM client
    npm = NPMAutoSetup()
    
    # Login to NPM
    if not npm.login():
        print("❌ Could not login to NPM")
        sys.exit(1)
    
    # Create all proxy hosts
    success_count = 0
    total_count = len(services)
    
    for service in services:
        if npm.create_proxy_host(
            domain=service["domain"],
            target_host=service["target"], 
            target_port=service["port"],
            websockets=service["websockets"]
        ):
            success_count += 1
        
        # Small delay between requests
        time.sleep(1)
    
    # Summary
    print(f"\n📊 NPM Auto-Setup Complete:")
    print(f"✅ Successfully configured: {success_count}/{total_count} proxy hosts")
    
    if success_count == total_count:
        print("🎉 All services are now accessible via subdomains!")
        print("\nTest with:")
        for service in services:
            print(f"  curl -I http://{service['domain']}")
    else:
        print("⚠️ Some services may need manual configuration")
        print("Check NPM Admin UI for details: http://pocmaster.argentquest.com:81")

if __name__ == "__main__":
    main()