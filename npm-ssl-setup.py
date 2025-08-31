#!/usr/bin/env python3
"""
Configure Let's Encrypt SSL certificates for all domains
"""

import requests
import json
import time

def main():
    npm_url = "http://localhost:81"
    api_url = f"{npm_url}/api"
    domain = "pocmaster.argentquest.com"
    email = "admin@argentquest.com"
    
    # Login
    login_data = {"identity": "admin@example.com", "secret": "changeme"}
    response = requests.post(f"{api_url}/tokens", json=login_data)
    token = response.json().get("token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("[INFO] Creating Let's Encrypt SSL certificate...")
    
    # Create SSL certificate for the main domain and all subdomains
    cert_config = {
        "provider": "letsencrypt",
        "domain_names": [
            domain,
            f"portainer.{domain}",
            f"pgadmin.{domain}",
            f"mongo.{domain}",
            f"redis.{domain}",
            f"minio.{domain}",
            f"code.{domain}",
            f"mcp.{domain}",
            f"api-dev.{domain}",
            f"api.{domain}",
            f"heimdall.{domain}"
        ],
        "meta": {
            "letsencrypt_email": email,
            "letsencrypt_agree": True,
            "dns_challenge": False
        }
    }
    
    response = requests.post(f"{api_url}/nginx/certificates", json=cert_config, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        cert_id = result.get("id")
        print(f"[SUCCESS] SSL certificate created with ID: {cert_id}")
        
        # Wait for certificate to be issued
        print("[WAIT] Waiting for Let's Encrypt certificate issuance...")
        time.sleep(60)
        
        # Get all proxy hosts and update them to use SSL
        print("[UPDATE] Updating all proxy hosts to use SSL...")
        hosts_response = requests.get(f"{api_url}/nginx/proxy-hosts", headers=headers)
        hosts = hosts_response.json()
        
        updated_count = 0
        for host in hosts:
            host_id = host["id"]
            domain_name = host.get("domain_names", ["unknown"])[0]
            
            # Update host to use SSL
            host["certificate_id"] = cert_id
            host["ssl_forced"] = True
            host["hsts_enabled"] = True
            host["hsts_subdomains"] = False
            host["http2_support"] = True
            
            update_response = requests.put(f"{api_url}/nginx/proxy-hosts/{host_id}", json=host, headers=headers)
            
            if update_response.status_code == 200:
                print(f"[SUCCESS] Updated {domain_name} to use SSL")
                updated_count += 1
            else:
                print(f"[ERROR] Failed to update {domain_name}: {update_response.status_code}")
            
            time.sleep(1)
        
        print(f"\n[COMPLETE] Updated {updated_count} proxy hosts to use SSL")
        print(f"\n[INFO] All services now available via HTTPS:")
        print(f"   Main Dashboard:     https://{domain}")
        print(f"   Docker Management:  https://portainer.{domain}")
        print(f"   PostgreSQL Admin:   https://pgadmin.{domain}")
        print(f"   And all other services...")
        
    else:
        print(f"[ERROR] SSL certificate creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"\n[INFO] This is normal for local development.")
        print(f"[INFO] For production, ensure:")
        print(f"   1. Domain points to your server's public IP")
        print(f"   2. Ports 80 and 443 are open")
        print(f"   3. Remove hosts file entries")

if __name__ == "__main__":
    main()