#!/usr/bin/env python
"""
Test utility to check FastAPI on both ports:
- Port 8000: Docker version
- Port 8001: Local debug version
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any
from datetime import datetime

# Configuration
DOCKER_PORT = 8000
DEBUG_PORT = 8001
TEST_TIMEOUT = 30  # seconds


async def test_health_endpoint(session: aiohttp.ClientSession, port: int) -> Dict[str, Any]:
    """Test the /health endpoint on a specific port."""
    url = f"http://localhost:{port}/health"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "status": "accessible",
                    "response_code": response.status,
                    "data": data
                }
            else:
                return {
                    "status": "error",
                    "response_code": response.status,
                    "error": f"HTTP {response.status}"
                }
    except aiohttp.ClientError as e:
        return {
            "status": "unreachable",
            "error": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def test_docs_endpoint(session: aiohttp.ClientSession, port: int) -> Dict[str, Any]:
    """Test the /docs endpoint on a specific port."""
    url = f"http://localhost:{port}/docs"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            if response.status == 200:
                return {
                    "status": "accessible",
                    "response_code": response.status,
                    "content_type": response.headers.get('content-type', 'unknown')
                }
            else:
                return {
                    "status": "error",
                    "response_code": response.status
                }
    except aiohttp.ClientError as e:
        return {
            "status": "unreachable",
            "error": str(e)
        }


async def test_ai_endpoint(session: aiohttp.ClientSession, port: int) -> Dict[str, Any]:
    """Test the /ai/test endpoint with a simple request."""
    url = f"http://localhost:{port}/ai/test"
    payload = {
        "system_prompt": "You are a helpful assistant.",
        "user_context": "Say hello"
    }

    try:
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "status": "working",
                    "response_code": response.status,
                    "response_length": len(data.get("ai_result", "")),
                    "has_embedding": "embedding" in data,
                    "response_time_ms": data.get("response_time_ms", 0)
                }
            else:
                text = await response.text()
                return {
                    "status": "error",
                    "response_code": response.status,
                    "error": text[:200]
                }
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "error": f"Request timed out after {TEST_TIMEOUT} seconds"
        }
    except aiohttp.ClientError as e:
        return {
            "status": "unreachable",
            "error": str(e)
        }


async def test_port(port: int, name: str) -> Dict[str, Any]:
    """Run all tests for a specific port."""
    print("\n[SEARCH] Testing {name} on port {port}...")
    print("-" * 50)

    results = {
        "port": port,
        "name": name,
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }

    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("  Testing /health endpoint...")
        health_result = await test_health_endpoint(session, port)
        results["tests"]["health"] = health_result

        if health_result["status"] == "accessible":
            print("  [OK] Health check: {health_result['data'].get('status', 'unknown')}")

            # Show service statuses if available
            if "data" in health_result and "containers" in health_result["data"]:
                containers = health_result["data"]["containers"]
                for service, info in containers.items():
                    status_icon = "[OK]" if info.get("status") == "healthy" else "[WARN]"
                    print("     {status_icon} {service}: {info.get('status', 'unknown')}")
        else:
            print("  [X] Health check failed: {health_result.get('error', 'Unknown error')}")

        # Test docs endpoint
        print("  Testing /docs endpoint...")
        docs_result = await test_docs_endpoint(session, port)
        results["tests"]["docs"] = docs_result

        if docs_result["status"] == "accessible":
            print("  [OK] API Docs accessible")
        else:
            print("  [X] API Docs: {docs_result.get('error', 'Not accessible')}")

        # Test AI endpoint (only if health check passed)
        if health_result["status"] == "accessible":
            print("  Testing /ai/test endpoint (may take up to {TEST_TIMEOUT}s)...")
            ai_result = await test_ai_endpoint(session, port)
            results["tests"]["ai"] = ai_result

            if ai_result["status"] == "working":
                print("  [OK] AI endpoint working")
                print("     Response time: {ai_result.get('response_time_ms', 0)}ms")
                print("     Response length: {ai_result.get('response_length', 0)} chars")
                print("     Has embedding: {ai_result.get('has_embedding', False)}")
            else:
                print("  [WARN] AI endpoint: {ai_result.get('error', 'Not working')}")

    return results


async def main():
    """Main test function."""
    print("=" * 60)
    print("[ROCKET] FASTAPI DUAL PORT TESTING")
    print("=" * 60)
    print("Testing both Docker (:{DOCKER_PORT}) and Debug (:{DEBUG_PORT}) instances")

    # Test both ports
    docker_results = await test_port(DOCKER_PORT, "Docker Instance")
    debug_results = await test_port(DEBUG_PORT, "Local Debug Instance")

    # Summary
    print("\n" + "=" * 60)
    print("[CHART] SUMMARY")
    print("=" * 60)

    # Docker summary
    docker_health = docker_results["tests"].get("health", {})
    if docker_health.get("status") == "accessible":
        print("[OK] Docker ({DOCKER_PORT}): Running")
        if docker_health.get("data", {}).get("status") == "healthy":
            print("   All services healthy")
        else:
            print("   Status: {docker_health.get('data', {}).get('status', 'unknown')}")
    else:
        print("[X] Docker ({DOCKER_PORT}): Not running or unreachable")

    # Debug summary
    debug_health = debug_results["tests"].get("health", {})
    if debug_health.get("status") == "accessible":
        print("[OK] Debug ({DEBUG_PORT}): Running")
        if debug_health.get("data", {}).get("status") == "healthy":
            print("   All services healthy")
        else:
            print("   Status: {debug_health.get('data', {}).get('status', 'unknown')}")
    else:
        print("[X] Debug ({DEBUG_PORT}): Not running or unreachable")

    # Comparison
    print("\n[GRAPH] COMPARISON:")
    both_running = (
        docker_health.get("status") == "accessible"
        and debug_health.get("status") == "accessible"
    )

    if both_running:
        print("[OK] Both instances are running - perfect for A/B testing!")
        print("   - Use Docker (8000) for production-like testing")
        print("   - Use Debug (8001) for development with breakpoints")
    elif docker_health.get("status") == "accessible":
        print("[UNICODE] Only Docker instance is running")
        print("   - Start debug instance with VSCode (F5) to debug")
    elif debug_health.get("status") == "accessible":
        print("[UNICODE] Only Debug instance is running")
        print("   - Run 'docker-compose up -d' to start Docker instance")
    else:
        print("[WARN] No instances are running!")
        print("   - Run 'docker-compose up -d' for Docker instance")
        print("   - Press F5 in VSCode for Debug instance")

    # Save results to file
    results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            "docker": docker_results,
            "debug": debug_results
        }, f, indent=2)
    print("\n[FLOPPY] Detailed results saved to: {results_file}")

if __name__ == "__main__":
    asyncio.run(main())
