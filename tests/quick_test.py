#!/usr/bin/env python
"""
Quick test to check which FastAPI instances are running.
"""

import requests
import sys


def check_port(port: int, name: str) -> bool:
    """Check if FastAPI is running on a specific port."""
    try:
        response = requests.get("http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            print("[OK] {name} (port {port}): Running - Status: {status}")
            return True
        else:
            print("[WARN] {name} (port {port}): Responding but unhealthy (HTTP {response.status_code})")
            return False
    except requests.ConnectionError:
        print("[FAIL] {name} (port {port}): Not running")
        return False
    except requests.Timeout:
        print("[WARN] {name} (port {port}): Timeout")
        return False
    except Exception as e:
        print("[FAIL] {name} (port {port}): Error - {e}")
        return False


def main():
    print("=" * 50)
    print("FastAPI Instance Quick Check")
    print("=" * 50)

    docker_running = check_port(8000, "Docker")
    debug_running = check_port(8001, "Debug")

    print("-" * 50)

    if docker_running and debug_running:
        print("[OK] Both instances running! You can:")
        print("   - Test Docker version at http://localhost:8000")
        print("   - Test Debug version at http://localhost:8001")
        print("   - Compare behavior between versions")
        return 0
    elif docker_running:
        print("[INFO] Only Docker instance running")
        print("   - Docker API: http://localhost:8000/docs")
        print("   - To start debug: Open VSCode and press F5")
        return 0
    elif debug_running:
        print("[INFO] Only Debug instance running")
        print("   - Debug API: http://localhost:8001/docs")
        print("   - To start Docker: docker-compose up -d")
        return 0
    else:
        print("[WARN] No instances running!")
        print("   - Start Docker: docker-compose up -d")
        print("   - Start Debug: VSCode -> F5")
        return 1


if __name__ == "__main__":
    sys.exit(main())
