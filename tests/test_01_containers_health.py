#!/usr/bin/env python3
"""
Test 01: Container Health Validation
Tests that all 5 containers are running and healthy
"""

import sys
import time
import requests
import subprocess
import json
from typing import Dict, Any

def run_test():
    """Test all container health status"""
    print("=" * 60)
    print("TEST 01: CONTAINER HEALTH VALIDATION")
    print("=" * 60)
    
    # Check if containers are running
    print("\n1. Checking container status...")
    container_status = check_container_status()
    
    if not container_status['all_running']:
        print("❌ FAILED: Not all containers are running")
        print("Missing containers:", container_status['missing'])
        return False
    
    print("✅ All containers are running")
    
    # Test application health endpoint
    print("\n2. Testing application health endpoint...")
    health_status = test_health_endpoint()
    
    if not health_status['healthy']:
        print("❌ FAILED: Health endpoint reports issues")
        print("Unhealthy services:", health_status['unhealthy'])
        return False
    
    print("✅ All services report healthy status")
    
    # Test individual container connectivity
    print("\n3. Testing individual container connectivity...")
    connectivity_results = test_individual_connectivity()
    
    failed_connections = [name for name, status in connectivity_results.items() if not status['success']]
    if failed_connections:
        print(f"❌ FAILED: Cannot connect to: {failed_connections}")
        return False
    
    print("✅ All containers are individually accessible")
    
    print("\n" + "=" * 60)
    print("✅ TEST 01 PASSED: All containers are healthy and accessible")
    print("=" * 60)
    return True

def check_container_status() -> Dict[str, Any]:
    """Check if all expected containers are running"""
    expected_containers = [
        'v2-poc-app',
        'v2-poc-nginx', 
        'v2-poc-postgres',
        'v2-poc-minio',
        'v2-poc-redis'
    ]
    
    try:
        # Get running containers
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            check=True
        )
        
        running_containers = result.stdout.strip().split('\n')
        running_containers = [c.strip() for c in running_containers if c.strip()]
        
        missing = [c for c in expected_containers if c not in running_containers]
        
        print(f"Expected containers: {len(expected_containers)}")
        print(f"Running containers: {len(running_containers)}")
        
        for container in expected_containers:
            status = "✅ Running" if container in running_containers else "❌ Missing"
            print(f"  {container}: {status}")
        
        return {
            'all_running': len(missing) == 0,
            'running': running_containers,
            'missing': missing
        }
        
    except subprocess.CalledProcessError as e:
        print(f"Error checking container status: {e}")
        return {'all_running': False, 'running': [], 'missing': expected_containers}

def test_health_endpoint() -> Dict[str, Any]:
    """Test the application health endpoint"""
    try:
        # Wait a moment for services to stabilize
        time.sleep(2)
        
        response = requests.get('http://localhost/health', timeout=30)
        
        if response.status_code != 200:
            print(f"Health endpoint returned status: {response.status_code}")
            return {'healthy': False, 'error': f'HTTP {response.status_code}'}
        
        health_data = response.json()
        print(f"Health endpoint response: {response.status_code}")
        
        # Check overall status
        overall_status = health_data.get('status', 'unknown')
        print(f"Overall status: {overall_status}")
        
        # Check individual containers
        containers = health_data.get('containers', {})
        unhealthy = []
        
        for service, details in containers.items():
            service_status = details.get('status', 'unknown') if isinstance(details, dict) else 'unknown'
            status_icon = "✅" if service_status == 'healthy' else "❌"
            print(f"  {service}: {status_icon} {service_status}")
            
            if service_status != 'healthy':
                unhealthy.append(service)
        
        return {
            'healthy': overall_status == 'healthy' and len(unhealthy) == 0,
            'overall_status': overall_status,
            'unhealthy': unhealthy,
            'details': health_data
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to health endpoint: {e}")
        return {'healthy': False, 'error': str(e)}

def test_individual_connectivity() -> Dict[str, Dict[str, Any]]:
    """Test connectivity to each container individually"""
    tests = {
        'nginx': test_nginx_connectivity,
        'app': test_app_connectivity,
        'postgres': test_postgres_connectivity,
        'redis': test_redis_connectivity,
        'minio': test_minio_connectivity
    }
    
    results = {}
    
    for service, test_func in tests.items():
        print(f"  Testing {service}...")
        try:
            results[service] = test_func()
            status_icon = "✅" if results[service]['success'] else "❌"
            print(f"    {status_icon} {results[service].get('message', 'OK')}")
        except Exception as e:
            results[service] = {'success': False, 'error': str(e)}
            print(f"    ❌ Error: {e}")
    
    return results

def test_nginx_connectivity() -> Dict[str, Any]:
    """Test Nginx connectivity"""
    response = requests.get('http://localhost/', timeout=10)
    return {
        'success': response.status_code in [200, 404],  # 404 is OK, means nginx is routing
        'status_code': response.status_code,
        'message': f'HTTP {response.status_code}'
    }

def test_app_connectivity() -> Dict[str, Any]:
    """Test FastAPI app connectivity"""
    response = requests.get('http://localhost:8000/', timeout=10)
    return {
        'success': response.status_code == 200,
        'status_code': response.status_code,
        'message': f'HTTP {response.status_code}'
    }

def test_postgres_connectivity() -> Dict[str, Any]:
    """Test PostgreSQL connectivity"""
    try:
        result = subprocess.run([
            'docker', 'exec', 'v2-poc-postgres',
            'pg_isready', '-U', 'pocuser', '-d', 'poc_db'
        ], capture_output=True, text=True, timeout=10)
        
        return {
            'success': result.returncode == 0,
            'message': result.stdout.strip() or result.stderr.strip()
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'message': 'Connection timeout'}

def test_redis_connectivity() -> Dict[str, Any]:
    """Test Redis connectivity"""
    try:
        result = subprocess.run([
            'docker', 'exec', 'v2-poc-redis',
            'redis-cli', 'ping'
        ], capture_output=True, text=True, timeout=10)
        
        return {
            'success': result.returncode == 0 and 'PONG' in result.stdout,
            'message': result.stdout.strip()
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'message': 'Connection timeout'}

def test_minio_connectivity() -> Dict[str, Any]:
    """Test MinIO connectivity"""
    try:
        response = requests.get('http://localhost:9000/minio/health/live', timeout=10)
        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'message': f'HTTP {response.status_code}'
        }
    except requests.exceptions.RequestException as e:
        return {'success': False, 'message': str(e)}

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)