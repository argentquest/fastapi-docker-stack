#!/usr/bin/env python3
"""
Startup script to run both the Nginx dashboard (via Docker) and the stats API server.
This provides a complete monitoring solution for the V2 POC.
"""

import subprocess
import time
import threading
import sys
import os
from pathlib import Path


def run_stats_api():
    """Run the stats API server in a separate thread."""
    print("🚀 Starting Docker stats API server on port 8083...")
    try:
        # Change to the dashboard directory
        dashboard_dir = Path(__file__).parent / 'dashboard'
        os.chdir(dashboard_dir)
        
        # Run the stats API
        subprocess.run([sys.executable, 'api.py'], check=True)
    except KeyboardInterrupt:
        print("📊 Stats API server stopped.")
    except Exception as e:
        print(f"❌ Error running stats API: {e}")


def check_dashboard_status():
    """Check if the main dashboard is accessible."""
    import requests
    
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get('http://localhost:8082', timeout=2)
            if response.status_code == 200:
                print("✅ Dashboard is accessible at http://localhost:8082")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if i < max_retries - 1:
            print(f"⏳ Waiting for dashboard to be ready... ({i+1}/{max_retries})")
            time.sleep(2)
    
    print("⚠️ Dashboard may not be ready yet. Check Docker containers with: docker-compose ps")
    return False


def main():
    """Main function to coordinate dashboard and stats API startup."""
    print("=" * 60)
    print("🎛️ V2 POC DASHBOARD + STATS LAUNCHER")
    print("=" * 60)
    
    # Check if Docker containers are running
    try:
        result = subprocess.run(['docker-compose', 'ps', '--services', '--filter', 'status=running'], 
                              capture_output=True, text=True, timeout=10)
        running_services = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        if not running_services or not any(running_services):
            print("⚠️ No Docker containers appear to be running.")
            print("💡 Start the V2 POC stack first with: docker-compose up -d")
            print("   Then run this script again.")
            return
        
        print(f"✅ Found {len(running_services)} running Docker services")
        
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"❌ Error checking Docker status: {e}")
        print("💡 Make sure Docker is running and you're in the project directory")
        return
    
    # Check main dashboard availability
    print("\n📋 Checking main dashboard status...")
    dashboard_ready = check_dashboard_status()
    
    # Start stats API in background thread
    print("\n📊 Starting stats API server...")
    stats_thread = threading.Thread(target=run_stats_api, daemon=True)
    stats_thread.start()
    
    # Give the API a moment to start
    time.sleep(2)
    
    # Check if stats API is running
    try:
        import requests
        response = requests.get('http://localhost:8083/api/container-stats', timeout=3)
        if response.status_code == 200:
            print("✅ Stats API is running at http://localhost:8083")
        else:
            print("⚠️ Stats API started but returned unexpected response")
    except requests.exceptions.RequestException:
        print("⚠️ Stats API may still be starting up")
    
    print("\n" + "=" * 60)
    print("🎉 V2 POC MONITORING DASHBOARD READY")
    print("=" * 60)
    print("📋 Main Dashboard:    http://localhost:8082")
    print("📊 System Status:     http://localhost:8082/status.html")
    print("🔧 Stats API:         http://localhost:8083/api/container-stats")
    print("\n🔍 Available Features:")
    print("   • Service overview with all URLs and credentials")
    print("   • Real-time Docker container statistics")
    print("   • CPU, memory, and network usage monitoring") 
    print("   • Auto-refreshing status display")
    print("   • Direct links to all management interfaces")
    print("\n💡 Pro Tips:")
    print("   • The system status page auto-updates every 30 seconds")
    print("   • Click 'Refresh' button to update stats immediately")
    print("   • Stats API provides JSON data for external monitoring tools")
    print("\n⏹️ Press Ctrl+C to stop the stats API server...")
    print("=" * 60)
    
    try:
        # Keep the main thread alive to handle Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down dashboard monitoring...")
        print("📋 Main dashboard (Docker) will continue running")
        print("📊 Stats API server stopped")
        print("✅ Goodbye!")


if __name__ == '__main__':
    main()