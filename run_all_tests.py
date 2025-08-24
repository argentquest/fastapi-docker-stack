#!/usr/bin/env python3
"""
V2 POC Master Test Runner

This script automates the execution of all integration and unit tests for the V2 POC.
It runs each test script in a predefined sequence, captures the results, and provides
a comprehensive summary report.

The script is designed to be the single source of truth for validating the entire
application stack, and it returns a specific exit code based on the results to
support CI/CD pipelines.
"""

import sys
import subprocess
import time
from pathlib import Path

def main() -> int:
    """Main function to execute all test suites."""
    print("🚀 V2 POC COMPREHENSIVE TEST SUITE 🚀")
    print("=" * 60)
    
    # Define the test scripts to be executed in a specific order.
    # This order ensures that foundational tests (like container health) run first.
    test_scripts = [
        ("01", "Container Health Check", "test_01_containers_health.py"),
        ("02", "Database & pgvector", "test_02_database_pgvector.py"),
        ("03", "OpenRouter Integration", "test_03_openrouter_integration.py"),
        ("04", "MinIO Storage Operations", "test_04_minio_storage.py"),
        ("05", "Redis Cache Operations", "test_05_redis_cache.py"),
        ("06", "End-to-End Workflow", "test_06_end_to_end.py")
    ]
    
    test_results = []
    overall_start_time = time.time()
    
    print(f"\n🔍 Found {len(test_scripts)} test suites to run...\n")
    
    # --- Test Execution Loop ---
    for test_num, test_name, script_name in test_scripts:
        print(f"▶️  RUNNING TEST {test_num}: {test_name}")
        print("-" * 40)
        
        script_path = Path(__file__).parent / "tests" / script_name
        
        if not script_path.exists():
            print(f"❌ FAILED: Test script not found at {script_path}")
            test_results.append({
                'name': test_name, 'status': 'MISSING', 'duration': 0,
                'error': f"Script not found: {script_name}"
            })
            continue
        
        start_time = time.time()
        try:
            # Execute each test script as a separate process.
            # This isolates the tests and captures their stdout/stderr.
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True, text=True, timeout=120, check=False
            )
            duration = time.time() - start_time
            
            # Assess the outcome based on the return code.
            if result.returncode == 0:
                status = "PASSED"
                error = None
                print(f"✅ PASSED in {duration:.2f}s")
            else:
                status = "FAILED"
                error = result.stderr.strip() or result.stdout.strip()
                print(f"❌ FAILED in {duration:.2f}s")
                print(f"   ERROR: {error[:200]}..." if len(error) > 200 else f"   ERROR: {error}")
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            status = "TIMEOUT"
            error = "Test exceeded the 120-second timeout."
            print(f"⏱️  TIMEOUT after {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            status = "ERROR"
            error = f"An unexpected error occurred: {e}"
            print(f"💥 ERROR: {e}")
        
        test_results.append({
            'name': test_name, 'status': status, 
            'duration': duration, 'error': error
        })
        print()
    
    # --- Results Summary ---
    overall_duration = time.time() - overall_start_time
    passed_count = sum(1 for t in test_results if t['status'] == 'PASSED')
    failed_count = len(test_results) - passed_count
    
    print("\n" + "=" * 60)
    print("📊 TEST SUITE SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {len(test_results)} | ✅ Passed: {passed_count} | ❌ Failed: {failed_count}")
    print(f"⏱️  Total Duration: {overall_duration:.2f}s")
    print("-" * 60)
    
    for test in test_results:
        status_emoji = {'PASSED': '✅', 'FAILED': '❌', 'TIMEOUT': '⏱️', 'ERROR': '💥', 'MISSING': '❓'}
        print(f"{status_emoji.get(test['status'])} {test['name']:<30} [{test['status']:<7}] ({test['duration']:.2f}s)")
        if test['error']:
            # Indent the error message for readability.
            error_line = test['error'].replace('\n', ' ').strip()
            print(f"    └─ Error: {error_line[:100]}{'...' if len(error_line) > 100 else ''}")
    
    # --- Final Assessment & Exit Code ---
    print("\n" + "=" * 60)
    if failed_count == 0:
        print("🎉 ALL TESTS PASSED! The V2 stack is healthy and integrated correctly.")
        return_code = 0
    else:
        print("❌ SOME TESTS FAILED. Please review the errors above.")
        print("\n📝 NEXT STEPS:")
        print("1. Check container logs: `docker-compose logs <service_name>`")
        print("2. Verify your `.env` file has the correct credentials.")
        print("3. Re-run failed tests individually for more detailed output.")
        return_code = 1
    print("=" * 60)
    
    return return_code

if __name__ == '__main__':
    # Exit with a status code indicating success (0) or failure (non-zero).
    sys.exit(main())
