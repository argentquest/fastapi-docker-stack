#!/usr/bin/env python3
"""
Test 01: Container Health and Connectivity

This test script performs the most basic and essential validation of the V2 stack.
It ensures that all Docker containers are running and that the core services are
accessible and reporting a healthy status.

This is the first test that should be run after starting the application.
"""

import sys
import time
import requests
import subprocess
from typing import Dict, Any

def main():
    """Main test execution function."""
    print("=" * 60)
    print("TEST 01: CONTAINER HEALTH AND CONNECTIVITY VALIDATION")
    print("=" * 60)
    
    # --- Check 1: Docker Container Status ---
    print("\n1. Verifying that all expected Docker containers are running...")
    container_status = check_container_status()
    if not container_status['all_running']:
        print(f"❌ FAILED: The following containers are not running: {container_status['missing']}")
        print("Please check `docker-compose ps` and `docker-compose logs`.")
        return False
    print("✅ All expected containers are running.")
    
    # --- Check 2: Application Health Endpoint ---
    print("\n2. Querying the application's master health check endpoint...")
    # This endpoint provides an aggregated health status from all backend services.
    health_status = test_health_endpoint()
    if not health_status['healthy']:
        print(f"❌ FAILED: The application's health endpoint reports issues.")
        print(f"Unhealthy services reported: {health_status['unhealthy']}")
        return False
    print("✅ Application health endpoint reports all services are healthy.")
    
    print("\n" + "=" * 60)
    print("✅ TEST 01 PASSED: All containers are running and report a healthy status.")
    print("=" * 60)
    return True

def check_container_status() -> Dict[str, Any]:
    """
    Checks `docker ps` to see if all expected containers are in a running state.

    Returns:
        A dictionary containing the test result and lists of running/missing containers.
    """
    expected_containers = [
        'v2-poc-app', 'v2-poc-npm', 'v2-poc-postgres',
        'v2-poc-minio', 'v2-poc-redis', 'v2-poc-pgadmin', 
        'v2-poc-redis-commander', 'v2-poc-dashboard'
    ]
    
    try:
        # Use `docker ps` to get the names of all currently running containers.
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}'],
            capture_output=True, text=True, check=True, timeout=10
        )
        running_containers = result.stdout.strip().split('\n')
        
        missing = [c for c in expected_containers if c not in running_containers]
        
        for container in sorted(expected_containers):
            status_icon = "✅" if container in running_containers else "❌"
            print(f"  {status_icon} {container}")
            
        return {'all_running': not missing, 'missing': missing}
        
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Error executing `docker ps`: {e}")
        return {'all_running': False, 'missing': expected_containers}

def test_health_endpoint() -> Dict[str, Any]:
    """
    Tests the application's primary `/health` endpoint.

    Returns:
        A dictionary summarizing the health status of the services.
    """
    health_url = "http://localhost/health"
    try:
        # Allow a moment for services to respond after startup.
        time.sleep(2)
        response = requests.get(health_url, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx) 
        
        health_data = response.json()
        print(f"Successfully connected to {health_url} (Status: {response.status_code})")
        
        overall_status = health_data.get('status', 'unknown')
        unhealthy_services = []
        
        # Check the status of each individual container reported by the endpoint.
        for service, details in health_data.get('containers', {}).items():
            service_status = details.get('status', 'unknown')
            status_icon = "✅" if service_status == 'healthy' else "❌"
            print(f"  {status_icon} {service}: {service_status}")
            if service_status != 'healthy':
                unhealthy_services.append(service)
        
        is_healthy = overall_status == 'healthy' and not unhealthy_services
        return {'healthy': is_healthy, 'unhealthy': unhealthy_services}
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to health endpoint at {health_url}: {e}")
        return {'healthy': False, 'unhealthy': ['all'], 'error': str(e)}

if __name__ == '__main__':
    # Set the exit code based on the test result.
    # 0 for success, 1 for failure. This is useful for CI/CD pipelines.
    if main():
        sys.exit(0)
    else:
        sys.exit(1)