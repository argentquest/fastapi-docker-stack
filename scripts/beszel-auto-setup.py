#!/usr/bin/env python3
"""
Beszel Automatic Configuration Script
Generates SSH keys and provides configuration instructions.
"""

import requests
import json
import time
import subprocess
import os
import sys

def wait_for_beszel():
    """Wait for Beszel hub to be ready."""
    print("⏳ Waiting for Beszel hub to be ready...")
    for i in range(60):
        try:
            response = requests.get("http://aq-devsuite-beszel:8090", timeout=5)
            if response.status_code == 200:
                print("✅ Beszel hub is ready")
                return True
        except:
            pass
        time.sleep(3)
    
    print("❌ Beszel hub not ready after 180 seconds")
    return False

def generate_ssh_key():
    """Generate SSH key pair."""
    try:
        key_dir = "/keys"
        os.makedirs(key_dir, exist_ok=True)
        key_path = f"{key_dir}/beszel_key"
        
        # Generate Ed25519 key pair
        result = subprocess.run([
            "ssh-keygen", "-t", "ed25519", "-f", key_path,
            "-N", "", "-C", "beszel-agent@argentquest"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ ssh-keygen failed: {result.stderr}")
            return None, None
        
        # Read keys
        with open(key_path, 'r') as f:
            private_key = f.read().strip()
        with open(f"{key_path}.pub", 'r') as f:
            public_key = f.read().strip()
        
        # Save public key for docker-compose update
        with open("/keys/public_key.txt", 'w') as f:
            f.write(public_key)
            
        print("✅ SSH key pair generated and saved")
        return private_key, public_key
        
    except Exception as e:
        print(f"❌ Error generating SSH keys: {e}")
        return None, None

def main():
    """Main setup function."""
    print("🚀 Beszel Automatic Configuration...")
    
    # Wait for Beszel to be ready
    if not wait_for_beszel():
        print("❌ Cannot connect to Beszel hub")
        print("💡 Check if Beszel container is running")
        return
    
    # Generate SSH key pair
    private_key, public_key = generate_ssh_key()
    
    if not private_key or not public_key:
        print("❌ Failed to generate SSH keys")
        return
    
    # Output configuration
    print("\n" + "="*60)
    print("🔑 BESZEL AUTO-CONFIGURATION COMPLETE")
    print("="*60)
    print("\n📋 NEXT STEPS:")
    print("1. Run this command to update the agent key:")
    print(f"   export BESZEL_KEY='{public_key}'")
    print("   docker-compose restart beszel-agent")
    print("\n2. Access Beszel dashboard:")
    print("   http://localhost:8090")
    print("   http://beszel.pocmaster.argentquest.com")
    print("\n3. Login with:")
    print("   Email: admin@example.com")
    print("   Password: changeme")
    print("\n4. Add system:")
    print("   Name: Argentquest Development Suite")
    print("   Host: aq-devsuite-beszel-agent")
    print("   Port: 45876")
    print(f"   Public Key: {public_key}")
    print("   ✅ Enable Docker Monitoring")
    print("\n🎉 Beszel will then automatically discover all 20 containers!")
    print("="*60)

if __name__ == "__main__":
    main()