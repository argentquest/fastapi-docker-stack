#!/usr/bin/env python
"""
Simple performance benchmarking script for V2 POC.
Tests basic performance without requiring additional dependencies.
"""

import time
import requests
import json
import statistics
from typing import Dict


def test_health_endpoint_performance() -> Dict:
    """Test health endpoint response time."""
    print("Testing health endpoint performance...")
    
    times = []
    success_count = 0
    
    for i in range(5):
        start = time.time()
        try:
            response = requests.get("http://localhost:8000/health", timeout=30)
            elapsed = (time.time() - start) * 1000  # Convert to milliseconds
            times.append(elapsed)
            
            if response.status_code == 200:
                success_count += 1
                print(f"  Request {i+1}: {elapsed:.0f}ms (SUCCESS)")
            else:
                print(f"  Request {i+1}: {elapsed:.0f}ms (HTTP {response.status_code})")
                
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            print(f"  Request {i+1}: {elapsed:.0f}ms (ERROR: {e})")
            times.append(elapsed)
    
    if times:
        return {
            "avg_response_time_ms": statistics.mean(times),
            "min_response_time_ms": min(times),
            "max_response_time_ms": max(times),
            "successful_requests": success_count,
            "total_requests": 5,
            "success_rate_percent": (success_count / 5) * 100
        }
    else:
        return {"error": "All requests failed"}


def test_service_availability() -> Dict:
    """Test which services are available and responding."""
    print("\nTesting service availability...")
    
    services = {
        "FastAPI Docker (8000)": "http://localhost:8000/health",
        "FastAPI Debug (8001)": "http://localhost:8001/health", 
        "MinIO API (9000)": "http://localhost:9000/minio/health/live",
        "MinIO Console (9001)": "http://localhost:9001/",
        "pgAdmin (5050)": "http://localhost:5050/",
        "Redis Commander (8081)": "http://localhost:8081/",
        "Nginx Proxy Manager (81)": "http://localhost:81/",
        "Dashboard (8082)": "http://localhost:8082/"
    }
    
    results = {}
    available_count = 0
    
    for service_name, url in services.items():
        try:
            start = time.time()
            response = requests.get(url, timeout=3)
            elapsed = (time.time() - start) * 1000
            
            if response.status_code < 400:
                results[service_name] = {
                    "status": "available",
                    "response_time_ms": elapsed,
                    "http_status": response.status_code
                }
                available_count += 1
                print(f"  [OK] {service_name}: {elapsed:.0f}ms")
            else:
                results[service_name] = {
                    "status": "available_but_error",
                    "response_time_ms": elapsed,
                    "http_status": response.status_code
                }
                print(f"  [WARN] {service_name}: {elapsed:.0f}ms (HTTP {response.status_code})")
                
        except requests.exceptions.Timeout:
            results[service_name] = {
                "status": "timeout",
                "error": "Request timed out after 3s"
            }
            print(f"  [TIMEOUT] {service_name}")
        except requests.exceptions.ConnectionError:
            results[service_name] = {
                "status": "unavailable",
                "error": "Connection refused"
            }
            print(f"  [X] {service_name}: Not running")
        except Exception as e:
            results[service_name] = {
                "status": "error",
                "error": str(e)
            }
            print(f"  [ERROR] {service_name}: {e}")
    
    results["_summary"] = {
        "available_services": available_count,
        "total_services": len(services),
        "availability_percent": (available_count / len(services)) * 100
    }
    
    return results


def test_docker_containers() -> Dict:
    """Test Docker container status using docker-compose."""
    print("\nTesting Docker container status...")
    
    import subprocess
    
    try:
        # Run docker-compose ps to get container status
        result = subprocess.run(
            ['docker-compose', 'ps', '--format', 'json'],
            capture_output=True, text=True, check=True, timeout=10
        )
        
        containers_json = result.stdout.strip()
        if containers_json:
            containers = []
            for line in containers_json.split('\n'):
                if line.strip():
                    containers.append(json.loads(line))
            
            container_status = {}
            healthy_count = 0
            
            for container in containers:
                name = container.get('Name', 'Unknown')
                service = container.get('Service', 'Unknown')  
                state = container.get('State', 'Unknown')
                status = container.get('Status', 'Unknown')
                
                is_healthy = 'healthy' in status.lower() or state.lower() == 'running'
                if is_healthy:
                    healthy_count += 1
                
                container_status[name] = {
                    "service": service,
                    "state": state,
                    "status": status,
                    "healthy": is_healthy
                }
                
                health_icon = "[OK]" if is_healthy else "[X]"
                print(f"  {health_icon} {service}: {state}")
            
            container_status["_summary"] = {
                "healthy_containers": healthy_count,
                "total_containers": len(containers),
                "health_percent": (healthy_count / len(containers)) * 100 if containers else 0
            }
            
            return container_status
        else:
            return {"error": "No containers found"}
            
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Docker command failed: {e}")
        return {"error": f"Docker command failed: {e}"}
    except Exception as e:
        print(f"  [ERROR] {e}")
        return {"error": str(e)}


def generate_performance_report(results: Dict) -> None:
    """Generate a formatted performance report."""
    print("\n" + "=" * 60)
    print("PERFORMANCE BENCHMARK REPORT")
    print("=" * 60)
    
    # Health endpoint performance
    if "health_performance" in results and "avg_response_time_ms" in results["health_performance"]:
        health = results["health_performance"]
        print(f"\nHealth Endpoint Performance:")
        print(f"  Average Response Time: {health['avg_response_time_ms']:.0f}ms")
        print(f"  Min/Max Response Time: {health['min_response_time_ms']:.0f}ms / {health['max_response_time_ms']:.0f}ms")
        print(f"  Success Rate: {health['successful_requests']}/{health['total_requests']} ({health['success_rate_percent']:.0f}%)")
        
        # POC Plan comparison for response time
        response_time_ok = health['avg_response_time_ms'] < 5000
        print(f"  POC Baseline (< 5s): {'PASS' if response_time_ok else 'FAIL'}")
    
    # Service availability  
    if "service_availability" in results and "_summary" in results["service_availability"]:
        summary = results["service_availability"]["_summary"]
        print(f"\nService Availability:")
        print(f"  Available Services: {summary['available_services']}/{summary['total_services']} ({summary['availability_percent']:.0f}%)")
    
    # Container health
    if "container_status" in results and "_summary" in results["container_status"]:
        summary = results["container_status"]["_summary"] 
        print(f"\nContainer Health:")
        print(f"  Healthy Containers: {summary['healthy_containers']}/{summary['total_containers']} ({summary['health_percent']:.0f}%)")
    
    # Overall assessment
    print(f"\nOVERALL ASSESSMENT:")
    
    # Check if main services are working
    health_working = (results.get("health_performance", {}).get("success_rate_percent", 0) > 0)
    services_available = (results.get("service_availability", {}).get("_summary", {}).get("availability_percent", 0) > 50)
    containers_healthy = (results.get("container_status", {}).get("_summary", {}).get("health_percent", 0) > 70)
    
    if health_working and services_available and containers_healthy:
        print("  Status: HEALTHY - POC is functioning well")
    elif health_working and services_available:
        print("  Status: FUNCTIONAL - Core services working, some containers may have issues") 
    elif health_working:
        print("  Status: MINIMAL - Health endpoint working but limited service availability")
    else:
        print("  Status: DEGRADED - Significant issues detected")


def main():
    """Run all performance benchmarks."""
    print("[ROCKET] V2 POC SIMPLE PERFORMANCE BENCHMARK [ROCKET]")
    print("=" * 60)
    
    results = {}
    
    # Run all benchmark tests
    results["health_performance"] = test_health_endpoint_performance()
    results["service_availability"] = test_service_availability()
    results["container_status"] = test_docker_containers()
    
    # Generate report
    generate_performance_report(results)
    
    # Save results to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"simple_benchmark_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()