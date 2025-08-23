#!/usr/bin/env python3
"""
V2 POC Test Runner
Executes all test scripts in sequence and provides comprehensive results
"""

import sys
import subprocess
import time
from pathlib import Path

def main():
    """Run all POC tests in sequence"""
    print("🚀 V2 POC COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("Testing all 5 containers: FastAPI, PostgreSQL+pgvector, Redis, MinIO, Nginx")
    print("=" * 60)
    
    # Test scripts to run in order
    test_scripts = [
        ("01", "Container Health", "test_01_containers_health.py"),
        ("02", "PostgreSQL + pgvector", "test_02_database_pgvector.py"),
        ("03", "OpenRouter Integration", "test_03_openrouter_integration.py"),
        ("04", "MinIO Storage", "test_04_minio_storage.py"),
        ("05", "Redis Cache", "test_05_redis_cache.py"),
        ("06", "End-to-End Integration", "test_06_end_to_end.py")
    ]
    
    test_results = []
    overall_start_time = time.time()
    
    print(f"\n🔍 Running {len(test_scripts)} test suites...\n")
    
    for test_num, test_name, script_name in test_scripts:
        print(f"▶️  TEST {test_num}: {test_name}")
        print("-" * 40)
        
        script_path = Path(__file__).parent / "tests" / script_name
        
        if not script_path.exists():
            print(f"❌ FAILED: Test script not found: {script_name}")
            test_results.append({
                'test_num': test_num,
                'name': test_name,
                'status': 'MISSING',
                'duration': 0,
                'error': f"Script not found: {script_name}"
            })
            continue
        
        # Run the test script
        start_time = time.time()
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=script_path.parent.parent,  # Run from V2 directory
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout per test
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                status = "PASSED"
                error = None
                print(f"✅ PASSED ({duration:.1f}s)")
            else:
                status = "FAILED"
                error = result.stderr or "Unknown error"
                print(f"❌ FAILED ({duration:.1f}s)")
                if result.stdout:
                    print("STDOUT:")
                    print(result.stdout[-500:])  # Show last 500 chars
                if result.stderr:
                    print("STDERR:")
                    print(result.stderr[-500:])
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            status = "TIMEOUT"
            error = "Test timed out after 120 seconds"
            print(f"⏱️  TIMEOUT ({duration:.1f}s)")
            
        except Exception as e:
            duration = time.time() - start_time
            status = "ERROR"
            error = str(e)
            print(f"💥 ERROR ({duration:.1f}s): {e}")
        
        test_results.append({
            'test_num': test_num,
            'name': test_name,
            'status': status,
            'duration': duration,
            'error': error
        })
        
        print()  # Add spacing between tests
    
    # Print comprehensive results
    overall_duration = time.time() - overall_start_time
    
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    passed_tests = [t for t in test_results if t['status'] == 'PASSED']
    failed_tests = [t for t in test_results if t['status'] not in ['PASSED']]
    
    print(f"🎯 Total Tests: {len(test_results)}")
    print(f"✅ Passed: {len(passed_tests)}")
    print(f"❌ Failed: {len(failed_tests)}")
    print(f"⏱️  Total Duration: {overall_duration:.1f}s")
    
    print("\n📋 Individual Test Results:")
    print("-" * 60)
    
    for test in test_results:
        status_emoji = {
            'PASSED': '✅',
            'FAILED': '❌', 
            'TIMEOUT': '⏱️',
            'ERROR': '💥',
            'MISSING': '❓'
        }.get(test['status'], '❓')
        
        print(f"{status_emoji} TEST {test['test_num']}: {test['name']:<25} "
              f"[{test['status']:<7}] ({test['duration']:.1f}s)")
        
        if test['error']:
            print(f"    └─ Error: {test['error'][:80]}{'...' if len(test['error']) > 80 else ''}")
    
    # Final assessment
    print("\n" + "=" * 60)
    
    if len(passed_tests) == len(test_results):
        print("🎉 ALL TESTS PASSED! V2 POC IS READY FOR DEPLOYMENT!")
        print("✨ All 5 containers are working together perfectly:")
        print("   • FastAPI application server")
        print("   • PostgreSQL with pgvector extension")
        print("   • OpenRouter AI integration")
        print("   • MinIO S3-compatible storage")
        print("   • Redis caching layer")
        print("   • Nginx reverse proxy")
        return_code = 0
        
    elif len(passed_tests) >= 4:  # Allow some flexibility
        print("⚠️  MOSTLY SUCCESSFUL - Minor issues detected")
        print(f"   {len(passed_tests)}/{len(test_results)} tests passed")
        print("   Review failed tests and consider if they're critical")
        return_code = 1
        
    else:
        print("❌ CRITICAL ISSUES DETECTED")
        print(f"   Only {len(passed_tests)}/{len(test_results)} tests passed")
        print("   🚨 DO NOT DEPLOY - Fix failing tests first")
        return_code = 2
    
    print("=" * 60)
    
    # Provide next steps
    if failed_tests:
        print("\n📝 NEXT STEPS:")
        print("1. Check that all containers are running: docker-compose ps")
        print("2. Check container logs: docker-compose logs [service-name]")
        print("3. Verify environment variables in .env file")
        print("4. Re-run individual failed tests:")
        
        for test in failed_tests:
            script_name = None
            for _, _, script in test_scripts:
                if test['test_num'] in script:
                    script_name = script
                    break
            if script_name:
                print(f"   python tests/{script_name}")
    else:
        print("\n🚀 READY FOR NEXT PHASE:")
        print("1. Deploy to development VPS")
        print("2. Run production-like tests")
        print("3. Begin gradual migration from Azure")
    
    return return_code

if __name__ == '__main__':
    sys.exit(main())