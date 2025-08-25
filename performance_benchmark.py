#!/usr/bin/env python
"""
Performance benchmarking script for V2 POC.
Tests the performance baselines mentioned in POC_PLAN.md.
"""

import time
import requests
import psutil
import json
from typing import Dict, List
import statistics


def test_health_endpoint_performance() -> Dict:
    """Test health endpoint response time."""
    print("Testing health endpoint performance...")
    
    times = []
    for i in range(10):
        start = time.time()
        try:
            response = requests.get("http://localhost:8000/health", timeout=30)
            elapsed = (time.time() - start) * 1000  # Convert to milliseconds
            if response.status_code == 200:
                times.append(elapsed)
                print(f"  Request {i+1}: {elapsed:.0f}ms")
            else:
                print(f"  Request {i+1}: Failed (HTTP {response.status_code})")
        except Exception as e:
            print(f"  Request {i+1}: Error - {e}")
    
    if times:
        return {
            "avg_response_time_ms": statistics.mean(times),
            "min_response_time_ms": min(times),
            "max_response_time_ms": max(times),
            "successful_requests": len(times),
            "total_requests": 10
        }
    else:
        return {"error": "All requests failed"}


def test_memory_usage() -> Dict:
    """Test current memory usage of the system."""
    print("Testing memory usage...")
    
    # System memory
    system_memory = psutil.virtual_memory()
    
    # Try to get Docker container memory usage
    container_memory = {}
    try:
        import docker
        client = docker.from_env()
        containers = client.containers.list()
        
        for container in containers:
            if container.name.startswith('v2-poc-'):
                stats = container.stats(stream=False)
                if 'memory' in stats:
                    memory_usage = stats['memory']['usage']
                    memory_limit = stats['memory']['limit']
                    container_memory[container.name] = {
                        "usage_mb": memory_usage / (1024 * 1024),
                        "limit_mb": memory_limit / (1024 * 1024),
                        "usage_percent": (memory_usage / memory_limit) * 100
                    }
    except Exception as e:
        print(f"  Could not get Docker container stats: {e}")
    
    return {
        "system_memory": {
            "total_gb": system_memory.total / (1024**3),
            "used_gb": system_memory.used / (1024**3),
            "available_gb": system_memory.available / (1024**3),
            "percent_used": system_memory.percent
        },
        "container_memory": container_memory
    }


def test_cpu_usage() -> Dict:
    """Test current CPU usage."""
    print("Testing CPU usage...")
    
    # Get CPU usage over a short period
    cpu_before = psutil.cpu_percent(interval=None)
    time.sleep(1)
    cpu_after = psutil.cpu_percent(interval=1)
    
    cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
    
    return {
        "overall_cpu_percent": cpu_after,
        "cpu_count": psutil.cpu_count(),
        "cpu_per_core": cpu_per_core,
        "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else "N/A"
    }


def test_service_availability() -> Dict:
    """Test which services are available and responding."""
    print("Testing service availability...")
    
    services = {
        "FastAPI Docker (8000)": "http://localhost:8000/health",
        "FastAPI Debug (8001)": "http://localhost:8001/health",
        "MinIO Console (9001)": "http://localhost:9001/minio/health/live",
        "pgAdmin (5050)": "http://localhost:5050/misc/ping",
        "Redis Commander (8081)": "http://localhost:8081/",
        "Nginx Proxy Manager (81)": "http://localhost:81/",
        "Dashboard (8082)": "http://localhost:8082/"
    }
    
    results = {}
    for service_name, url in services.items():
        try:
            start = time.time()
            response = requests.get(url, timeout=5)
            elapsed = (time.time() - start) * 1000
            
            results[service_name] = {
                "status": "available",
                "response_time_ms": elapsed,
                "http_status": response.status_code
            }
            print(f"  [OK] {service_name}: {elapsed:.0f}ms (HTTP {response.status_code})")
        except requests.exceptions.Timeout:
            results[service_name] = {
                "status": "timeout",
                "error": "Request timed out"
            }
            print(f"  [TIMEOUT] {service_name}: Timed out")
        except Exception as e:
            results[service_name] = {
                "status": "unavailable", 
                "error": str(e)
            }
            print(f"  [X] {service_name}: {e}")
    
    return results


def generate_performance_report(results: Dict) -> None:
    """Generate a formatted performance report."""
    print("\n" + "=" * 60)
    print("PERFORMANCE BENCHMARK REPORT")
    print("=" * 60)
    
    # Health endpoint performance
    if "health_performance" in results:
        health = results["health_performance"]
        if "avg_response_time_ms" in health:
            print(f"\nHealth Endpoint Performance:")
            print(f"  Average Response Time: {health['avg_response_time_ms']:.0f}ms")
            print(f"  Min/Max Response Time: {health['min_response_time_ms']:.0f}ms / {health['max_response_time_ms']:.0f}ms")
            print(f"  Success Rate: {health['successful_requests']}/{health['total_requests']} ({health['successful_requests']/health['total_requests']*100:.0f}%)")
        else:
            print(f"\nHealth Endpoint Performance: FAILED - {health.get('error', 'Unknown error')}")
    
    # Memory usage
    if "memory_usage" in results:
        memory = results["memory_usage"]
        sys_mem = memory["system_memory"]
        print(f"\nMemory Usage:")
        print(f"  System Memory: {sys_mem['used_gb']:.1f}GB / {sys_mem['total_gb']:.1f}GB ({sys_mem['percent_used']:.1f}%)")
        
        if memory["container_memory"]:
            total_container_mb = sum(c["usage_mb"] for c in memory["container_memory"].values())
            print(f"  Container Memory: {total_container_mb:.0f}MB total")
            for container, stats in memory["container_memory"].items():
                container_name = container.replace("v2-poc-", "")
                print(f"    {container_name}: {stats['usage_mb']:.0f}MB ({stats['usage_percent']:.1f}%)")
    
    # CPU usage
    if "cpu_usage" in results:
        cpu = results["cpu_usage"]
        print(f"\nCPU Usage:")
        print(f"  Overall CPU: {cpu['overall_cpu_percent']:.1f}%")
        print(f"  CPU Cores: {cpu['cpu_count']}")
        if cpu["load_average"] != "N/A":
            print(f"  Load Average: {cpu['load_average']}")
    
    # Service availability
    if "service_availability" in results:
        services = results["service_availability"]
        available_count = sum(1 for s in services.values() if s["status"] == "available")
        total_count = len(services)
        
        print(f"\nService Availability: {available_count}/{total_count} services available")
        for service_name, status in services.items():
            if status["status"] == "available":
                print(f"  [OK] {service_name}: {status['response_time_ms']:.0f}ms")
            else:
                print(f"  [X] {service_name}: {status['status']}")
    
    # POC Plan baseline comparison
    print(f"\nPOC PLAN BASELINE COMPARISON:")
    print(f"  Response time < 5 seconds: {'PASS' if health.get('avg_response_time_ms', 0) < 5000 else 'FAIL'}")
    print(f"  Memory usage < 4GB total: {'PASS' if sys_mem.get('used_gb', 0) < 4 else 'UNKNOWN'}")
    print(f"  CPU usage < 50%: {'PASS' if cpu.get('overall_cpu_percent', 0) < 50 else 'FAIL'}")


def main():
    """Run all performance benchmarks."""
    print("[ROCKET] V2 POC PERFORMANCE BENCHMARK [ROCKET]")
    print("=" * 60)
    
    results = {}
    
    # Run all benchmark tests
    results["health_performance"] = test_health_endpoint_performance()
    results["memory_usage"] = test_memory_usage()
    results["cpu_usage"] = test_cpu_usage()
    results["service_availability"] = test_service_availability()
    
    # Generate report
    generate_performance_report(results)
    
    # Save results to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"performance_benchmark_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()