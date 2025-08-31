#!/usr/bin/env python3
"""
Complete NPM Setup - Add all remaining services
"""

import requests
import json
import time

def main():
    npm_url = "http://localhost:81"
    api_url = f"{npm_url}/api"
    domain = "pocmaster.argentquest.com"
    
    # Login
    login_data = {"identity": "admin@example.com", "secret": "changeme"}
    response = requests.post(f"{api_url}/tokens", json=login_data)
    token = response.json().get("token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("[INFO] Adding remaining services to NPM proxy...")
    
    # Additional services to add
    new_services = [
        # MongoDB Express
        {
            "domain_names": ["mongo.pocmaster.argentquest.com"],
            "forward_scheme": "http",
            "forward_host": "mongo-express",
            "forward_port": 8081,
            "description": "MongoDB Admin"
        },
        # Redis Commander
        {
            "domain_names": ["redis.pocmaster.argentquest.com"],
            "forward_scheme": "http",
            "forward_host": "redis-commander",
            "forward_port": 8081,
            "description": "Redis Admin"
        },
        # MinIO Console
        {
            "domain_names": ["minio.pocmaster.argentquest.com"],
            "forward_scheme": "http",
            "forward_host": "minio",
            "forward_port": 9001,
            "description": "Object Storage Admin"
        },
        # VS Code Server
        {
            "domain_names": ["code.pocmaster.argentquest.com"],
            "forward_scheme": "http",
            "forward_host": "vscode",
            "forward_port": 8080,
            "description": "VS Code Server",
            "websocket": True
        },
        # MCP Inspector
        {
            "domain_names": ["mcp.pocmaster.argentquest.com"],
            "forward_scheme": "http",
            "forward_host": "mcp-inspector",
            "forward_port": 5173,
            "description": "MCP Protocol Inspector",
            "websocket": True
        },
        # FastAPI Development
        {
            "domain_names": ["api-dev.pocmaster.argentquest.com"],
            "forward_scheme": "http",
            "forward_host": "app-dev",
            "forward_port": 8000,
            "description": "FastAPI Development",
            "websocket": True
        },
        # FastAPI Production
        {
            "domain_names": ["api.pocmaster.argentquest.com"],
            "forward_scheme": "http",
            "forward_host": "app-prod",
            "forward_port": 8000,
            "description": "FastAPI Production",
            "websocket": True
        },
        # Heimdall Dashboard (alternative)
        {
            "domain_names": ["heimdall.pocmaster.argentquest.com"],
            "forward_scheme": "http",
            "forward_host": "heimdall",
            "forward_port": 80,
            "description": "Heimdall Dashboard"
        }
    ]
    
    success_count = 0
    for service in new_services:
        print(f"\n[CREATE] Adding {service['description']} - {service['domain_names'][0]}")
        
        config = {
            "domain_names": service["domain_names"],
            "forward_scheme": service["forward_scheme"],
            "forward_host": service["forward_host"],
            "forward_port": service["forward_port"],
            "certificate_id": 0,
            "ssl_forced": False,
            "caching_enabled": False,
            "block_exploits": False,
            "allow_websocket_upgrade": service.get("websocket", False),
            "access_list_id": 0
        }
        
        # Add advanced config for specific services
        if "minio" in service["forward_host"]:
            config["advanced_config"] = "client_max_body_size 100M;"
        elif "code" in service["forward_host"]:
            config["advanced_config"] = "proxy_connect_timeout 120s; proxy_send_timeout 120s; proxy_read_timeout 120s;"
        
        response = requests.post(f"{api_url}/nginx/proxy-hosts", json=config, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            print(f"[SUCCESS] Created proxy host ID: {result.get('id')}")
            success_count += 1
        else:
            print(f"[ERROR] Failed: {response.status_code}")
            print(f"Response: {response.text}")
        
        time.sleep(1)  # Rate limiting
    
    print(f"\n[COMPLETE] Added {success_count}/{len(new_services)} services")
    
    # Print all service URLs
    print(f"\n[ACCESS] All Service URLs:")
    print(f"   Main Dashboard:     http://{domain}")
    print(f"   Docker Management:  http://portainer.{domain}")
    print(f"   PostgreSQL Admin:   http://pgladmin.{domain}")
    print(f"   MongoDB Admin:      http://mongo.{domain}")
    print(f"   Redis Admin:        http://redis.{domain}")
    print(f"   Object Storage:     http://minio.{domain}")
    print(f"   VS Code Server:     http://code.{domain}")
    print(f"   MCP Inspector:      http://mcp.{domain}")
    print(f"   FastAPI Dev:        http://api-dev.{domain}")
    print(f"   FastAPI Prod:       http://api.{domain}")
    print(f"   Heimdall Alt:       http://heimdall.{domain}")
    print(f"   NPM Admin:          http://{domain}:81")

if __name__ == "__main__":
    main()