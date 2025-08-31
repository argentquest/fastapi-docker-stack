#!/usr/bin/env python3
"""
NPM Simple Setup - Individual proxy hosts for each service
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class NPMSimpleSetup:
    def __init__(self, npm_url: str = "http://localhost:81"):
        self.npm_url = npm_url.rstrip('/')
        self.api_url = f"{self.npm_url}/api"
        self.token = None
        
    def login(self, email: str, password: str) -> bool:
        """Login to NPM and get authentication token"""
        print(f"[LOGIN] Logging into NPM at {self.npm_url}...")
        
        login_data = {
            "identity": email,
            "secret": password
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/tokens",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("token")
                print("[SUCCESS] Successfully logged into NPM")
                return True
            else:
                print(f"[ERROR] Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Login error: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def delete_all_proxy_hosts(self):
        """Delete all existing proxy hosts"""
        try:
            response = requests.get(
                f"{self.api_url}/nginx/proxy-hosts",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                hosts = response.json()
                for host in hosts:
                    print(f"[DELETE] Deleting proxy host ID: {host['id']}")
                    delete_response = requests.delete(
                        f"{self.api_url}/nginx/proxy-hosts/{host['id']}",
                        headers=self.get_headers()
                    )
                    if delete_response.status_code == 200:
                        print(f"[SUCCESS] Deleted proxy host {host['id']}")
                    else:
                        print(f"[ERROR] Failed to delete {host['id']}")
                    time.sleep(1)
        except Exception as e:
            print(f"[ERROR] Error deleting hosts: {str(e)}")
    
    def create_proxy_host(self, config: Dict[str, Any]) -> bool:
        """Create a single proxy host"""
        domain = config.get('domain_names', ['Unknown'])[0]
        print(f"[PROXY] Creating proxy host for {domain}...")
        
        try:
            response = requests.post(
                f"{self.api_url}/nginx/proxy-hosts",
                json=config,
                headers=self.get_headers()
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"[SUCCESS] Proxy host created: {result.get('id')}")
                return True
            else:
                print(f"[ERROR] Proxy host creation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Proxy host error: {str(e)}")
            return False

def main():
    print("NPM Simple Setup Script")
    print("=" * 50)
    
    # Configuration
    DOMAIN = "pocmaster.argentquest.com"
    
    # NPM credentials
    npm = NPMSimpleSetup()
    
    # Login with default credentials
    if not npm.login("admin@example.com", "changeme"):
        print("[ERROR] Failed to login to NPM")
        sys.exit(1)
    
    # Delete existing proxy hosts first
    print("\n[CLEANUP] Removing existing proxy hosts...")
    npm.delete_all_proxy_hosts()
    
    # Port-based configurations for single domain
    configs = [
        # Main Dashboard (System Monitor)
        {
            "domain_names": [DOMAIN],
            "forward_scheme": "http", 
            "forward_host": "172.21.0.11",
            "forward_port": 80,
            "certificate_id": 0,
            "ssl_forced": False,
            "caching_enabled": False,
            "block_exploits": False,
            "allow_websocket_upgrade": False,
            "access_list_id": 0
        },
        # Portainer on port 9443
        {
            "domain_names": [f"{DOMAIN}:9443"],
            "forward_scheme": "https",
            "forward_host": "172.24.0.10", 
            "forward_port": 9443,
            "certificate_id": 0,
            "ssl_forced": False,
            "caching_enabled": False,
            "block_exploits": False,
            "allow_websocket_upgrade": True,
            "access_list_id": 0,
            "advanced_config": "proxy_ssl_verify off;"
        },
        # pgAdmin on port 5050  
        {
            "domain_names": [f"{DOMAIN}:5050"],
            "forward_scheme": "http",
            "forward_host": "172.24.0.11",
            "forward_port": 80,
            "certificate_id": 0,
            "ssl_forced": False,
            "caching_enabled": False,
            "block_exploits": False,
            "allow_websocket_upgrade": False,
            "access_list_id": 0
        }
    ]
    
    success_count = 0
    for config in configs:
        if npm.create_proxy_host(config):
            success_count += 1
        time.sleep(2)
    
    print(f"\n[COMPLETE] Setup Complete: {success_count}/{len(configs)} proxy hosts configured")
    print(f"\n[ACCESS] Test your services:")
    print(f"   Main Dashboard: http://{DOMAIN}")
    print(f"   Docker Management: https://{DOMAIN}:9443")
    print(f"   PostgreSQL Admin: http://{DOMAIN}:5050") 
    print(f"   NPM Admin: http://{DOMAIN}:81")

if __name__ == "__main__":
    main()