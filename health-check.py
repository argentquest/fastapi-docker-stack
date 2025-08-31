#!/usr/bin/env python3
"""
Comprehensive Health Check for all V2 POC services
"""

import requests
import json
import time
from typing import Dict, List

def check_service(name: str, url: str, expected_status: int = 200, timeout: int = 10) -> Dict:
    """Check a single service and return status"""
    result = {
        "service": name,
        "url": url,
        "status": "unknown",
        "response_time": 0,
        "error": None
    }
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout, allow_redirects=True, verify=False)
        result["response_time"] = round((time.time() - start_time) * 1000, 2)
        
        if response.status_code == expected_status:
            result["status"] = "healthy"
        elif response.status_code in [301, 302, 401, 403]:  # Redirect or auth required is OK
            result["status"] = "healthy"
        else:
            result["status"] = "unhealthy"
            result["error"] = f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["error"] = "Request timeout"
    except requests.exceptions.ConnectionError:
        result["status"] = "unreachable"
        result["error"] = "Connection failed"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

def main():
    print("=" * 60)
    print("V2 POC Health Check Report")
    print("=" * 60)
    
    # Services to check
    services = [
        ("Main Dashboard", "http://pocmaster.argentquest.com"),
        ("NPM Admin", "http://pocmaster.argentquest.com:81"),
        ("Portainer", "http://portainer.pocmaster.argentquest.com"),
        ("pgAdmin", "http://pgadmin.pocmaster.argentquest.com"),
        ("MongoDB Express", "http://mongo.pocmaster.argentquest.com"),
        ("Redis Commander", "http://redis.pocmaster.argentquest.com"),
        ("MinIO Console", "http://minio.pocmaster.argentquest.com"),
        ("VS Code Server", "http://code.pocmaster.argentquest.com"),
        ("MCP Inspector", "http://mcp.pocmaster.argentquest.com"),
        ("FastAPI Dev", "http://api-dev.pocmaster.argentquest.com"),
        ("FastAPI Prod", "http://api.pocmaster.argentquest.com"),
        ("Heimdall", "http://heimdall.pocmaster.argentquest.com"),
        
        # Direct port access
        ("pgAdmin Direct", "http://localhost:5050"),
        ("Portainer Direct", "https://localhost:9443")
    ]
    
    # Container health check (Docker API)
    print(f"\n{'Service':<20} {'Status':<12} {'Response':<10} {'Error':<30}")
    print("-" * 75)
    
    healthy = 0
    total = len(services)
    results = []
    
    for name, url in services:
        result = check_service(name, url)
        results.append(result)
        
        if result["status"] == "healthy":
            healthy += 1
            status_emoji = "[OK]"
        elif result["status"] in ["timeout", "unreachable"]:
            status_emoji = "[--]"
        else:
            status_emoji = "[XX]"
        
        error_msg = result.get('error', '') or ''
        print(f"{name:<20} {status_emoji} {result['status']:<10} {result['response_time']:<8}ms {error_msg:<30}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"SUMMARY: {healthy}/{total} services healthy ({(healthy/total)*100:.1f}%)")
    
    # Service status by category
    proxy_services = [r for r in results if "pocmaster.argentquest.com" in r["url"] and ":81" not in r["url"]]
    direct_services = [r for r in results if "localhost" in r["url"]]
    npm_admin = [r for r in results if ":81" in r["url"]]
    
    proxy_healthy = sum(1 for r in proxy_services if r["status"] == "healthy")
    direct_healthy = sum(1 for r in direct_services if r["status"] == "healthy")
    npm_healthy = sum(1 for r in npm_admin if r["status"] == "healthy")
    
    print(f"\nProxy Services:  {proxy_healthy}/{len(proxy_services)} healthy")
    print(f"Direct Access:   {direct_healthy}/{len(direct_services)} healthy")
    print(f"NPM Admin:       {npm_healthy}/{len(npm_admin)} healthy")
    
    # Recommendations
    print(f"\nRECOMMENDATIONS:")
    unreachable = [r for r in results if r["status"] == "unreachable"]
    if unreachable:
        print(f"   • Add missing hosts file entries for unreachable services")
        for r in unreachable:
            if "pocmaster.argentquest.com" in r["url"]:
                domain = r["url"].split("//")[1].split("/")[0].split(":")[0]
                print(f"     127.0.0.1    {domain}")
    
    if healthy == total:
        print(f"   • All services are healthy!")
    else:
        print(f"   • {total - healthy} services need attention")
    
    print(f"\nQUICK ACCESS LINKS:")
    print(f"   NPM Admin: http://pocmaster.argentquest.com:81")
    print(f"   Main Dashboard: http://pocmaster.argentquest.com")
    print(f"   Docker Management: https://localhost:9443")

if __name__ == "__main__":
    main()