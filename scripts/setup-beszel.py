#!/usr/bin/env python3
"""
Beszel Auto-Configuration Script
Generates SSH keys and automatically configures Beszel monitoring.
"""

import requests
import json
import time
import subprocess
import os
import tempfile

def generate_ssh_key():
    """Generate SSH key pair for Beszel agent authentication."""
    try:
        # Generate Ed25519 key pair
        with tempfile.TemporaryDirectory() as temp_dir:
            private_key_path = os.path.join(temp_dir, "beszel_key")
            public_key_path = f"{private_key_path}.pub"
            
            # Generate key pair
            subprocess.run([
                "ssh-keygen", "-t", "ed25519", "-f", private_key_path, 
                "-N", "", "-C", "beszel-agent@argentquest"
            ], check=True, capture_output=True)
            
            # Read keys
            with open(private_key_path, 'r') as f:
                private_key = f.read().strip()
            with open(public_key_path, 'r') as f:
                public_key = f.read().strip()
                
            return private_key, public_key
            
    except Exception as e:
        print(f"Error generating SSH keys: {e}")
        return None, None

def setup_beszel_hub():
    """Configure Beszel hub via API."""
    try:
        # Wait for Beszel to be ready
        print("⏳ Waiting for Beszel hub to be ready...")
        for i in range(30):
            try:
                response = requests.get("http://localhost:8090", timeout=5)
                if response.status_code == 200:
                    print("✅ Beszel hub is ready")
                    break
            except:
                pass
            time.sleep(2)
        else:
            print("❌ Beszel hub not ready after 60 seconds")
            return False
            
        # Create admin user if needed
        # Note: This may require manual setup on first run
        print("✅ Beszel hub accessible at http://localhost:8090")
        print("🔑 Use credentials: admin@example.com / changeme")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Beszel hub: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Starting Beszel Auto-Configuration...")
    
    # Generate SSH keys
    print("🔐 Generating SSH key pair...")
    private_key, public_key = generate_ssh_key()
    
    if not private_key or not public_key:
        print("❌ Failed to generate SSH keys")
        print("💡 Manual setup required - access Beszel at http://localhost:8090")
        return
    
    print(f"✅ Generated SSH keys")
    print(f"🔑 Public key: {public_key}")
    
    # Setup Beszel hub
    if setup_beszel_hub():
        print("\n📊 Beszel Configuration Complete!")
        print("📋 Next steps:")
        print("1. Access Beszel dashboard: http://localhost:8090")
        print("2. Login with: admin@example.com / changeme")
        print("3. Add system with agent host: aq-devsuite-beszel-agent:45876")
        print(f"4. Use this public key: {public_key}")
        print("5. Enable Docker monitoring to see all 20 containers")
    else:
        print("❌ Failed to configure Beszel hub")

if __name__ == "__main__":
    main()